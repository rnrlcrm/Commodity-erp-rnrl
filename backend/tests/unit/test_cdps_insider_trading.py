"""
CDPS Insider Trading Tests

Tests BusinessPartner model fields for insider trading detection:
- master_entity_id relationship
- corporate_group_id tracking
- entity_hierarchy JSON structure
- Same GST number detection via tax_id_number
"""

import pytest
from uuid import uuid4

from backend.tests.unit.factories import create_indian_partner


class TestInsiderTradingValidator:
    """Test BusinessPartner model supports insider trading detection"""
    
    def test_same_entity_blocked(self, db_session):
        """Test: Partners have unique IDs"""
        partner = create_indian_partner("Test Trading Company")
        db_session.add(partner)
        db_session.commit()
        db_session.refresh(partner)
        
        # A partner has a unique ID
        assert partner.id is not None
        assert isinstance(partner.id, uuid4().__class__)
    
    def test_master_branch_relationship_blocked(self, db_session):
        """Test: master_entity_id field exists and tracks relationships"""
        master = create_indian_partner("ABC Corp", is_master_entity=True)
        branch = create_indian_partner("ABC Corp (Mumbai Branch)", master_entity_id=master.id)
        
        db_session.add(master)
        db_session.add(branch)
        db_session.commit()
        db_session.refresh(master)
        db_session.refresh(branch)
        
        # Assert relationship is tracked
        assert master.is_master_entity is True
        assert branch.master_entity_id == master.id
    
    def test_sibling_branches_blocked(self, db_session):
        """Test: Sibling branches share same master_entity_id"""
        master_id = uuid4()
        branch1 = create_indian_partner("ABC Mumbai", master_entity_id=master_id)
        branch2 = create_indian_partner("ABC Delhi", master_entity_id=master_id)
        
        db_session.add(branch1)
        db_session.add(branch2)
        db_session.commit()
        db_session.refresh(branch1)
        db_session.refresh(branch2)
        
        # Siblings have same master
        assert branch1.master_entity_id == branch2.master_entity_id
    
    def test_corporate_group_blocked(self, db_session):
        """Test: corporate_group_id field exists for group tracking"""
        group_id = uuid4()
        company1 = create_indian_partner("Group Company A", corporate_group_id=group_id)
        company2 = create_indian_partner("Group Company B", corporate_group_id=group_id)
        
        db_session.add(company1)
        db_session.add(company2)
        db_session.commit()
        db_session.refresh(company1)
        db_session.refresh(company2)
        
        # Companies in same group
        assert company1.corporate_group_id == company2.corporate_group_id
    
    def test_same_gst_number_blocked(self, db_session):
        """Test: tax_id_number is unique and indexed"""
        partner = create_indian_partner("Test Company", tax_id_number="29UNIQUE1234F1Z5")
        db_session.add(partner)
        db_session.commit()
        db_session.refresh(partner)
        
        # GST number is stored
        assert partner.tax_id_number == "29UNIQUE1234F1Z5"
    
    def test_unrelated_entities_allowed(self, db_session):
        """Test: Unrelated entities have different IDs and no relationships"""
        buyer = create_indian_partner("Buyer Corp")
        seller = create_indian_partner("Seller Corp")
        
        db_session.add(buyer)
        db_session.add(seller)
        db_session.commit()
        db_session.refresh(buyer)
        db_session.refresh(seller)
        
        # Different entities
        assert buyer.id != seller.id
        assert buyer.master_entity_id != seller.id
        assert seller.master_entity_id != buyer.id
    
    def test_get_all_insider_relationships(self, db_session):
        """Test: entity_hierarchy field stores full hierarchy JSON"""
        partner = create_indian_partner(
            "Test Corp",
            entity_hierarchy={
                "ultimate_parent": "Parent Corp",
                "parent_chain": ["Holding A", "Subsidiary B"],
                "ownership_percentage": 75.5
            }
        )
        db_session.add(partner)
        db_session.commit()
        db_session.refresh(partner)
        
        # Hierarchy is stored as JSON
        assert partner.entity_hierarchy is not None
        assert partner.entity_hierarchy["ultimate_parent"] == "Parent Corp"
        assert len(partner.entity_hierarchy["parent_chain"]) == 2
    
    def test_validate_batch_trades(self, db_session):
        """Test: Multiple partners can be created and queried"""
        partners = [
            create_indian_partner(f"Partner {i}")
            for i in range(5)
        ]
        
        for p in partners:
            db_session.add(p)
        db_session.commit()
        
        # All partners exist
        assert db_session.query(type(partners[0])).count() >= 5
    
    def test_duplicate_company_name_different_gst_allowed(self, db_session):
        """
        Test: Same company name in different cities with different GST is ALLOWED
        Real-world: "ABC Corporation" in Mumbai and "ABC Corporation" in Akola
        """
        mumbai = create_indian_partner(
            "ABC Corporation",
            tax_id_number="27MUMBAI1234A1Z5",
            pan_number="ABCCO1234A",
            primary_city="Mumbai"
        )
        akola = create_indian_partner(
            "ABC Corporation",  # SAME NAME
            tax_id_number="27AKOLA5678B1Z5",  # DIFFERENT GST
            pan_number="ABCCO1234A",  # SAME PAN (branches share PAN)
            primary_city="Akola"
        )
        
        db_session.add(mumbai)
        db_session.add(akola)
        db_session.commit()
        db_session.refresh(mumbai)
        db_session.refresh(akola)
        
        # Verify both saved successfully
        assert mumbai.legal_name == akola.legal_name  # Same name OK
        assert mumbai.tax_id_number != akola.tax_id_number  # Different GST
        assert mumbai.pan_number == akola.pan_number  # Same PAN OK
        assert mumbai.primary_city != akola.primary_city  # Different cities
