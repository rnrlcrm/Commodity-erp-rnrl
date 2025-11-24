"""
Unit Tests - Requirement WebSocket Service

Tests real-time broadcasting for:
1. requirement.created
2. requirement.published (intent routing)
3. requirement.updated
4. requirement.fulfillment_updated
5. requirement.fulfilled
6. requirement.cancelled
7. requirement.ai_adjusted
8. requirement.risk_alert

Tests all 9 channel patterns.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4
from decimal import Decimal

from backend.modules.trade_desk.websocket.requirement_websocket import (
    RequirementWebSocketService,
    RequirementChannelPatterns,
)
from backend.modules.trade_desk.enums import IntentType, UrgencyLevel


@pytest.mark.asyncio
class TestRequirementWebSocketService:
    """Test RequirementWebSocketService broadcasting."""
    
    async def test_channel_patterns(self):
        """Test all channel pattern methods."""
        requirement_id = uuid4()
        buyer_id = uuid4()
        commodity_id = uuid4()
        
        # Test specific channels
        assert RequirementChannelPatterns.requirement_channel(requirement_id) == f"requirement:{requirement_id}"
        assert RequirementChannelPatterns.buyer_requirements_channel(buyer_id) == f"buyer:{buyer_id}:requirements"
        assert RequirementChannelPatterns.commodity_requirements_channel(commodity_id) == f"commodity:{commodity_id}:requirements"
        assert RequirementChannelPatterns.intent_requirements_channel("DIRECT_BUY") == "intent:DIRECT_BUY:requirements"
        assert RequirementChannelPatterns.urgency_requirements_channel("URGENT") == "urgency:URGENT:requirements"
        
        # Test global channels
        assert RequirementChannelPatterns.requirement_updates_channel() == "requirement:updates"
        assert RequirementChannelPatterns.requirement_intent_updates_channel() == "requirement:intent_updates"
        assert RequirementChannelPatterns.requirement_fulfillment_updates_channel() == "requirement:fulfillment_updates"
        assert RequirementChannelPatterns.requirement_risk_alerts_channel() == "requirement:risk_alerts"
    
    async def test_broadcast_requirement_created(self):
        """Test broadcasting requirement.created event."""
        mock_connection_manager = Mock()
        mock_connection_manager.broadcast_to_channel = AsyncMock()
        
        ws_service = RequirementWebSocketService(mock_connection_manager)
        
        requirement_id = uuid4()
        buyer_id = uuid4()
        commodity_id = uuid4()
        
        await ws_service.broadcast_requirement_created(
            requirement_id=requirement_id,
            buyer_id=buyer_id,
            commodity_id=commodity_id,
            intent_type=IntentType.DIRECT_BUY.value,
            urgency_level=UrgencyLevel.NORMAL.value,
            data={
                "min_quantity": 100.0,
                "max_quantity": 500.0,
                "max_budget_per_unit": 76500.0,
            }
        )
        
        # Verify broadcast to 4 channels
        assert mock_connection_manager.broadcast_to_channel.call_count == 4
        
        # Verify channels
        calls = mock_connection_manager.broadcast_to_channel.call_args_list
        channels = [call[0][0] for call in calls]
        assert f"requirement:{requirement_id}" in channels
        assert f"buyer:{buyer_id}:requirements" in channels
        assert f"commodity:{commodity_id}:requirements" in channels
        assert "requirement:updates" in channels
    
    async def test_broadcast_requirement_published_with_intent_routing(self):
        """Test broadcasting requirement.published triggers intent routing."""
        mock_connection_manager = Mock()
        mock_connection_manager.broadcast_to_channel = AsyncMock()
        
        ws_service = RequirementWebSocketService(mock_connection_manager)
        
        requirement_id = uuid4()
        buyer_id = uuid4()
        commodity_id = uuid4()
        
        await ws_service.broadcast_requirement_published(
            requirement_id=requirement_id,
            buyer_id=buyer_id,
            commodity_id=commodity_id,
            intent_type=IntentType.NEGOTIATION.value,
            urgency_level=UrgencyLevel.URGENT.value,
            data={
                "min_quantity": 100.0,
                "max_quantity": 500.0,
                "max_budget_per_unit": 76500.0,
                "buyer_priority_score": 1.5,
            }
        )
        
        # Verify broadcast to 7 channels (including intent routing)
        assert mock_connection_manager.broadcast_to_channel.call_count == 7
        
        # Verify intent routing channels
        calls = mock_connection_manager.broadcast_to_channel.call_args_list
        channels = [call[0][0] for call in calls]
        assert "intent:NEGOTIATION:requirements" in channels  # 🚀 Intent routing
        assert "urgency:URGENT:requirements" in channels
        assert "requirement:intent_updates" in channels  # 🚀 Global intent
        assert f"requirement:{requirement_id}" in channels
        assert f"buyer:{buyer_id}:requirements" in channels
        assert f"commodity:{commodity_id}:requirements" in channels
        assert "requirement:updates" in channels
    
    async def test_broadcast_fulfillment_updated(self):
        """Test broadcasting fulfillment progress."""
        mock_connection_manager = Mock()
        mock_connection_manager.broadcast_to_channel = AsyncMock()
        
        ws_service = RequirementWebSocketService(mock_connection_manager)
        
        requirement_id = uuid4()
        buyer_id = uuid4()
        
        await ws_service.broadcast_fulfillment_updated(
            requirement_id=requirement_id,
            buyer_id=buyer_id,
            data={
                "purchased_quantity": 200.0,
                "amount_spent": 15000000.0,
                "remaining_quantity": 300.0,
            }
        )
        
        # Verify broadcast to 3 channels
        assert mock_connection_manager.broadcast_to_channel.call_count == 3
        
        calls = mock_connection_manager.broadcast_to_channel.call_args_list
        channels = [call[0][0] for call in calls]
        assert f"requirement:{requirement_id}" in channels
        assert f"buyer:{buyer_id}:requirements" in channels
        assert "requirement:fulfillment_updates" in channels
    
    async def test_broadcast_requirement_fulfilled(self):
        """Test broadcasting requirement fulfilled."""
        mock_connection_manager = Mock()
        mock_connection_manager.broadcast_to_channel = AsyncMock()
        
        ws_service = RequirementWebSocketService(mock_connection_manager)
        
        requirement_id = uuid4()
        buyer_id = uuid4()
        
        await ws_service.broadcast_requirement_fulfilled(
            requirement_id=requirement_id,
            buyer_id=buyer_id,
            data={
                "total_purchased_quantity": 500.0,
                "total_spent": 38250000.0,
                "avg_price_per_unit": 76500.0,
            }
        )
        
        # Verify broadcast to 3 channels
        assert mock_connection_manager.broadcast_to_channel.call_count == 3
        
        calls = mock_connection_manager.broadcast_to_channel.call_args_list
        channels = [call[0][0] for call in calls]
        assert f"requirement:{requirement_id}" in channels
        assert f"buyer:{buyer_id}:requirements" in channels
        assert "requirement:fulfillment_updates" in channels
    
    async def test_broadcast_requirement_cancelled(self):
        """Test broadcasting requirement cancelled."""
        mock_connection_manager = Mock()
        mock_connection_manager.broadcast_to_channel = AsyncMock()
        
        ws_service = RequirementWebSocketService(mock_connection_manager)
        
        requirement_id = uuid4()
        buyer_id = uuid4()
        
        await ws_service.broadcast_requirement_cancelled(
            requirement_id=requirement_id,
            buyer_id=buyer_id,
            data={
                "reason": "Business requirements changed",
                "unfulfilled_quantity": 300.0,
            }
        )
        
        # Verify broadcast to 3 channels
        assert mock_connection_manager.broadcast_to_channel.call_count == 3
        
        calls = mock_connection_manager.broadcast_to_channel.call_args_list
        channels = [call[0][0] for call in calls]
        assert f"requirement:{requirement_id}" in channels
        assert f"buyer:{buyer_id}:requirements" in channels
        assert "requirement:updates" in channels
    
    async def test_broadcast_ai_adjusted(self):
        """Test broadcasting AI adjustment event."""
        mock_connection_manager = Mock()
        mock_connection_manager.broadcast_to_channel = AsyncMock()
        
        ws_service = RequirementWebSocketService(mock_connection_manager)
        
        requirement_id = uuid4()
        buyer_id = uuid4()
        
        await ws_service.broadcast_ai_adjusted(
            requirement_id=requirement_id,
            buyer_id=buyer_id,
            data={
                "adjustment_type": "budget",
                "old_value": "76500",
                "new_value": "80000",
                "ai_confidence": 0.85,
                "ai_reasoning": "Market prices increased 5%",
                "auto_applied": True,
            }
        )
        
        # Verify broadcast to 3 channels
        assert mock_connection_manager.broadcast_to_channel.call_count == 3
        
        calls = mock_connection_manager.broadcast_to_channel.call_args_list
        channels = [call[0][0] for call in calls]
        assert f"requirement:{requirement_id}" in channels
        assert f"buyer:{buyer_id}:requirements" in channels
        assert "requirement:updates" in channels
        
        # Verify event data
        message = calls[0][0][1]
        assert message.event == "requirement.ai_adjusted"
        assert message.data["ai_confidence"] == 0.85
    
    async def test_broadcast_risk_alert(self):
        """Test broadcasting risk alert."""
        mock_connection_manager = Mock()
        mock_connection_manager.broadcast_to_channel = AsyncMock()
        
        ws_service = RequirementWebSocketService(mock_connection_manager)
        
        requirement_id = uuid4()
        buyer_id = uuid4()
        
        await ws_service.broadcast_risk_alert(
            requirement_id=requirement_id,
            buyer_id=buyer_id,
            risk_status="FAIL",
            risk_score=35,
            risk_factors=["Insufficient credit limit", "Low buyer rating"],
            data={
                "estimated_trade_value": 7650000.0,
                "buyer_exposure_after_trade": -2000000.0,
            }
        )
        
        # Verify broadcast to 3 channels including risk_alerts
        assert mock_connection_manager.broadcast_to_channel.call_count == 3
        
        calls = mock_connection_manager.broadcast_to_channel.call_args_list
        channels = [call[0][0] for call in calls]
        assert f"requirement:{requirement_id}" in channels
        assert f"buyer:{buyer_id}:requirements" in channels
        assert "requirement:risk_alerts" in channels  # 🚀 Risk alert channel
        
        # Verify event data
        message = calls[0][0][1]
        assert message.event == "requirement.risk_alert"
        assert message.data["risk_status"] == "FAIL"
        assert message.data["risk_score"] == 35
        assert len(message.data["risk_factors"]) == 2
    
    async def test_broadcast_updated(self):
        """Test broadcasting requirement updated."""
        mock_connection_manager = Mock()
        mock_connection_manager.broadcast_to_channel = AsyncMock()
        
        ws_service = RequirementWebSocketService(mock_connection_manager)
        
        requirement_id = uuid4()
        buyer_id = uuid4()
        
        await ws_service.broadcast_requirement_updated(
            requirement_id=requirement_id,
            buyer_id=buyer_id,
            updated_fields={"max_budget_per_unit": "80000"},
            data={}
        )
        
        # Verify broadcast to 3 channels
        assert mock_connection_manager.broadcast_to_channel.call_count == 3
        
        calls = mock_connection_manager.broadcast_to_channel.call_args_list
        channels = [call[0][0] for call in calls]
        assert f"requirement:{requirement_id}" in channels
        assert f"buyer:{buyer_id}:requirements" in channels
        assert "requirement:updates" in channels
