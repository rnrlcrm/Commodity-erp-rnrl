"""
Country-Specific Validation Service

Validates partner onboarding data based on country-specific requirements.
Ensures compliance with regional regulations and data formats.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, ValidationError


class CountryValidationRule(BaseModel):
    """Country-specific validation rule"""
    country_code: str
    country_name: str
    required_fields: List[str]
    state_required: bool
    postal_code_format: Optional[str] = None
    phone_format: Optional[str] = None
    tax_id_format: Optional[str] = None
    tax_id_name: str  # GST, VAT, EIN, TIN, etc.
    bank_code_format: str  # IFSC, SWIFT, IBAN, Routing


class ValidationResult(BaseModel):
    """Validation result"""
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []


class CountryValidatorService:
    """
    Country-specific validation for partner onboarding.
    
    Features:
    - Required field validation by country
    - Format validation (postal code, phone, tax ID)
    - State/province requirements
    - Bank code format validation
    """
    
    # Country-specific rules
    COUNTRY_RULES = {
        "IN": CountryValidationRule(
            country_code="IN",
            country_name="India",
            required_fields=["state", "pan_number", "tax_id_number"],
            state_required=True,
            postal_code_format=r"^\d{6}$",
            phone_format=r"^\+91\d{10}$",
            tax_id_format=r"^\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}$",
            tax_id_name="GST",
            bank_code_format="IFSC"
        ),
        "US": CountryValidationRule(
            country_code="US",
            country_name="United States",
            required_fields=["state", "tax_id_number"],
            state_required=True,
            postal_code_format=r"^\d{5}(-\d{4})?$",
            phone_format=r"^\+1\d{10}$",
            tax_id_format=r"^\d{2}-\d{7}$",
            tax_id_name="EIN",
            bank_code_format="SWIFT"
        ),
        "GB": CountryValidationRule(
            country_code="GB",
            country_name="United Kingdom",
            required_fields=["tax_id_number"],
            state_required=False,
            postal_code_format=r"^[A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2}$",
            phone_format=r"^\+44\d{10}$",
            tax_id_format=r"^GB\d{9}$",
            tax_id_name="VAT",
            bank_code_format="SWIFT"
        ),
        "CN": CountryValidationRule(
            country_code="CN",
            country_name="China",
            required_fields=["state", "tax_id_number"],
            state_required=True,
            postal_code_format=r"^\d{6}$",
            phone_format=r"^\+86\d{11}$",
            tax_id_format=r"^[A-Z0-9]{15,20}$",
            tax_id_name="TIN",
            bank_code_format="SWIFT"
        ),
        "BD": CountryValidationRule(
            country_code="BD",
            country_name="Bangladesh",
            required_fields=["tax_id_number"],
            state_required=False,
            postal_code_format=r"^\d{4}$",
            phone_format=r"^\+880\d{10}$",
            tax_id_format=r"^\d{12}$",
            tax_id_name="TIN",
            bank_code_format="SWIFT"
        ),
        "PK": CountryValidationRule(
            country_code="PK",
            country_name="Pakistan",
            required_fields=["tax_id_number"],
            state_required=False,
            postal_code_format=r"^\d{5}$",
            phone_format=r"^\+92\d{10}$",
            tax_id_format=r"^\d{7}-\d$",
            tax_id_name="NTN",
            bank_code_format="SWIFT"
        ),
        "AE": CountryValidationRule(
            country_code="AE",
            country_name="United Arab Emirates",
            required_fields=["tax_id_number"],
            state_required=False,
            postal_code_format=None,  # No postal codes in UAE
            phone_format=r"^\+971\d{9}$",
            tax_id_format=r"^\d{15}$",
            tax_id_name="TRN",
            bank_code_format="SWIFT"
        ),
        "AU": CountryValidationRule(
            country_code="AU",
            country_name="Australia",
            required_fields=["state", "tax_id_number"],
            state_required=True,
            postal_code_format=r"^\d{4}$",
            phone_format=r"^\+61\d{9}$",
            tax_id_format=r"^\d{2}\s\d{3}\s\d{3}\s\d{3}$",
            tax_id_name="ABN",
            bank_code_format="SWIFT"
        ),
    }
    
    def validate_onboarding_data(
        self,
        country: str,
        data: Dict
    ) -> ValidationResult:
        """
        Validate onboarding data against country-specific rules.
        
        Args:
            country: Country code (ISO 2-letter) or name
            data: Onboarding data dictionary
        
        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []
        
        # Get country rule
        country_code = self._normalize_country_code(country)
        rule = self.COUNTRY_RULES.get(country_code)
        
        if not rule:
            # Unknown country - apply generic validation
            warnings.append(f"Country '{country}' not in validation rules. Using generic validation.")
            return ValidationResult(valid=True, warnings=warnings)
        
        # Check required fields
        for field in rule.required_fields:
            if field not in data or not data.get(field):
                errors.append(f"Field '{field}' is required for {rule.country_name}")
        
        # Validate state if required
        if rule.state_required and not data.get("primary_state"):
            errors.append(f"State/Province is required for {rule.country_name}")
        
        # Validate postal code format
        if rule.postal_code_format and data.get("primary_postal_code"):
            import re
            if not re.match(rule.postal_code_format, data["primary_postal_code"]):
                errors.append(
                    f"Invalid postal code format for {rule.country_name}. "
                    f"Expected pattern: {rule.postal_code_format}"
                )
        
        # Validate phone format
        if rule.phone_format and data.get("primary_contact_phone"):
            import re
            if not re.match(rule.phone_format, data["primary_contact_phone"]):
                warnings.append(
                    f"Phone number format may be invalid for {rule.country_name}. "
                    f"Expected format: {rule.phone_format}"
                )
        
        # Validate tax ID format
        if rule.tax_id_format and data.get("tax_id_number"):
            import re
            if not re.match(rule.tax_id_format, data["tax_id_number"]):
                errors.append(
                    f"Invalid {rule.tax_id_name} format for {rule.country_name}. "
                    f"Expected pattern: {rule.tax_id_format}"
                )
        
        # Validate bank code format
        if data.get("bank_routing_code"):
            if rule.bank_code_format == "IFSC" and country_code == "IN":
                import re
                if not re.match(r"^[A-Z]{4}0[A-Z0-9]{6}$", data["bank_routing_code"]):
                    errors.append("Invalid IFSC code format for India")
            elif rule.bank_code_format == "SWIFT":
                import re
                if not re.match(r"^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$", data["bank_routing_code"]):
                    warnings.append("Bank code should be valid SWIFT/BIC code")
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def get_country_requirements(self, country: str) -> Dict:
        """
        Get country-specific requirements for UI guidance.
        
        Args:
            country: Country code or name
        
        Returns:
            Dict with country requirements
        """
        country_code = self._normalize_country_code(country)
        rule = self.COUNTRY_RULES.get(country_code)
        
        if not rule:
            return {
                "country": country,
                "requirements": "Generic requirements apply",
                "tax_id_name": "Tax ID",
                "state_required": False
            }
        
        return {
            "country": rule.country_name,
            "country_code": rule.country_code,
            "required_fields": rule.required_fields,
            "state_required": rule.state_required,
            "tax_id_name": rule.tax_id_name,
            "tax_id_format": rule.tax_id_format,
            "postal_code_format": rule.postal_code_format,
            "phone_format": rule.phone_format,
            "bank_code_format": rule.bank_code_format,
            "example_postal_code": self._get_example_postal_code(country_code),
            "example_phone": self._get_example_phone(country_code),
            "example_tax_id": self._get_example_tax_id(country_code)
        }
    
    def _normalize_country_code(self, country: str) -> str:
        """Convert country name to 2-letter code"""
        country = country.upper().strip()
        
        # If already 2-letter code, return as is
        if len(country) == 2:
            return country
        
        # Map common country names
        name_to_code = {
            "INDIA": "IN",
            "UNITED STATES": "US",
            "USA": "US",
            "UNITED KINGDOM": "GB",
            "UK": "GB",
            "CHINA": "CN",
            "BANGLADESH": "BD",
            "PAKISTAN": "PK",
            "UAE": "AE",
            "UNITED ARAB EMIRATES": "AE",
            "AUSTRALIA": "AU",
        }
        
        return name_to_code.get(country, country[:2])
    
    def _get_example_postal_code(self, country_code: str) -> str:
        """Get example postal code for country"""
        examples = {
            "IN": "400001",
            "US": "10001 or 10001-1234",
            "GB": "SW1A 1AA",
            "CN": "100000",
            "BD": "1000",
            "PK": "44000",
            "AE": "N/A (No postal codes)",
            "AU": "2000"
        }
        return examples.get(country_code, "Varies by country")
    
    def _get_example_phone(self, country_code: str) -> str:
        """Get example phone number for country"""
        examples = {
            "IN": "+919876543210",
            "US": "+12125551234",
            "GB": "+442071234567",
            "CN": "+8613800138000",
            "BD": "+8801712345678",
            "PK": "+923001234567",
            "AE": "+971501234567",
            "AU": "+61412345678"
        }
        return examples.get(country_code, "+CountryCode...")
    
    def _get_example_tax_id(self, country_code: str) -> str:
        """Get example tax ID for country"""
        examples = {
            "IN": "27AABCD1234E1Z5 (GST)",
            "US": "12-3456789 (EIN)",
            "GB": "GB123456789 (VAT)",
            "CN": "ABCD123456789012345 (TIN)",
            "BD": "123456789012 (TIN)",
            "PK": "1234567-8 (NTN)",
            "AE": "123456789012345 (TRN)",
            "AU": "12 345 678 901 (ABN)"
        }
        return examples.get(country_code, "Varies by country")
