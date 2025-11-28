"""
Test factories for creating valid model instances

These factories handle all required fields for BusinessPartner
to simplify test creation.
"""

from uuid import uuid4
from typing import Dict, Any, Optional

from backend.modules.partners.models import BusinessPartner


def create_business_partner(
    legal_name: str,
    country: str,
    entity_class: str,
    capabilities: Optional[Dict[str, Any]] = None,
    **overrides
) -> BusinessPartner:
    """
    Factory to create valid BusinessPartner instances for testing.
    
    Handles all required fields with sensible defaults.
    
    Args:
        legal_name: Partner's legal name
        country: Country of registration
        entity_class: 'business_entity' or 'service_provider'
        capabilities: CDPS capabilities dict (defaults to empty)
        **overrides: Any additional fields to override defaults
    
    Returns:
        BusinessPartner instance (not saved to DB)
    """
    defaults = {
        'id': uuid4(),
        'legal_name': legal_name,
        'country': country,
        'entity_class': entity_class,
        'capabilities': capabilities or {},
        # Required bank fields
        'bank_account_name': f"{legal_name} Account",
        'bank_name': f"Test Bank {country}",
        'bank_account_number': str(uuid4())[:10],
        'bank_routing_code': f"BANK{country[:3].upper()}",
        # Required address fields
        'primary_address': f"123 Test Street",
        'primary_city': 'Test City',
        'primary_postal_code': '12345',
        'primary_country': country,
        # Required contact fields
        'primary_contact_name': f"{legal_name} Contact",
        'primary_contact_email': f"contact@{legal_name.lower().replace(' ', '')}.com",
        'primary_contact_phone': "+1-555-0100",
        # Required status/entity fields
        'status': 'pending',
        'is_master_entity': False,
        'is_deleted': False,
        'current_employee_count': 0,
        'max_employees_allowed': 2,
    }
    
    # Merge overrides
    defaults.update(overrides)
    
    return BusinessPartner(**defaults)


def create_indian_partner(
    legal_name: str,
    entity_class: str = "business_entity",
    has_capabilities: bool = False,
    **overrides
) -> BusinessPartner:
    """Create Indian business partner with optional capabilities."""
    
    capabilities = {}
    if has_capabilities:
        capabilities = {
            "domestic_buy_india": True,
            "domestic_sell_india": True,
            "domestic_buy_home_country": False,
            "domestic_sell_home_country": False,
            "import_allowed": False,
            "export_allowed": False,
            "auto_detected": True,
            "detected_from_documents": ["GST", "PAN"]
        }
    
    defaults = {
        'tax_id_number': f"29{legal_name[:5].upper()}{str(uuid4())[:4].upper()}F1Z5",  # Mock GST with unique suffix
        'pan_number': f"{legal_name[:5].upper()}{str(uuid4())[:4].upper()}",  # PAN with unique suffix
        'bank_routing_code': 'IFSC0001234',
        'primary_city': 'Mumbai',
        'primary_state': 'Maharashtra',
    }
    defaults.update(overrides)
    
    return create_business_partner(
        legal_name=legal_name,
        country="India",
        entity_class=entity_class,
        capabilities=capabilities,
        **defaults
    )


def create_foreign_partner(
    legal_name: str,
    country: str,
    entity_class: str = "business_entity",
    has_capabilities: bool = False,
    **overrides
) -> BusinessPartner:
    """
    Create foreign business partner.
    
    CRITICAL: Foreign entities can ONLY trade in home country, NOT India.
    """
    
    capabilities = {}
    if has_capabilities:
        capabilities = {
            "domestic_buy_india": False,  # ALWAYS False for foreign entities
            "domestic_sell_india": False,  # ALWAYS False for foreign entities
            "domestic_buy_home_country": True,
            "domestic_sell_home_country": True,
            "import_allowed": True,
            "export_allowed": True,
            "auto_detected": True,
            "detected_from_documents": ["FOREIGN_TAX_ID"]
        }
    
    return create_business_partner(
        legal_name=legal_name,
        country=country,
        entity_class=entity_class,
        capabilities=capabilities,
        **overrides
    )


def create_service_provider(
    legal_name: str,
    service_type: str = "broker",
    country: str = "India",
    **overrides
) -> BusinessPartner:
    """
    Create service provider partner.
    
    Service providers have ALL capabilities = False (cannot trade).
    """
    
    capabilities = {
        "domestic_buy_india": False,
        "domestic_sell_india": False,
        "domestic_buy_home_country": False,
        "domestic_sell_home_country": False,
        "import_allowed": False,
        "export_allowed": False,
        "auto_detected": True
    }
    
    defaults = {
        'service_provider_type': service_type,
    }
    defaults.update(overrides)
    
    return create_business_partner(
        legal_name=legal_name,
        country=country,
        entity_class="service_provider",
        capabilities=capabilities,
        **defaults
    )
