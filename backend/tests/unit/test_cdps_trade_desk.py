"""
CDPS Trade Desk Capability Tests

Tests BusinessPartner capabilities field for trade desk validation:
- Foreign entities have home_country capabilities, NOT India
- Service providers have all trading capabilities = False
- Indian entities have India capabilities
"""

import pytest

from backend.tests.unit.factories import (
    create_indian_partner,
    create_foreign_partner,
    create_service_provider
)


class TestTradeDeskCapabilityIntegration:
    """Test BusinessPartner capabilities for trade desk rules"""
    
    def test_foreign_entity_cannot_post_availability_in_india(self, db_session):
        """
        ⚠️ CRITICAL: Foreign entities cannot sell in India
        domestic_sell_india must be False
        """
        usa_seller = create_foreign_partner("USA Cotton Seller", "USA", has_capabilities=True)
        db_session.add(usa_seller)
        db_session.commit()
        db_session.refresh(usa_seller)
        
        # Foreign entity CANNOT sell in India
        assert usa_seller.capabilities.get("domestic_sell_india") is False
        assert usa_seller.country == "USA"
    
    def test_foreign_entity_can_post_availability_in_home_country(self, db_session):
        """
        Foreign entities CAN sell in home country
        domestic_sell_home_country must be True
        """
        usa_seller = create_foreign_partner("USA Cotton Corp", "USA", has_capabilities=True)
        db_session.add(usa_seller)
        db_session.commit()
        db_session.refresh(usa_seller)
        
        # Foreign entity CAN sell in home country
        assert usa_seller.capabilities.get("domestic_sell_home_country") is True
        assert usa_seller.country == "USA"
    
    def test_foreign_entity_cannot_post_requirement_for_india_delivery(self, db_session):
        """
        ⚠️ CRITICAL: Foreign entities cannot buy in India
        domestic_buy_india must be False
        """
        china_buyer = create_foreign_partner("China Textile Buyer", "China", has_capabilities=True)
        db_session.add(china_buyer)
        db_session.commit()
        db_session.refresh(china_buyer)
        
        # Foreign entity CANNOT buy in India
        assert china_buyer.capabilities.get("domestic_buy_india") is False
        assert china_buyer.country == "China"
    
    def test_service_provider_cannot_post_availability(self, db_session):
        """
        Service providers cannot sell (domestic_sell_india = False)
        """
        broker = create_service_provider("Cotton Broker Services", "broker")
        db_session.add(broker)
        db_session.commit()
        db_session.refresh(broker)
        
        # Service provider CANNOT sell
        assert broker.capabilities.get("domestic_sell_india") is False
        assert broker.capabilities.get("domestic_sell_home_country") is False
    
    def test_service_provider_cannot_post_requirement(self, db_session):
        """
        Service providers cannot buy (domestic_buy_india = False)
        """
        broker = create_service_provider("Cotton Broker LLC", "broker")
        db_session.add(broker)
        db_session.commit()
        db_session.refresh(broker)
        
        # Service provider CANNOT buy
        assert broker.capabilities.get("domestic_buy_india") is False
        assert broker.capabilities.get("domestic_buy_home_country") is False
    
    def test_indian_entity_can_post_in_india(self, db_session):
        """
        Indian entities CAN buy and sell in India
        """
        indian_trader = create_indian_partner("Mumbai Cotton Mills", has_capabilities=True)
        db_session.add(indian_trader)
        db_session.commit()
        db_session.refresh(indian_trader)
        
        # Indian entity CAN trade in India
        assert indian_trader.capabilities.get("domestic_buy_india") is True
        assert indian_trader.capabilities.get("domestic_sell_india") is True
        assert indian_trader.country == "India"
    
    def test_validate_trade_parties_both_sides(self, db_session):
        """
        Test: Both buyer and seller capabilities can be checked
        """
        buyer = create_indian_partner("Buyer Corp", has_capabilities=True)
        seller = create_indian_partner("Seller Corp", has_capabilities=True)
        
        db_session.add(buyer)
        db_session.add(seller)
        db_session.commit()
        db_session.refresh(buyer)
        db_session.refresh(seller)
        
        # Both have appropriate capabilities
        assert buyer.capabilities.get("domestic_buy_india") is True
        assert seller.capabilities.get("domestic_sell_india") is True
    
    def test_indian_entity_without_capability_blocked(self, db_session):
        """
        Test: Indian entity without capabilities has empty/False values
        """
        no_caps_partner = create_indian_partner("Incomplete Partner", has_capabilities=False)
        db_session.add(no_caps_partner)
        db_session.commit()
        db_session.refresh(no_caps_partner)
        
        # No capabilities detected
        assert no_caps_partner.capabilities == {} or \
               no_caps_partner.capabilities.get("domestic_buy_india") is not True
