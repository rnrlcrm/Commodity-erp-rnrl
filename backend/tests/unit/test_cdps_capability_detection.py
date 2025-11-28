"""
CDPS Capability Detection Tests

Tests the core capability detection logic including:
- Indian domestic capabilities (GST + PAN)
- Import/Export capabilities (IEC + GST + PAN)
- Foreign entity home country capabilities
- CRITICAL: Foreign entities can ONLY trade in home country, NOT India
- Service providers cannot trade
"""

import pytest
from uuid import uuid4

from backend.tests.unit.factories import (
    create_indian_partner,
    create_foreign_partner,
    create_service_provider
)


class TestCapabilityDetection:
    """Test capability detection via partner capabilities field"""
    
    def test_indian_domestic_capability_structure(self, db_session):
        """
        Test Rule A: Indian entities get domestic_sell_india and domestic_buy_india capabilities
        """
        # Arrange & Act
        partner = create_indian_partner("Test Indian Trader", has_capabilities=True)
        db_session.add(partner)
        db_session.commit()
        db_session.refresh(partner)
        
        # Assert
        assert partner.capabilities is not None
        assert partner.capabilities.get("domestic_sell_india") is True
        assert partner.capabilities.get("domestic_buy_india") is True
        assert partner.capabilities.get("domestic_sell_home_country") is False
        assert partner.capabilities.get("domestic_buy_home_country") is False
    
    def test_import_export_capability_structure(self, db_session):
        """
        Test Rule B: IEC + GST + PAN → import/export capabilities
        """
        # Arrange & Act - Indian partner with capabilities includes import/export
        partner = create_indian_partner("Test Importer Exporter", has_capabilities=True)
        db_session.add(partner)
        db_session.commit()
        db_session.refresh(partner)
        
        # Assert
        assert "import_allowed" in partner.capabilities
        assert "export_allowed" in partner.capabilities
    
    def test_foreign_domestic_capability_home_country_only(self, db_session):
        """
        ⚠️ CRITICAL TEST: Foreign entities get home_country capabilities, NOT India capabilities
        
        Rule C: Foreign entities can ONLY trade domestically in their home country
        """
        # Arrange & Act
        usa_partner = create_foreign_partner(
            "USA Cotton Corp",
            "USA",
            has_capabilities=True
        )
        db_session.add(usa_partner)
        db_session.commit()
        db_session.refresh(usa_partner)
        
        # Assert - Foreign entity has HOME COUNTRY capabilities
        assert usa_partner.capabilities.get("domestic_sell_home_country") is True
        assert usa_partner.capabilities.get("domestic_buy_home_country") is True
        
        # Assert - Foreign entity DOES NOT have India capabilities
        assert usa_partner.capabilities.get("domestic_sell_india") is False
        assert usa_partner.capabilities.get("domestic_buy_india") is False
    
    def test_foreign_entity_india_capabilities_always_false(self, db_session):
        """
        ⚠️ CRITICAL TEST: Foreign entities from ANY country cannot trade in India
        
        Tests multiple foreign countries - all should have India capabilities = False
        """
        # Test multiple countries
        countries = ["USA", "China", "UK", "Germany", "Bangladesh"]
        
        for country in countries:
            partner = create_foreign_partner(
                f"{country} Trading Corp",
                country,
                has_capabilities=True
            )
            db_session.add(partner)
            db_session.commit()
            db_session.refresh(partner)
            
            # Assert - NO India capabilities for any foreign entity
            assert partner.capabilities.get("domestic_sell_india") is False, \
                f"{country} entity should NOT have domestic_sell_india capability"
            assert partner.capabilities.get("domestic_buy_india") is False, \
                f"{country} entity should NOT have domestic_buy_india capability"
            
            # Assert - HAS home country capabilities
            assert partner.capabilities.get("domestic_sell_home_country") is True, \
                f"{country} entity should have domestic_sell_home_country capability"
            assert partner.capabilities.get("domestic_buy_home_country") is True, \
                f"{country} entity should have domestic_buy_home_country capability"
            
            db_session.rollback()
    
    def test_service_providers_cannot_trade(self, db_session):
        """
        Test Rule E: Service providers have ALL capabilities = False
        """
        # Arrange & Act
        broker = create_service_provider("Cotton Broker Services", "broker")
        db_session.add(broker)
        db_session.commit()
        db_session.refresh(broker)
        
        # Assert - All trading capabilities are False
        assert broker.capabilities.get("domestic_sell_india") is False
        assert broker.capabilities.get("domestic_buy_india") is False
        assert broker.capabilities.get("domestic_sell_home_country") is False
        assert broker.capabilities.get("domestic_buy_home_country") is False
        assert broker.capabilities.get("import_allowed") is False
        assert broker.capabilities.get("export_allowed") is False
    
    def test_indian_entity_no_foreign_capabilities(self, db_session):
        """
        Test: Indian entities use India capabilities, not home_country
        """
        # Arrange & Act
        indian_partner = create_indian_partner("Indian Cotton Mills", has_capabilities=True)
        db_session.add(indian_partner)
        db_session.commit()
        db_session.refresh(indian_partner)
        
        # Assert - Indian entity has India capabilities
        assert indian_partner.capabilities.get("domestic_sell_india") is True
        assert indian_partner.capabilities.get("domestic_buy_india") is True
        
        # Assert - Indian entity does NOT use home_country capabilities
        assert indian_partner.capabilities.get("domestic_sell_home_country") is False
        assert indian_partner.capabilities.get("domestic_buy_home_country") is False
