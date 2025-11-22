"""
Business Partners Module

External companies (buyers, sellers, brokers, transporters) that interact with the system.
This is a minimal model providing the FK foundation for data isolation.
"""

from backend.modules.settings.business_partners.models import BusinessPartner

__all__ = ['BusinessPartner']
