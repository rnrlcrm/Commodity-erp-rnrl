"""
Integration Tests - Requirement Service

Tests the 12-step AI pipeline and all service methods:
1. create_requirement with AI enhancements
2. publish_requirement with intent routing
3. cancel_requirement
4. update_fulfillment
5. apply_ai_adjustment (Enhancement #7)
6. update_risk_precheck (Risk Management)
7. search operations
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from unittest.mock import Mock, AsyncMock, patch

from backend.modules.trade_desk.services.requirement_service import RequirementService
from backend.modules.trade_desk.enums import (
    RequirementStatus,
    IntentType,
    MarketVisibility,
    UrgencyLevel,
)


@pytest.mark.asyncio
class TestRequirementService:
    """Test RequirementService with mocked database."""
    
    async def test_create_requirement_basic(self):
        """Test creating requirement with basic 12-step pipeline."""
        # Mock dependencies
        mock_db = AsyncMock()
        mock_ws_service = Mock()
        mock_ws_service.broadcast_requirement_created = AsyncMock()
        
        service = RequirementService(mock_db, ws_service=mock_ws_service)
        
        # Mock repository methods
        mock_requirement = Mock()
        mock_requirement.id = uuid4()
        mock_requirement.buyer_partner_id = uuid4()
        mock_requirement.commodity_id = uuid4()
        mock_requirement.intent_type = IntentType.DIRECT_BUY.value
        mock_requirement.urgency_level = UrgencyLevel.NORMAL.value
        mock_requirement.min_quantity = Decimal("100")
        mock_requirement.max_quantity = Decimal("500")
        mock_requirement.max_budget_per_unit = Decimal("76500")
        mock_requirement.status = RequirementStatus.DRAFT.value
        mock_requirement.market_visibility = MarketVisibility.PUBLIC.value
        mock_requirement.emit_created = Mock()
        mock_requirement.flush_events = AsyncMock()
        
        service.repo.create = AsyncMock(return_value=mock_requirement)
        
        # Mock AI pipeline methods
        service._validate_buyer_locations = AsyncMock()
        service._fetch_buyer_credit_limit = AsyncMock(return_value=None)
        service._fetch_buyer_rating = AsyncMock(return_value=None)
        service._fetch_payment_performance = AsyncMock(return_value=None)
        service.normalize_quality_requirements = AsyncMock(
            return_value={"staple_length": {"min": 28, "max": 30}}
        )
        service.suggest_market_price = AsyncMock(return_value={
            "suggested_max_price": Decimal("77000"),
            "confidence_score": 85,
            "is_unrealistic": False
        })
        service.calculate_buyer_priority_score = AsyncMock(return_value=1.5)
        service.validate_budget_realism = AsyncMock(return_value={"is_unrealistic": False})
        service.generate_market_context_embedding = AsyncMock(return_value=[0.1] * 1536)
        service.adjust_for_market_sentiment = AsyncMock(return_value={
            "sentiment": "neutral",
            "adjustment_factor": 1.0,
            "reason": "Market stable"
        })
        service.recommend_quality_tolerances = AsyncMock(return_value={})
        service.suggest_commodity_equivalents = AsyncMock(return_value=None)
        service.suggest_negotiation_preferences = AsyncMock(return_value={
            "allow_auto_negotiation": True,
            "max_rounds": 5
        })
        service.recommend_sellers = AsyncMock(return_value=[])
        service.calculate_ai_score_vector = AsyncMock(return_value={})
        service._route_by_intent = AsyncMock()
        
        # Create requirement
        buyer_id = uuid4()
        commodity_id = uuid4()
        created_by = uuid4()
        
        result = await service.create_requirement(
            buyer_id=buyer_id,
            commodity_id=commodity_id,
            min_quantity=Decimal("100"),
            max_quantity=Decimal("500"),
            quantity_unit="bales",
            max_budget_per_unit=Decimal("76500"),
            quality_requirements={"staple_length": {"min": 28}},
            valid_from=datetime.now(timezone.utc),
            valid_until=datetime.now(timezone.utc) + timedelta(days=30),
            created_by=created_by,
            intent_type=IntentType.DIRECT_BUY.value,
        )
        
        # Verify AI pipeline executed
        service._validate_buyer_locations.assert_called_once()
        service.normalize_quality_requirements.assert_called_once()
        service.suggest_market_price.assert_called_once()
        service.calculate_buyer_priority_score.assert_called_once()
        service.generate_market_context_embedding.assert_called_once()
        
        # Verify repository called
        service.repo.create.assert_called_once()
        
        # Verify event emitted
        mock_requirement.emit_created.assert_called_once_with(created_by)
        mock_requirement.flush_events.assert_called_once()
    
    async def test_create_requirement_with_auto_publish(self):
        """Test creating requirement with auto-publish triggers intent routing."""
        mock_db = AsyncMock()
        mock_ws_service = Mock()
        mock_ws_service.broadcast_requirement_created = AsyncMock()
        mock_ws_service.broadcast_requirement_published = AsyncMock()
        
        service = RequirementService(mock_db, ws_service=mock_ws_service)
        
        # Mock requirement
        mock_requirement = Mock()
        mock_requirement.id = uuid4()
        mock_requirement.buyer_partner_id = uuid4()
        mock_requirement.commodity_id = uuid4()
        mock_requirement.intent_type = IntentType.NEGOTIATION.value
        mock_requirement.urgency_level = UrgencyLevel.URGENT.value
        mock_requirement.min_quantity = Decimal("100")
        mock_requirement.max_quantity = Decimal("500")
        mock_requirement.max_budget_per_unit = Decimal("76500")
        mock_requirement.quality_requirements = {}
        mock_requirement.buyer_priority_score = 1.5
        mock_requirement.emit_created = Mock()
        mock_requirement.publish = Mock()
        mock_requirement.emit_published = Mock()
        mock_requirement.flush_events = AsyncMock()
        
        service.repo.create = AsyncMock(return_value=mock_requirement)
        
        # Mock AI pipeline
        service._validate_buyer_locations = AsyncMock()
        service._fetch_buyer_credit_limit = AsyncMock(return_value=None)
        service._fetch_buyer_rating = AsyncMock(return_value=None)
        service._fetch_payment_performance = AsyncMock(return_value=None)
        service.normalize_quality_requirements = AsyncMock(return_value={})
        service.suggest_market_price = AsyncMock(return_value={
            "suggested_max_price": None,
            "confidence_score": None,
            "is_unrealistic": False
        })
        service.calculate_buyer_priority_score = AsyncMock(return_value=1.5)
        service.validate_budget_realism = AsyncMock(return_value={"is_unrealistic": False})
        service.generate_market_context_embedding = AsyncMock(return_value=[])
        service.adjust_for_market_sentiment = AsyncMock(return_value={
            "adjustment_factor": 1.0,
            "sentiment": "neutral",
            "reason": ""
        })
        service.recommend_quality_tolerances = AsyncMock(return_value={})
        service.suggest_commodity_equivalents = AsyncMock(return_value=None)
        service.suggest_negotiation_preferences = AsyncMock(return_value={})
        service.recommend_sellers = AsyncMock(return_value=[])
        service.calculate_ai_score_vector = AsyncMock(return_value={})
        service._route_by_intent = AsyncMock()
        
        # Create with auto_publish=True
        buyer_id = uuid4()
        commodity_id = uuid4()
        created_by = uuid4()
        
        result = await service.create_requirement(
            buyer_id=buyer_id,
            commodity_id=commodity_id,
            min_quantity=Decimal("100"),
            max_quantity=Decimal("500"),
            quantity_unit="bales",
            max_budget_per_unit=Decimal("76500"),
            quality_requirements={},
            valid_from=datetime.now(timezone.utc),
            valid_until=datetime.now(timezone.utc) + timedelta(days=30),
            created_by=created_by,
            auto_publish=True,  # Auto-publish
        )
        
        # Verify publish called
        mock_requirement.publish.assert_called_once_with(created_by)
        mock_requirement.emit_published.assert_called_once_with(created_by)
        
        # Verify intent routing triggered
        service._route_by_intent.assert_called_once_with(mock_requirement)
        
        # Verify WebSocket broadcasts
        mock_ws_service.broadcast_requirement_created.assert_called_once()
        mock_ws_service.broadcast_requirement_published.assert_called_once()
    
    async def test_publish_requirement(self):
        """Test publishing requirement triggers intent routing."""
        mock_db = AsyncMock()
        mock_ws_service = Mock()
        mock_ws_service.broadcast_requirement_published = AsyncMock()
        
        service = RequirementService(mock_db, ws_service=mock_ws_service)
        
        # Mock requirement
        requirement_id = uuid4()
        mock_requirement = Mock()
        mock_requirement.id = requirement_id
        mock_requirement.buyer_partner_id = uuid4()
        mock_requirement.commodity_id = uuid4()
        mock_requirement.intent_type = IntentType.AUCTION_REQUEST.value
        mock_requirement.urgency_level = UrgencyLevel.URGENT.value
        mock_requirement.min_quantity = Decimal("100")
        mock_requirement.max_quantity = Decimal("500")
        mock_requirement.max_budget_per_unit = Decimal("76500")
        mock_requirement.quality_requirements = {}
        mock_requirement.buyer_priority_score = 1.0
        mock_requirement.publish = Mock()
        mock_requirement.flush_events = AsyncMock()
        
        service.repo.get_by_id = AsyncMock(return_value=mock_requirement)
        service.repo.update = AsyncMock(return_value=mock_requirement)
        service._route_by_intent = AsyncMock()
        
        # Publish
        published_by = uuid4()
        result = await service.publish_requirement(requirement_id, published_by)
        
        # Verify
        mock_requirement.publish.assert_called_once_with(published_by)
        service.repo.update.assert_called_once()
        service._route_by_intent.assert_called_once_with(mock_requirement)
        mock_ws_service.broadcast_requirement_published.assert_called_once()
    
    async def test_cancel_requirement(self):
        """Test cancelling requirement."""
        mock_db = AsyncMock()
        mock_ws_service = Mock()
        mock_ws_service.broadcast_requirement_cancelled = AsyncMock()
        
        service = RequirementService(mock_db, ws_service=mock_ws_service)
        
        # Mock requirement
        requirement_id = uuid4()
        mock_requirement = Mock()
        mock_requirement.id = requirement_id
        mock_requirement.buyer_partner_id = uuid4()
        mock_requirement.max_quantity = Decimal("500")
        mock_requirement.total_purchased_quantity = Decimal("200")
        mock_requirement.cancel = Mock()
        mock_requirement.flush_events = AsyncMock()
        
        service.repo.get_by_id = AsyncMock(return_value=mock_requirement)
        service.repo.update = AsyncMock(return_value=mock_requirement)
        
        # Cancel
        cancelled_by = uuid4()
        reason = "Changed business requirements"
        result = await service.cancel_requirement(requirement_id, cancelled_by, reason)
        
        # Verify
        mock_requirement.cancel.assert_called_once_with(cancelled_by, reason)
        service.repo.update.assert_called_once()
        mock_ws_service.broadcast_requirement_cancelled.assert_called_once()
    
    async def test_update_fulfillment(self):
        """Test updating fulfillment with WebSocket broadcast."""
        mock_db = AsyncMock()
        mock_ws_service = Mock()
        mock_ws_service.broadcast_fulfillment_updated = AsyncMock()
        mock_ws_service.broadcast_requirement_fulfilled = AsyncMock()
        
        service = RequirementService(mock_db, ws_service=mock_ws_service)
        
        # Mock requirement
        requirement_id = uuid4()
        mock_requirement = Mock()
        mock_requirement.id = requirement_id
        mock_requirement.buyer_partner_id = uuid4()
        mock_requirement.status = RequirementStatus.PARTIALLY_FULFILLED.value
        mock_requirement.max_quantity = Decimal("500")
        mock_requirement.total_purchased_quantity = Decimal("300")
        mock_requirement.total_spent = Decimal("22500000")
        mock_requirement.update_fulfillment = Mock()
        mock_requirement.flush_events = AsyncMock()
        
        service.repo.get_by_id = AsyncMock(return_value=mock_requirement)
        service.repo.update = AsyncMock(return_value=mock_requirement)
        
        # Update fulfillment
        updated_by = uuid4()
        result = await service.update_fulfillment(
            requirement_id=requirement_id,
            purchased_quantity=Decimal("100"),
            amount_spent=Decimal("7500000"),
            updated_by=updated_by,
        )
        
        # Verify
        mock_requirement.update_fulfillment.assert_called_once()
        service.repo.update.assert_called_once()
        mock_ws_service.broadcast_fulfillment_updated.assert_called_once()
    
    async def test_apply_ai_adjustment(self):
        """Test applying AI adjustment with WebSocket broadcast."""
        mock_db = AsyncMock()
        mock_ws_service = Mock()
        mock_ws_service.broadcast_ai_adjusted = AsyncMock()
        
        service = RequirementService(mock_db, ws_service=mock_ws_service)
        
        # Mock requirement
        requirement_id = uuid4()
        mock_requirement = Mock()
        mock_requirement.id = requirement_id
        mock_requirement.buyer_partner_id = uuid4()
        mock_requirement.max_budget_per_unit = Decimal("76500")
        mock_requirement.emit_ai_adjusted = Mock()
        mock_requirement.flush_events = AsyncMock()
        
        service.repo.get_by_id = AsyncMock(return_value=mock_requirement)
        service.repo.update = AsyncMock(return_value=mock_requirement)
        
        # Apply AI adjustment
        result = await service.apply_ai_adjustment(
            requirement_id=requirement_id,
            adjustment_type="budget",
            new_value=Decimal("80000"),
            ai_confidence=0.87,
            ai_reasoning="Market prices increased due to supply shortage",
            market_context={"supply_change": "-15%"},
            expected_impact="Better matching rate",
            auto_apply=True,
        )
        
        # Verify
        assert mock_requirement.max_budget_per_unit == Decimal("80000")
        mock_requirement.emit_ai_adjusted.assert_called_once()
        service.repo.update.assert_called_once()
        mock_ws_service.broadcast_ai_adjusted.assert_called_once()
    
    async def test_update_risk_precheck(self):
        """Test updating risk precheck with WebSocket alert."""
        mock_db = AsyncMock()
        mock_ws_service = Mock()
        mock_ws_service.broadcast_risk_alert = AsyncMock()
        
        service = RequirementService(mock_db, ws_service=mock_ws_service)
        
        # Mock requirement
        requirement_id = uuid4()
        mock_requirement = Mock()
        mock_requirement.id = requirement_id
        mock_requirement.buyer_partner_id = uuid4()
        mock_requirement.update_risk_precheck = Mock(return_value={
            "risk_precheck_status": "FAIL",
            "risk_precheck_score": 35,
            "estimated_trade_value": Decimal("7650000"),
            "buyer_exposure_after_trade": Decimal("-2000000"),
            "risk_factors": ["Insufficient credit limit", "Low buyer rating"]
        })
        
        service.repo.get_by_id = AsyncMock(return_value=mock_requirement)
        service.repo.update = AsyncMock()
        
        # Update risk precheck
        result = await service.update_risk_precheck(
            requirement_id=requirement_id,
            credit_limit_remaining=Decimal("5000000"),
            rating_score=Decimal("1.5"),
            payment_performance_score=40,
        )
        
        # Verify
        mock_requirement.update_risk_precheck.assert_called_once()
        service.repo.update.assert_called_once()
        
        # Verify risk alert broadcasted (status is FAIL)
        mock_ws_service.broadcast_risk_alert.assert_called_once()
        call_args = mock_ws_service.broadcast_risk_alert.call_args
        assert call_args[1]["risk_status"] == "FAIL"
        assert call_args[1]["risk_score"] == 35
