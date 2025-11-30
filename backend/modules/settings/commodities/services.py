"""
Commodity Services

Business logic layer with event sourcing for commodity management.
"""

from __future__ import annotations

import json
from typing import List, Optional
from uuid import UUID

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.events.emitter import EventEmitter
from backend.core.outbox import OutboxRepository
from backend.modules.settings.commodities.ai_helpers import CommodityAIHelper
from backend.modules.settings.commodities.events import (
    CommodityCreated,
    CommodityDeleted,
    CommodityParameterAdded,
    CommodityParameterUpdated,
    CommodityUpdated,
    CommodityVarietyAdded,
    CommodityVarietyUpdated,
    CommissionStructureSet,
    TradeTermsCreated,
    TradeTermsUpdated,
)
from backend.modules.settings.commodities.models import (
    BargainType,
    Commodity,
    CommodityParameter,
    CommodityVariety,
    CommissionStructure,
    DeliveryTerm,
    PassingTerm,
    PaymentTerm,
    SystemCommodityParameter,
    TradeType,
    WeightmentTerm,
)
from backend.modules.settings.commodities.repositories import (
    BargainTypeRepository,
    CommodityParameterRepository,
    CommodityRepository,
    CommodityVarietyRepository,
    CommissionStructureRepository,
    DeliveryTermRepository,
    PassingTermRepository,
    PaymentTermRepository,
    SystemCommodityParameterRepository,
    TradeTypeRepository,
    WeightmentTermRepository,
)
from backend.modules.settings.commodities.schemas import (
    BargainTypeCreate,
    BargainTypeUpdate,
    CommodityCreate,
    CommodityParameterCreate,
    CommodityParameterUpdate,
    CommodityUpdate,
    CommodityVarietyCreate,
    CommodityVarietyUpdate,
    CommissionStructureCreate,
    CommissionStructureUpdate,
    DeliveryTermCreate,
    DeliveryTermUpdate,
    PassingTermCreate,
    PassingTermUpdate,
    PaymentTermCreate,
    PaymentTermUpdate,
    SystemCommodityParameterCreate,
    SystemCommodityParameterUpdate,
    TradeTypeCreate,
    TradeTypeUpdate,
    WeightmentTermCreate,
    WeightmentTermUpdate,
)


class CommodityService:
    """Service for commodity operations with event sourcing"""
    
    def __init__(
        self,
        session: AsyncSession,
        event_emitter: EventEmitter,
        ai_helper: CommodityAIHelper,
        current_user_id: UUID,
        redis_client: Optional[redis.Redis] = None
    ):
        self.repository = CommodityRepository(session)
        self.event_emitter = event_emitter
        self.ai_helper = ai_helper
        self.current_user_id = current_user_id
        self.redis = redis_client
        self.db = session
        self.outbox_repo = OutboxRepository(session)
    
    async def create_commodity(self, data: CommodityCreate) -> Commodity:
        """Create new commodity with AI enrichment and event emission"""
        
        # AI enrichment if needed
        if not data.hsn_code or not data.gst_rate:
            enrichment = await self.ai_helper.enrich_commodity_data(
                name=data.name,
                category=data.category,
                description=data.description
            )
            
            if not data.hsn_code:
                data.hsn_code = enrichment["suggested_hsn_code"]
            if not data.gst_rate:
                data.gst_rate = enrichment["suggested_gst_rate"]
        
        # Create commodity
        commodity = await self.repository.create(**data.model_dump())
        
        # NEW: Learn from this commodity creation (AI self-improvement)
        if self.ai_helper.hsn_learning and data.hsn_code:
            await self.ai_helper.hsn_learning.confirm_hsn_mapping(
                commodity_name=data.name,
                category=data.category,
                hsn_code=data.hsn_code,
                gst_rate=data.gst_rate,
                user_id=self.current_user_id
            )
        
        # Emit event
        await self.event_emitter.emit(
            CommodityCreated(
                aggregate_id=commodity.id,
                user_id=self.current_user_id,
                data={
                    "name": commodity.name,
                    "category": commodity.category,
                    "hsn_code": commodity.hsn_code,
                    "gst_rate": str(commodity.gst_rate) if commodity.gst_rate else None
                }
            )
        )
        
        return commodity
    
    async def update_commodity(
        self,
        commodity_id: UUID,
        data: CommodityUpdate
    ) -> Optional[Commodity]:
        """Update commodity and emit event"""
        
        # Get existing
        existing = await self.repository.get_by_id(commodity_id)
        if not existing:
            return None
        
        # Update
        commodity = await self.repository.update(commodity_id, **data.model_dump(exclude_unset=True))
        if not commodity:
            return None
        
        # Emit event
        changes = {}
        for field in ["name", "category", "hsn_code", "gst_rate", "is_active"]:
            old_value = getattr(existing, field)
            new_value = getattr(commodity, field)
            if old_value != new_value:
                changes[field] = {
                    "old": str(old_value) if old_value is not None else None,
                    "new": str(new_value) if new_value is not None else None
                }
        
        await self.event_emitter.emit(
            CommodityUpdated(
                aggregate_id=commodity.id,
                user_id=self.current_user_id,
                data={"changes": changes}
            )
        )
        
        return commodity
    
    async def delete_commodity(self, commodity_id: UUID) -> bool:
        """Delete commodity and emit event"""
        
        commodity = await self.repository.get_by_id(commodity_id)
        if not commodity:
            return False
        
        success = await self.repository.delete(commodity_id)
        
        if success:
            await self.event_emitter.emit(
                CommodityDeleted(
                    aggregate_id=commodity_id,
                    user_id=self.current_user_id,
                    data={"name": commodity.name}
                )
            )
        
        return success
    
    async def get_commodity(self, commodity_id: UUID) -> Optional[Commodity]:
        """Get commodity by ID"""
        return await self.repository.get_by_id(commodity_id)
    
    async def list_commodities(
        self,
        category: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> List[Commodity]:
        """List commodities with optional filters"""
        return await self.repository.list_all(category=category, is_active=is_active)


class CommodityVarietyService:
    """Service for commodity variety operations"""
    
    def __init__(
        self,
        session: AsyncSession,
        event_emitter: EventEmitter,
        current_user_id: UUID
    ):
        self.repository = CommodityVarietyRepository(session)
        self.event_emitter = event_emitter
        self.current_user_id = current_user_id
    
    async def add_variety(self, data: CommodityVarietyCreate) -> CommodityVariety:
        """Add variety to commodity"""
        
        variety = await self.repository.create(**data.model_dump())
        
        await self.event_emitter.emit(
            CommodityVarietyAdded(
                aggregate_id=variety.commodity_id,
                user_id=self.current_user_id,
                data={
                    "variety_id": str(variety.id),
                    "name": variety.name,
                    "code": variety.code
                }
            )
        )
        
        return variety
    
    async def update_variety(
        self,
        variety_id: UUID,
        data: CommodityVarietyUpdate
    ) -> Optional[CommodityVariety]:
        """Update variety"""
        
        variety = await self.repository.update(variety_id, **data.model_dump(exclude_unset=True))
        if not variety:
            return None
        
        await self.event_emitter.emit(
            CommodityVarietyUpdated(
                aggregate_id=variety.commodity_id,
                user_id=self.current_user_id,
                data={"variety_id": str(variety.id), "variety_name": variety.name}
            )
        )
        
        return variety
    
    async def list_varieties(
        self,
        commodity_id: Optional[UUID] = None
    ) -> List[CommodityVariety]:
        """List varieties"""
        return await self.repository.list_all(commodity_id=commodity_id)


class CommodityParameterService:
    """Service for commodity quality parameters with AI learning"""
    
    def __init__(
        self,
        session: AsyncSession,
        event_emitter: EventEmitter,
        current_user_id: UUID
    ):
        self.repository = CommodityParameterRepository(session)
        self.system_param_repository = SystemCommodityParameterRepository(session)
        self.commodity_repository = CommodityRepository(session)
        self.event_emitter = event_emitter
        self.current_user_id = current_user_id
        self.session = session
    
    async def add_parameter(
        self,
        data: CommodityParameterCreate
    ) -> CommodityParameter:
        """Add quality parameter to commodity with AI learning"""
        
        # Create the parameter for this commodity
        parameter = await self.repository.create(**data.model_dump())
        
        # AI LEARNING: Check if this parameter should become a template
        await self._learn_parameter_template(parameter)
        
        await self.event_emitter.emit(
            CommodityParameterAdded(
                aggregate_id=parameter.commodity_id,
                user_id=self.current_user_id,
                data={
                    "parameter_id": str(parameter.id),
                    "name": parameter.parameter_name,
                    "type": parameter.parameter_type
                }
            )
        )
        
        return parameter
    
    async def _learn_parameter_template(self, parameter: CommodityParameter) -> None:
        """
        AI Learning: Create/update SystemCommodityParameter template
        
        When user adds a custom parameter, system learns by:
        1. Getting the commodity's category
        2. Checking if template already exists for this category+parameter
        3. If not, creating a new template for future suggestions
        4. If yes, incrementing usage count to improve ranking
        """
        from sqlalchemy import select, func
        
        # Get commodity to determine category
        commodity = await self.commodity_repository.get_by_id(parameter.commodity_id)
        if not commodity:
            return
        
        # Check if this parameter template already exists for this category
        stmt = select(SystemCommodityParameter).where(
            SystemCommodityParameter.commodity_category == commodity.category,
            SystemCommodityParameter.parameter_name == parameter.parameter_name
        )
        result = await self.session.execute(stmt)
        existing_template = result.scalar_one_or_none()
        
        if existing_template:
            # Template exists - increment usage count (popularity tracking)
            existing_template.usage_count = (existing_template.usage_count or 0) + 1
            existing_template.updated_at = func.now()
        else:
            # New parameter discovered - create template for future suggestions
            new_template = SystemCommodityParameter(
                commodity_category=commodity.category,
                parameter_name=parameter.parameter_name,
                parameter_type=parameter.parameter_type,
                unit=parameter.unit,
                min_value=parameter.min_value,
                max_value=parameter.max_value,
                default_value=parameter.default_value,
                is_mandatory=parameter.is_mandatory,
                usage_count=1,
                created_by=self.current_user_id
            )
            self.session.add(new_template)
        
        await self.session.flush()
    
    async def update_parameter(
        self,
        parameter_id: UUID,
        data: CommodityParameterUpdate
    ) -> Optional[CommodityParameter]:
        """Update parameter"""
        
        parameter = await self.repository.update(parameter_id, **data.model_dump(exclude_unset=True))
        if not parameter:
            return None
        
        await self.event_emitter.emit(
            CommodityParameterUpdated(
                aggregate_id=parameter.commodity_id,
                user_id=self.current_user_id,
                data={"parameter_id": str(parameter.id), "parameter_name": parameter.parameter_name}
            )
        )
        
        return parameter
    
    async def list_parameters(
        self,
        commodity_id: Optional[UUID] = None
    ) -> List[CommodityParameter]:
        """List parameters"""
        return await self.repository.list_all(commodity_id=commodity_id)


class SystemCommodityParameterService:
    """Service for system-wide commodity parameters (AI training data)"""
    
    def __init__(self, session: AsyncSession):
        self.repository = SystemCommodityParameterRepository(session)
    
    async def create_parameter(
        self,
        data: SystemCommodityParameterCreate
    ) -> SystemCommodityParameter:
        """Create system parameter"""
        return await self.repository.create(**data.model_dump())
    
    async def update_parameter(
        self,
        parameter_id: UUID,
        data: SystemCommodityParameterUpdate
    ) -> Optional[SystemCommodityParameter]:
        """Update system parameter"""
        return await self.repository.update(parameter_id, **data.model_dump(exclude_unset=True))
    
    async def list_parameters(
        self,
        category: Optional[str] = None
    ) -> List[SystemCommodityParameter]:
        """List system parameters"""
        return await self.repository.list_all(category=category)


class TradeTypeService:
    """Service for trade type operations"""
    
    def __init__(
        self,
        session: AsyncSession,
        event_emitter: EventEmitter,
        current_user_id: UUID
    ):
        self.repository = TradeTypeRepository(session)
        self.event_emitter = event_emitter
        self.current_user_id = current_user_id
    
    async def create_trade_type(self, data: TradeTypeCreate) -> TradeType:
        """Create trade type"""
        
        trade_type = await self.repository.create(**data.model_dump())
        
        await self.event_emitter.emit(
            TradeTermsCreated(
                aggregate_id=trade_type.id,
                user_id=self.current_user_id,
                data={
                    "term_type": "Trade Type",
                    "name": trade_type.name
                }
            )
        )
        
        return trade_type
    
    async def update_trade_type(
        self,
        trade_type_id: UUID,
        data: TradeTypeUpdate
    ) -> Optional[TradeType]:
        """Update trade type"""
        
        trade_type = await self.repository.update(trade_type_id, **data.model_dump(exclude_unset=True))
        if not trade_type:
            return None
        
        await self.event_emitter.emit(
            TradeTermsUpdated(
                aggregate_id=trade_type.id,
                user_id=self.current_user_id,
                data={
                    "term_type": "Trade Type",
                    "name": trade_type.name
                }
            )
        )
        
        return trade_type
    
    async def list_trade_types(self) -> List[TradeType]:
        """List all trade types"""
        return await self.repository.list_all()


class BargainTypeService:
    """Service for bargain type operations"""
    
    def __init__(
        self,
        session: AsyncSession,
        event_emitter: EventEmitter,
        current_user_id: UUID
    ):
        self.repository = BargainTypeRepository(session)
        self.event_emitter = event_emitter
        self.current_user_id = current_user_id
    
    async def create_bargain_type(self, data: BargainTypeCreate) -> BargainType:
        """Create bargain type"""
        
        bargain_type = await self.repository.create(**data.model_dump())
        
        await self.event_emitter.emit(
            TradeTermsCreated(
                aggregate_id=bargain_type.id,
                user_id=self.current_user_id,
                data={
                    "term_type": "Bargain Type",
                    "name": bargain_type.name
                }
            )
        )
        
        return bargain_type
    
    async def update_bargain_type(
        self,
        bargain_type_id: UUID,
        data: BargainTypeUpdate
    ) -> Optional[BargainType]:
        """Update bargain type"""
        
        bargain_type = await self.repository.update(bargain_type_id, **data.model_dump(exclude_unset=True))
        if not bargain_type:
            return None
        
        await self.event_emitter.emit(
            TradeTermsUpdated(
                aggregate_id=bargain_type.id,
                user_id=self.current_user_id,
                data={
                    "term_type": "Bargain Type",
                    "name": bargain_type.name
                }
            )
        )
        
        return bargain_type
    
    async def list_bargain_types(self) -> List[BargainType]:
        """List all bargain types"""
        return await self.repository.list_all()


class PassingTermService:
    """Service for passing term operations"""
    
    def __init__(
        self,
        session: AsyncSession,
        event_emitter: EventEmitter,
        current_user_id: UUID
    ):
        self.repository = PassingTermRepository(session)
        self.event_emitter = event_emitter
        self.current_user_id = current_user_id
    
    async def create_passing_term(self, data: PassingTermCreate) -> PassingTerm:
        """Create passing term"""
        term = await self.repository.create(**data.model_dump())
        
        await self.event_emitter.emit(
            TradeTermsCreated(
                aggregate_id=term.id,
                user_id=self.current_user_id,
                data={"term_type": "Passing", "name": term.name}
            )
        )
        
        return term
    
    async def update_passing_term(
        self,
        term_id: UUID,
        data: PassingTermUpdate
    ) -> Optional[PassingTerm]:
        """Update passing term"""
        term = await self.repository.update(term_id, **data.model_dump(exclude_unset=True))
        if term:
            await self.event_emitter.emit(
                TradeTermsUpdated(
                    aggregate_id=term.id,
                    user_id=self.current_user_id,
                    data={"term_type": "Passing", "name": term.name}
                )
            )
        return term
    
    async def list_passing_terms(self) -> List[PassingTerm]:
        """List all passing terms"""
        return await self.repository.list_all()


class WeightmentTermService:
    """Service for weightment term operations"""
    
    def __init__(
        self,
        session: AsyncSession,
        event_emitter: EventEmitter,
        current_user_id: UUID
    ):
        self.repository = WeightmentTermRepository(session)
        self.event_emitter = event_emitter
        self.current_user_id = current_user_id
    
    async def create_weightment_term(
        self,
        data: WeightmentTermCreate
    ) -> WeightmentTerm:
        """Create weightment term"""
        term = await self.repository.create(**data.model_dump())
        
        await self.event_emitter.emit(
            TradeTermsCreated(
                aggregate_id=term.id,
                user_id=self.current_user_id,
                data={"term_type": "Weightment", "name": term.name}
            )
        )
        
        return term
    
    async def update_weightment_term(
        self,
        term_id: UUID,
        data: WeightmentTermUpdate
    ) -> Optional[WeightmentTerm]:
        """Update weightment term"""
        term = await self.repository.update(term_id, **data.model_dump(exclude_unset=True))
        if term:
            await self.event_emitter.emit(
                TradeTermsUpdated(
                    aggregate_id=term.id,
                    user_id=self.current_user_id,
                    data={"term_type": "Weightment", "name": term.name}
                )
            )
        return term
    
    async def list_weightment_terms(self) -> List[WeightmentTerm]:
        """List all weightment terms"""
        return await self.repository.list_all()


class DeliveryTermService:
    """Service for delivery term operations"""
    
    def __init__(
        self,
        session: AsyncSession,
        event_emitter: EventEmitter,
        current_user_id: UUID
    ):
        self.repository = DeliveryTermRepository(session)
        self.event_emitter = event_emitter
        self.current_user_id = current_user_id
    
    async def create_delivery_term(self, data: DeliveryTermCreate) -> DeliveryTerm:
        """Create delivery term"""
        term = await self.repository.create(**data.model_dump())
        
        await self.event_emitter.emit(
            TradeTermsCreated(
                aggregate_id=term.id,
                user_id=self.current_user_id,
                data={"term_type": "Delivery", "name": term.name}
            )
        )
        
        return term
    
    async def update_delivery_term(
        self,
        term_id: UUID,
        data: DeliveryTermUpdate
    ) -> Optional[DeliveryTerm]:
        """Update delivery term"""
        term = await self.repository.update(term_id, **data.model_dump(exclude_unset=True))
        if term:
            await self.event_emitter.emit(
                TradeTermsUpdated(
                    aggregate_id=term.id,
                    user_id=self.current_user_id,
                    data={"term_type": "Delivery", "name": term.name}
                )
            )
        return term
    
    async def list_delivery_terms(self) -> List[DeliveryTerm]:
        """List all delivery terms"""
        return await self.repository.list_all()


class PaymentTermService:
    """Service for payment term operations"""
    
    def __init__(
        self,
        session: AsyncSession,
        event_emitter: EventEmitter,
        current_user_id: UUID
    ):
        self.repository = PaymentTermRepository(session)
        self.event_emitter = event_emitter
        self.current_user_id = current_user_id
    
    async def create_payment_term(self, data: PaymentTermCreate) -> PaymentTerm:
        """Create payment term"""
        term = await self.repository.create(**data.model_dump())
        
        await self.event_emitter.emit(
            TradeTermsCreated(
                aggregate_id=term.id,
                user_id=self.current_user_id,
                data={"term_type": "Payment", "name": term.name}
            )
        )
        
        return term
    
    async def update_payment_term(
        self,
        term_id: UUID,
        data: PaymentTermUpdate
    ) -> Optional[PaymentTerm]:
        """Update payment term"""
        term = await self.repository.update(term_id, **data.model_dump(exclude_unset=True))
        if term:
            await self.event_emitter.emit(
                TradeTermsUpdated(
                    aggregate_id=term.id,
                    user_id=self.current_user_id,
                    data={"term_type": "Payment", "name": term.name}
                )
            )
        return term
    
    async def list_payment_terms(self) -> List[PaymentTerm]:
        """List all payment terms"""
        return await self.repository.list_all()


class CommissionStructureService:
    """Service for commission structure operations"""
    
    def __init__(
        self,
        session: AsyncSession,
        event_emitter: EventEmitter,
        current_user_id: UUID
    ):
        self.repository = CommissionStructureRepository(session)
        self.event_emitter = event_emitter
        self.current_user_id = current_user_id
    
    async def set_commission(
        self,
        data: CommissionStructureCreate
    ) -> CommissionStructure:
        """Set commission structure for commodity"""
        
        commission = await self.repository.create(**data.model_dump())
        
        await self.event_emitter.emit(
            CommissionStructureSet(
                aggregate_id=commission.commodity_id if commission.commodity_id else commission.trade_type_id,
                user_id=self.current_user_id,
                data={
                    "commission_id": str(commission.id),
                    "name": commission.name,
                    "rate": str(commission.rate) if commission.rate else None
                }
            )
        )
        
        return commission
    
    async def update_commission(
        self,
        commission_id: UUID,
        data: CommissionStructureUpdate
    ) -> Optional[CommissionStructure]:
        """Update commission structure"""
        
        commission = await self.repository.update(commission_id, **data.model_dump(exclude_unset=True))
        if not commission:
            return None
        
        await self.event_emitter.emit(
            CommissionStructureSet(
                aggregate_id=commission.commodity_id if commission.commodity_id else commission.trade_type_id,
                user_id=self.current_user_id,
                data={
                    "commission_id": str(commission.id),
                    "name": commission.name,
                    "rate": str(commission.rate) if commission.rate else None
                }
            )
        )
        
        return commission
    
    async def get_commission(
        self,
        commodity_id: UUID
    ) -> Optional[CommissionStructure]:
        """Get commission for commodity"""
        commissions = await self.repository.list_all(commodity_id=commodity_id)
        return commissions[0] if commissions else None
    
    async def list_commissions(
        self,
        commodity_id: Optional[UUID] = None,
        trade_type_id: Optional[UUID] = None,
        is_active: Optional[bool] = None
    ) -> List[CommissionStructure]:
        """List all commission structures with optional filters"""
        return await self.repository.list_all(
            commodity_id=commodity_id,
            trade_type_id=trade_type_id,
            is_active=is_active
        )
