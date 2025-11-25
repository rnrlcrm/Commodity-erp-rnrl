"""
Test suite for Availability Risk Management features

Tests the 10 new risk management fields added to the Availability model:
1. expected_price
2. estimated_trade_value
3. risk_precheck_status
4. risk_precheck_score
5. seller_exposure_after_trade
6. seller_branch_id
7. blocked_for_branches
8. seller_rating_score
9. seller_delivery_score
10. risk_flags
"""

import pytest
from decimal import Decimal
from uuid import uuid4
from datetime import datetime, timedelta

from backend.modules.trade_desk.models.availability import Availability
from backend.modules.trade_desk.enums import AvailabilityStatus, MarketVisibility


class TestAvailabilityRiskManagement:
    """Test risk management features in Availability model"""
    
    def test_calculate_estimated_trade_value_with_expected_price(self):
        """Test trade value calculation using expected_price"""
        availability = Availability(
            id=uuid4(),
            commodity_id=uuid4(),
            location_id=uuid4(),
            seller_id=uuid4(),
            total_quantity=Decimal("500"),
            available_quantity=Decimal("500"),
            expected_price=Decimal("76500"),
            created_by=uuid4()
        )
        
        trade_value = availability.calculate_estimated_trade_value()
        
        assert trade_value == Decimal("38250000")  # 500 * 76500
        assert availability.estimated_trade_value == Decimal("38250000")
    
    def test_calculate_estimated_trade_value_fallback_to_base_price(self):
        """Test trade value falls back to base_price if expected_price is None"""
        availability = Availability(
            id=uuid4(),
            commodity_id=uuid4(),
            location_id=uuid4(),
            seller_id=uuid4(),
            total_quantity=Decimal("300"),
            available_quantity=Decimal("300"),
            base_price=Decimal("75000"),
            expected_price=None,
            created_by=uuid4()
        )
        
        trade_value = availability.calculate_estimated_trade_value()
        
        assert trade_value == Decimal("22500000")  # 300 * 75000
        assert availability.estimated_trade_value == Decimal("22500000")
    
    def test_update_risk_precheck_pass_status(self):
        """Test risk precheck with PASS status (high scores)"""
        availability = Availability(
            id=uuid4(),
            commodity_id=uuid4(),
            location_id=uuid4(),
            seller_id=uuid4(),
            total_quantity=Decimal("500"),
            available_quantity=Decimal("500"),
            expected_price=Decimal("76500"),
            created_by=uuid4()
        )
        
        user_id = uuid4()
        risk_assessment = availability.update_risk_precheck(
            seller_credit_limit_remaining=Decimal("50000000"),  # High limit
            seller_rating=Decimal("4.5"),  # Excellent rating
            seller_delivery_performance=95,  # Great delivery
            seller_exposure=Decimal("10000000"),
            user_id=user_id
        )
        
        assert availability.risk_precheck_status == "PASS"
        assert availability.risk_precheck_score >= 80
        assert availability.seller_rating_score == Decimal("4.5")
        assert availability.seller_delivery_score == 95
        assert availability.estimated_trade_value == Decimal("38250000")
        assert availability.seller_exposure_after_trade == Decimal("48250000")
        assert risk_assessment["risk_factors"] == []
    
    def test_update_risk_precheck_fail_status_insufficient_credit(self):
        """Test risk precheck with FAIL status (insufficient credit)"""
        availability = Availability(
            id=uuid4(),
            commodity_id=uuid4(),
            location_id=uuid4(),
            seller_id=uuid4(),
            total_quantity=Decimal("500"),
            available_quantity=Decimal("500"),
            expected_price=Decimal("76500"),
            created_by=uuid4()
        )
        
        user_id = uuid4()
        risk_assessment = availability.update_risk_precheck(
            seller_credit_limit_remaining=Decimal("5000000"),  # Insufficient
            seller_rating=Decimal("2.5"),  # Low rating
            seller_delivery_performance=45,  # Poor delivery
            seller_exposure=Decimal("20000000"),
            user_id=user_id
        )
        
        assert availability.risk_precheck_status == "FAIL"
        assert availability.risk_precheck_score < 60
        assert len(risk_assessment["risk_factors"]) >= 3
        
        # Check risk factors content
        risk_factors_str = " ".join(risk_assessment["risk_factors"])
        assert "Insufficient seller credit limit" in risk_factors_str
        assert "Low seller rating" in risk_factors_str
        assert "Poor delivery history" in risk_factors_str
        
        # Check risk_flags JSONB was populated
        assert availability.risk_flags is not None
        assert "risk_factors" in availability.risk_flags
        assert "assessed_at" in availability.risk_flags
    
    def test_update_risk_precheck_warn_status(self):
        """Test risk precheck with WARN status (moderate scores)"""
        availability = Availability(
            id=uuid4(),
            commodity_id=uuid4(),
            location_id=uuid4(),
            seller_id=uuid4(),
            total_quantity=Decimal("300"),
            available_quantity=Decimal("300"),
            expected_price=Decimal("75000"),
            created_by=uuid4()
        )
        
        user_id = uuid4()
        risk_assessment = availability.update_risk_precheck(
            seller_credit_limit_remaining=Decimal("30000000"),  # Sufficient
            seller_rating=Decimal("3.8"),  # Moderate rating
            seller_delivery_performance=72,  # Moderate delivery
            seller_exposure=Decimal("5000000"),
            user_id=user_id
        )
        
        # With moderate scores, should get WARN status (60-79 score range)
        assert availability.risk_precheck_status == "WARN"
        assert 60 <= availability.risk_precheck_score < 80
    
    def test_check_internal_trade_block_same_branch(self):
        """Test internal trade blocking when seller and buyer are same branch"""
        seller_branch_id = uuid4()
        
        availability = Availability(
            id=uuid4(),
            commodity_id=uuid4(),
            location_id=uuid4(),
            seller_id=uuid4(),
            total_quantity=Decimal("500"),
            available_quantity=Decimal("500"),
            seller_branch_id=seller_branch_id,
            blocked_for_branches=True,
            created_by=uuid4()
        )
        
        # Same branch should be blocked
        is_blocked = availability.check_internal_trade_block(seller_branch_id)
        assert is_blocked is True
    
    def test_check_internal_trade_block_different_branch(self):
        """Test internal trade allowed when different branches"""
        seller_branch_id = uuid4()
        buyer_branch_id = uuid4()
        
        availability = Availability(
            id=uuid4(),
            commodity_id=uuid4(),
            location_id=uuid4(),
            seller_id=uuid4(),
            total_quantity=Decimal("500"),
            available_quantity=Decimal("500"),
            seller_branch_id=seller_branch_id,
            blocked_for_branches=True,
            created_by=uuid4()
        )
        
        # Different branch should be allowed
        is_blocked = availability.check_internal_trade_block(buyer_branch_id)
        assert is_blocked is False
    
    def test_check_internal_trade_block_disabled(self):
        """Test internal trade blocking when feature is disabled"""
        seller_branch_id = uuid4()
        
        availability = Availability(
            id=uuid4(),
            commodity_id=uuid4(),
            location_id=uuid4(),
            seller_id=uuid4(),
            total_quantity=Decimal("500"),
            available_quantity=Decimal("500"),
            seller_branch_id=seller_branch_id,
            blocked_for_branches=False,  # Disabled
            created_by=uuid4()
        )
        
        # Should not block even with same branch
        is_blocked = availability.check_internal_trade_block(seller_branch_id)
        assert is_blocked is False
    
    def test_risk_flags_jsonb_structure(self):
        """Test that risk_flags JSONB is populated with correct structure"""
        availability = Availability(
            id=uuid4(),
            commodity_id=uuid4(),
            location_id=uuid4(),
            seller_id=uuid4(),
            total_quantity=Decimal("500"),
            available_quantity=Decimal("500"),
            expected_price=Decimal("76500"),
            created_by=uuid4()
        )
        
        user_id = uuid4()
        availability.update_risk_precheck(
            seller_credit_limit_remaining=Decimal("50000000"),
            seller_rating=Decimal("4.5"),
            seller_delivery_performance=95,
            seller_exposure=Decimal("10000000"),
            user_id=user_id
        )
        
        # Verify risk_flags structure
        assert availability.risk_flags is not None
        assert isinstance(availability.risk_flags, dict)
        assert "risk_factors" in availability.risk_flags
        assert "credit_limit_remaining" in availability.risk_flags
        assert "exposure_after_trade" in availability.risk_flags
        assert "rating_score" in availability.risk_flags
        assert "delivery_score" in availability.risk_flags
        assert "assessed_at" in availability.risk_flags
        
        # Verify data types
        assert isinstance(availability.risk_flags["risk_factors"], list)
        assert isinstance(availability.risk_flags["credit_limit_remaining"], float)
        assert isinstance(availability.risk_flags["exposure_after_trade"], float)
        assert isinstance(availability.risk_flags["rating_score"], float)
        assert isinstance(availability.risk_flags["delivery_score"], int)
        assert isinstance(availability.risk_flags["assessed_at"], str)
    
    def test_seller_rating_score_bounds(self):
        """Test seller rating score is within 0.00-5.00 bounds"""
        availability = Availability(
            id=uuid4(),
            commodity_id=uuid4(),
            location_id=uuid4(),
            seller_id=uuid4(),
            total_quantity=Decimal("500"),
            available_quantity=Decimal("500"),
            seller_rating_score=Decimal("4.75"),
            created_by=uuid4()
        )
        
        assert Decimal("0") <= availability.seller_rating_score <= Decimal("5")
    
    def test_seller_delivery_score_bounds(self):
        """Test seller delivery score is within 0-100 bounds"""
        availability = Availability(
            id=uuid4(),
            commodity_id=uuid4(),
            location_id=uuid4(),
            seller_id=uuid4(),
            total_quantity=Decimal("500"),
            available_quantity=Decimal("500"),
            seller_delivery_score=85,
            created_by=uuid4()
        )
        
        assert 0 <= availability.seller_delivery_score <= 100
    
    def test_risk_precheck_score_bounds(self):
        """Test risk precheck score is within 0-100 bounds"""
        availability = Availability(
            id=uuid4(),
            commodity_id=uuid4(),
            location_id=uuid4(),
            seller_id=uuid4(),
            total_quantity=Decimal("500"),
            available_quantity=Decimal("500"),
            expected_price=Decimal("76500"),
            created_by=uuid4()
        )
        
        user_id = uuid4()
        availability.update_risk_precheck(
            seller_credit_limit_remaining=Decimal("1000000"),  # Very low
            seller_rating=Decimal("1.0"),  # Very low
            seller_delivery_performance=10,  # Very low
            seller_exposure=Decimal("50000000"),
            user_id=user_id
        )
        
        assert 0 <= availability.risk_precheck_score <= 100
    
    def test_expected_price_used_over_base_price(self):
        """Test that expected_price takes precedence over base_price"""
        availability = Availability(
            id=uuid4(),
            commodity_id=uuid4(),
            location_id=uuid4(),
            seller_id=uuid4(),
            total_quantity=Decimal("500"),
            available_quantity=Decimal("500"),
            expected_price=Decimal("80000"),
            base_price=Decimal("75000"),
            created_by=uuid4()
        )
        
        trade_value = availability.calculate_estimated_trade_value()
        
        # Should use expected_price (80000), not base_price (75000)
        assert trade_value == Decimal("40000000")  # 500 * 80000
    
    def test_all_risk_fields_initialized(self):
        """Test that all 10 risk fields can be initialized"""
        seller_branch_id = uuid4()
        
        availability = Availability(
            id=uuid4(),
            commodity_id=uuid4(),
            location_id=uuid4(),
            seller_id=uuid4(),
            total_quantity=Decimal("500"),
            available_quantity=Decimal("500"),
            # All 10 risk fields
            expected_price=Decimal("76500"),
            estimated_trade_value=Decimal("38250000"),
            risk_precheck_status="PASS",
            risk_precheck_score=85,
            seller_exposure_after_trade=Decimal("50000000"),
            seller_branch_id=seller_branch_id,
            blocked_for_branches=True,
            seller_rating_score=Decimal("4.5"),
            seller_delivery_score=95,
            risk_flags={"test": "data"},
            created_by=uuid4()
        )
        
        # Verify all fields are set
        assert availability.expected_price == Decimal("76500")
        assert availability.estimated_trade_value == Decimal("38250000")
        assert availability.risk_precheck_status == "PASS"
        assert availability.risk_precheck_score == 85
        assert availability.seller_exposure_after_trade == Decimal("50000000")
        assert availability.seller_branch_id == seller_branch_id
        assert availability.blocked_for_branches is True
        assert availability.seller_rating_score == Decimal("4.5")
        assert availability.seller_delivery_score == 95
        assert availability.risk_flags == {"test": "data"}
