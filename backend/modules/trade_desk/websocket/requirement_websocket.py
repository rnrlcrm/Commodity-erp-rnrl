"""
Requirement WebSocket Routes - Engine 2

Real-time WebSocket channels for requirement updates and intent-based routing.

🚀 2035-READY WEBSOCKET CHANNELS:

1. requirement.updates - All requirement events
2. requirement.intent_updates - Intent-based routing events (CRITICAL)
3. requirement.fulfillment_updates - Fulfillment progress
4. requirement.risk_alerts - Risk assessment changes

Channel Patterns:
- requirement:{requirement_id} - Specific requirement updates
- buyer:{buyer_id}:requirements - All buyer's requirements
- commodity:{commodity_id}:requirements - Commodity demand updates
- intent:{intent_type}:requirements - Intent-based routing (DIRECT_BUY, NEGOTIATION, etc.)

Event Types:
- requirement.created
- requirement.published (🚀 triggers intent routing)
- requirement.updated
- requirement.budget_changed
- requirement.quality_changed
- requirement.visibility_changed
- requirement.fulfillment_updated
- requirement.fulfilled
- requirement.expired
- requirement.cancelled
- requirement.ai_adjusted (🚀 AI transparency)
- requirement.risk_alert (🚀 risk management)

WebSocket Usage:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/connect?token=JWT_TOKEN');

// Subscribe to intent updates (for matching engine)
ws.send(JSON.stringify({
    event: 'subscribe',
    channel: 'intent:DIRECT_BUY:requirements'
}));

// Subscribe to buyer's requirements
ws.send(JSON.stringify({
    event: 'subscribe',
    channel: 'buyer:123e4567-e89b-12d3-a456-426614174000:requirements'
}));

// Handle requirement events
ws.onmessage = (event) => {
    const message = JSON.parse(event.data);
    if (message.channel.startsWith('intent:')) {
        console.log('New requirement for intent:', message.data);
        // Trigger matching engine
    }
};
```
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import Depends

from backend.api.v1.websocket import get_connection_manager
from backend.core.websocket import ConnectionManager, WebSocketMessage
from backend.core.websocket.sharding import ChannelPatterns
from backend.modules.trade_desk.enums import IntentType

logger = logging.getLogger(__name__)


class RequirementChannelPatterns(ChannelPatterns):
    """🚀 Channel patterns for Requirement Engine WebSocket"""
    
    @staticmethod
    def requirement_channel(requirement_id: UUID) -> str:
        """Specific requirement updates channel"""
        return f"requirement:{requirement_id}"
    
    @staticmethod
    def buyer_requirements_channel(buyer_id: UUID) -> str:
        """All requirements for a buyer"""
        return f"buyer:{buyer_id}:requirements"
    
    @staticmethod
    def commodity_requirements_channel(commodity_id: UUID) -> str:
        """All requirements for a commodity (demand updates)"""
        return f"commodity:{commodity_id}:requirements"
    
    @staticmethod
    def intent_requirements_channel(intent_type: str) -> str:
        """🚀 CRITICAL: Intent-based routing channel
        
        This channel is subscribed by downstream engines:
        - DIRECT_BUY → Matching Engine (Engine 3)
        - NEGOTIATION → Negotiation Engine (Engine 4)
        - AUCTION_REQUEST → Auction Engine (Engine 5)
        - PRICE_DISCOVERY_ONLY → Analytics (no routing)
        """
        return f"intent:{intent_type}:requirements"
    
    @staticmethod
    def requirement_updates_channel() -> str:
        """Global requirement updates (all events)"""
        return "requirement:updates"
    
    @staticmethod
    def requirement_intent_updates_channel() -> str:
        """🚀 Global intent-based routing events (CRITICAL for engine coordination)"""
        return "requirement:intent_updates"
    
    @staticmethod
    def requirement_fulfillment_updates_channel() -> str:
        """Global fulfillment progress updates"""
        return "requirement:fulfillment_updates"
    
    @staticmethod
    def requirement_risk_alerts_channel() -> str:
        """🚀 Global risk assessment alerts"""
        return "requirement:risk_alerts"
    
    @staticmethod
    def urgency_requirements_channel(urgency_level: str) -> str:
        """Requirements by urgency level"""
        return f"urgency:{urgency_level}:requirements"


class RequirementWebSocketService:
    """
    🚀 Service for broadcasting requirement events via WebSocket.
    
    This service is called by RequirementService after each event emission.
    It broadcasts to appropriate channels for real-time updates.
    """
    
    def __init__(self, connection_manager: ConnectionManager):
        self.connection_manager = connection_manager
    
    async def broadcast_requirement_created(
        self,
        requirement_id: UUID,
        buyer_id: UUID,
        commodity_id: UUID,
        intent_type: str,
        urgency_level: str,
        data: Dict[str, Any]
    ) -> None:
        """
        Broadcast requirement.created event.
        
        Channels:
        - requirement:{requirement_id}
        - buyer:{buyer_id}:requirements
        - commodity:{commodity_id}:requirements
        - requirement:updates (global)
        """
        message = WebSocketMessage(
            event="requirement.created",
            channel=RequirementChannelPatterns.requirement_channel(requirement_id),
            data={
                "requirement_id": str(requirement_id),
                "buyer_id": str(buyer_id),
                "commodity_id": str(commodity_id),
                "intent_type": intent_type,
                "urgency_level": urgency_level,
                **data
            }
        )
        
        # Broadcast to multiple channels
        channels = [
            RequirementChannelPatterns.requirement_channel(requirement_id),
            RequirementChannelPatterns.buyer_requirements_channel(buyer_id),
            RequirementChannelPatterns.commodity_requirements_channel(commodity_id),
            RequirementChannelPatterns.requirement_updates_channel(),
        ]
        
        for channel in channels:
            message.channel = channel
            await self.connection_manager.broadcast_to_channel(channel, message)
    
    async def broadcast_requirement_published(
        self,
        requirement_id: UUID,
        buyer_id: UUID,
        commodity_id: UUID,
        intent_type: str,
        urgency_level: str,
        data: Dict[str, Any]
    ) -> None:
        """
        🚀 Broadcast requirement.published event.
        
        CRITICAL: This triggers intent-based routing to downstream engines.
        
        Channels:
        - requirement:{requirement_id}
        - buyer:{buyer_id}:requirements
        - commodity:{commodity_id}:requirements
        - intent:{intent_type}:requirements (🚀 CRITICAL for routing)
        - urgency:{urgency_level}:requirements
        - requirement:updates (global)
        - requirement:intent_updates (🚀 CRITICAL global intent channel)
        """
        message = WebSocketMessage(
            event="requirement.published",
            channel=RequirementChannelPatterns.requirement_channel(requirement_id),
            data={
                "requirement_id": str(requirement_id),
                "buyer_id": str(buyer_id),
                "commodity_id": str(commodity_id),
                "intent_type": intent_type,
                "urgency_level": urgency_level,
                **data
            }
        )
        
        # Broadcast to multiple channels
        channels = [
            RequirementChannelPatterns.requirement_channel(requirement_id),
            RequirementChannelPatterns.buyer_requirements_channel(buyer_id),
            RequirementChannelPatterns.commodity_requirements_channel(commodity_id),
            RequirementChannelPatterns.intent_requirements_channel(intent_type),  # 🚀 Intent routing
            RequirementChannelPatterns.urgency_requirements_channel(urgency_level),
            RequirementChannelPatterns.requirement_updates_channel(),
            RequirementChannelPatterns.requirement_intent_updates_channel(),  # 🚀 Global intent
        ]
        
        for channel in channels:
            message.channel = channel
            await self.connection_manager.broadcast_to_channel(channel, message)
        
        logger.info(
            f"Requirement {requirement_id} published - Intent: {intent_type} - "
            f"Broadcasted to {len(channels)} channels"
        )
    
    async def broadcast_requirement_updated(
        self,
        requirement_id: UUID,
        buyer_id: UUID,
        updated_fields: Dict[str, Any],
        data: Dict[str, Any]
    ) -> None:
        """
        Broadcast requirement.updated event.
        
        Channels:
        - requirement:{requirement_id}
        - buyer:{buyer_id}:requirements
        - requirement:updates (global)
        """
        message = WebSocketMessage(
            event="requirement.updated",
            channel=RequirementChannelPatterns.requirement_channel(requirement_id),
            data={
                "requirement_id": str(requirement_id),
                "buyer_id": str(buyer_id),
                "updated_fields": updated_fields,
                **data
            }
        )
        
        channels = [
            RequirementChannelPatterns.requirement_channel(requirement_id),
            RequirementChannelPatterns.buyer_requirements_channel(buyer_id),
            RequirementChannelPatterns.requirement_updates_channel(),
        ]
        
        for channel in channels:
            message.channel = channel
            await self.connection_manager.broadcast_to_channel(channel, message)
    
    async def broadcast_fulfillment_updated(
        self,
        requirement_id: UUID,
        buyer_id: UUID,
        data: Dict[str, Any]
    ) -> None:
        """
        Broadcast requirement.fulfillment_updated event.
        
        Channels:
        - requirement:{requirement_id}
        - buyer:{buyer_id}:requirements
        - requirement:fulfillment_updates (global)
        """
        message = WebSocketMessage(
            event="requirement.fulfillment_updated",
            channel=RequirementChannelPatterns.requirement_channel(requirement_id),
            data={
                "requirement_id": str(requirement_id),
                "buyer_id": str(buyer_id),
                **data
            }
        )
        
        channels = [
            RequirementChannelPatterns.requirement_channel(requirement_id),
            RequirementChannelPatterns.buyer_requirements_channel(buyer_id),
            RequirementChannelPatterns.requirement_fulfillment_updates_channel(),
        ]
        
        for channel in channels:
            message.channel = channel
            await self.connection_manager.broadcast_to_channel(channel, message)
    
    async def broadcast_requirement_fulfilled(
        self,
        requirement_id: UUID,
        buyer_id: UUID,
        data: Dict[str, Any]
    ) -> None:
        """
        Broadcast requirement.fulfilled event.
        
        Channels:
        - requirement:{requirement_id}
        - buyer:{buyer_id}:requirements
        - requirement:fulfillment_updates (global)
        """
        message = WebSocketMessage(
            event="requirement.fulfilled",
            channel=RequirementChannelPatterns.requirement_channel(requirement_id),
            data={
                "requirement_id": str(requirement_id),
                "buyer_id": str(buyer_id),
                **data
            }
        )
        
        channels = [
            RequirementChannelPatterns.requirement_channel(requirement_id),
            RequirementChannelPatterns.buyer_requirements_channel(buyer_id),
            RequirementChannelPatterns.requirement_fulfillment_updates_channel(),
        ]
        
        for channel in channels:
            message.channel = channel
            await self.connection_manager.broadcast_to_channel(channel, message)
    
    async def broadcast_requirement_cancelled(
        self,
        requirement_id: UUID,
        buyer_id: UUID,
        data: Dict[str, Any]
    ) -> None:
        """
        Broadcast requirement.cancelled event.
        
        Channels:
        - requirement:{requirement_id}
        - buyer:{buyer_id}:requirements
        - requirement:updates (global)
        """
        message = WebSocketMessage(
            event="requirement.cancelled",
            channel=RequirementChannelPatterns.requirement_channel(requirement_id),
            data={
                "requirement_id": str(requirement_id),
                "buyer_id": str(buyer_id),
                **data
            }
        )
        
        channels = [
            RequirementChannelPatterns.requirement_channel(requirement_id),
            RequirementChannelPatterns.buyer_requirements_channel(buyer_id),
            RequirementChannelPatterns.requirement_updates_channel(),
        ]
        
        for channel in channels:
            message.channel = channel
            await self.connection_manager.broadcast_to_channel(channel, message)
    
    async def broadcast_ai_adjusted(
        self,
        requirement_id: UUID,
        buyer_id: UUID,
        data: Dict[str, Any]
    ) -> None:
        """
        🚀 Broadcast requirement.ai_adjusted event (Enhancement #7).
        
        Provides transparency into AI decision making.
        
        Channels:
        - requirement:{requirement_id}
        - buyer:{buyer_id}:requirements
        - requirement:updates (global)
        """
        message = WebSocketMessage(
            event="requirement.ai_adjusted",
            channel=RequirementChannelPatterns.requirement_channel(requirement_id),
            data={
                "requirement_id": str(requirement_id),
                "buyer_id": str(buyer_id),
                **data
            }
        )
        
        channels = [
            RequirementChannelPatterns.requirement_channel(requirement_id),
            RequirementChannelPatterns.buyer_requirements_channel(buyer_id),
            RequirementChannelPatterns.requirement_updates_channel(),
        ]
        
        for channel in channels:
            message.channel = channel
            await self.connection_manager.broadcast_to_channel(channel, message)
    
    async def broadcast_risk_alert(
        self,
        requirement_id: UUID,
        buyer_id: UUID,
        risk_status: str,
        risk_score: int,
        risk_factors: list,
        data: Dict[str, Any]
    ) -> None:
        """
        🚀 Broadcast requirement.risk_alert event (Phase 5.5).
        
        Alerts when risk assessment changes (PASS → WARN → FAIL).
        
        Channels:
        - requirement:{requirement_id}
        - buyer:{buyer_id}:requirements
        - requirement:risk_alerts (🚀 global risk channel)
        """
        message = WebSocketMessage(
            event="requirement.risk_alert",
            channel=RequirementChannelPatterns.requirement_channel(requirement_id),
            data={
                "requirement_id": str(requirement_id),
                "buyer_id": str(buyer_id),
                "risk_status": risk_status,
                "risk_score": risk_score,
                "risk_factors": risk_factors,
                **data
            }
        )
        
        channels = [
            RequirementChannelPatterns.requirement_channel(requirement_id),
            RequirementChannelPatterns.buyer_requirements_channel(buyer_id),
            RequirementChannelPatterns.requirement_risk_alerts_channel(),
        ]
        
        for channel in channels:
            message.channel = channel
            await self.connection_manager.broadcast_to_channel(channel, message)
        
        logger.warning(
            f"Risk alert for requirement {requirement_id}: {risk_status} "
            f"(score: {risk_score}) - Factors: {risk_factors}"
        )


# Singleton instance (dependency injection)
_requirement_ws_service: Optional[RequirementWebSocketService] = None


def get_requirement_ws_service(
    connection_manager: ConnectionManager = Depends(get_connection_manager),
) -> RequirementWebSocketService:
    """Get or create RequirementWebSocketService singleton"""
    global _requirement_ws_service
    if _requirement_ws_service is None:
        _requirement_ws_service = RequirementWebSocketService(connection_manager)
    return _requirement_ws_service
