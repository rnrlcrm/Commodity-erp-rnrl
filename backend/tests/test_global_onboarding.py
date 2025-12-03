"""
Tests for Global Onboarding Enhancement Services

Tests country validation, currency conversion, and compliance checking.
"""

import pytest
from decimal import Decimal
from datetime import datetime

from backend.core.global_services.country_validator import CountryValidatorService, ValidationResult
from backend.core.global_services.currency_converter import CurrencyConversionService, ExchangeRate
from backend.core.global_services.compliance_checker import (
    ComplianceCheckerService,
    ComplianceStatus,
    ComplianceReport
)


class TestCountryValidator:
    """Test country-specific validation"""
    
    @pytest.fixture
    def validator(self):
        return CountryValidatorService()
    
    def test_india_validation_success(self, validator):
        """Test valid Indian partner data"""
        data = {
            "primary_state": "Maharashtra",
            "state": "Maharashtra",
            "primary_postal_code": "400001",
            "primary_contact_phone": "+919876543210",
            "tax_id_number": "27AABCD1234E1Z5",
            "pan_number": "ABCDE1234F",
            "bank_routing_code": "SBIN0001234"
        }
        
        result = validator.validate_onboarding_data("IN", data)
        
        assert result.valid is True
        assert len(result.errors) == 0
    
    def test_india_missing_state(self, validator):
        """Test Indian validation fails without state"""
        data = {
            "primary_postal_code": "400001",
            "tax_id_number": "27AABCD1234E1Z5"
        }
        
        result = validator.validate_onboarding_data("IN", data)
        
        assert result.valid is False
        assert any("State" in error for error in result.errors)
    
    def test_usa_validation_success(self, validator):
        """Test valid USA partner data"""
        data = {
            "primary_state": "New York",
            "state": "New York",
            "primary_postal_code": "10001",
            "primary_contact_phone": "+12125551234",
            "tax_id_number": "12-3456789",
            "bank_routing_code": "SBINUS33XXX"
        }
        
        result = validator.validate_onboarding_data("US", data)
        
        assert result.valid is True
    
    def test_usa_invalid_postal_code(self, validator):
        """Test USA validation fails with invalid ZIP"""
        data = {
            "primary_state": "New York",
            "primary_postal_code": "1234",  # Invalid
            "tax_id_number": "12-3456789"
        }
        
        result = validator.validate_onboarding_data("US", data)
        
        assert result.valid is False
        assert any("postal code" in error.lower() for error in result.errors)
    
    def test_uk_validation_no_state_required(self, validator):
        """Test UK validation - state not required"""
        data = {
            "primary_postal_code": "SW1A 1AA",
            "tax_id_number": "GB123456789",
            "bank_routing_code": "BARCGB22XXX"
        }
        
        result = validator.validate_onboarding_data("GB", data)
        
        assert result.valid is True
    
    def test_get_country_requirements_india(self, validator):
        """Test getting India requirements"""
        reqs = validator.get_country_requirements("IN")
        
        assert reqs["country_code"] == "IN"
        assert reqs["state_required"] is True
        assert reqs["tax_id_name"] == "GST"
        assert "state" in reqs["required_fields"]
    
    def test_get_country_requirements_usa(self, validator):
        """Test getting USA requirements"""
        reqs = validator.get_country_requirements("US")
        
        assert reqs["country_code"] == "US"
        assert reqs["state_required"] is True
        assert reqs["tax_id_name"] == "EIN"
        assert "12-3456789" in reqs["example_tax_id"]
    
    def test_unknown_country_fallback(self, validator):
        """Test validation for unknown country uses generic rules"""
        data = {
            "primary_postal_code": "12345",
            "tax_id_number": "ABC123"
        }
        
        result = validator.validate_onboarding_data("ZZ", data)
        
        assert result.valid is True
        assert len(result.warnings) > 0
        assert "not in validation rules" in result.warnings[0]


class TestCurrencyConverter:
    """Test currency conversion service"""
    
    @pytest.fixture
    def converter(self):
        return CurrencyConversionService()
    
    @pytest.mark.asyncio
    async def test_same_currency_conversion(self, converter):
        """Test converting same currency returns 1.0"""
        rate = await converter.get_rate("USD", "USD")
        
        assert rate.base_currency == "USD"
        assert rate.target_currency == "USD"
        assert rate.rate == Decimal("1.0")
    
    @pytest.mark.asyncio
    async def test_static_rate_fallback(self, converter):
        """Test fallback to static rates when API fails"""
        # This will use static rates since we don't have valid API key
        rate = await converter.get_rate("USD", "INR", use_cache=False)
        
        assert rate.base_currency == "USD"
        assert rate.target_currency == "INR"
        assert rate.rate > Decimal("50")  # INR is typically 70-90 per USD
    
    @pytest.mark.asyncio
    async def test_convert_amount(self, converter):
        """Test converting amount"""
        amount = Decimal("100.00")
        converted = await converter.convert(amount, "USD", "USD")
        
        assert converted == amount
    
    @pytest.mark.asyncio
    async def test_batch_conversion(self, converter):
        """Test batch currency conversion"""
        amounts = {
            "USD": Decimal("100.00"),
            "EUR": Decimal("100.00"),
            "GBP": Decimal("100.00")
        }
        
        results = await converter.convert_batch(amounts, "USD")
        
        assert "USD" in results
        assert "EUR" in results
        assert "GBP" in results
        assert results["USD"] == Decimal("100.00")  # Same currency
    
    def test_multi_currency_summary(self, converter):
        """Test multi-currency summary generation"""
        amounts = {
            "USD": Decimal("1000.00"),
            "EUR": Decimal("1000.00")
        }
        converted = {
            "USD": Decimal("1000.00"),
            "EUR": Decimal("1086.96")  # ~1.087 rate
        }
        
        summary = converter.get_multi_currency_summary(amounts, converted, "USD")
        
        assert summary["target_currency"] == "USD"
        assert summary["total_amount"] == 2086.96
        assert len(summary["breakdown"]) == 2
    
    def test_cache_operations(self, converter):
        """Test cache clear and stats"""
        converter.clear_cache()
        stats = converter.get_cache_stats()
        
        assert stats["total_entries"] == 0
        assert stats["supported_currencies"] > 20
    
    @pytest.mark.asyncio
    async def test_unsupported_currency_error(self, converter):
        """Test error raised for unsupported currency"""
        with pytest.raises(ValueError, match="Unsupported.*currency"):
            await converter.get_rate("USD", "XXX")


class TestComplianceChecker:
    """Test compliance checking service"""
    
    @pytest.fixture
    def checker(self):
        return ComplianceCheckerService()
    
    def test_india_exporter_compliant(self, checker):
        """Test compliant Indian exporter"""
        report = checker.check_compliance(
            country="IN",
            partner_type="exporter",
            submitted_documents=[
                "GST Certificate", 
                "IEC Certificate", 
                "PAN Card",
                "Export Compliance"  # Partner type specific doc
            ],
            tax_id_number="27AABCD1234E1Z5"
        )
        
        assert report.overall_status == ComplianceStatus.COMPLIANT
        assert report.country == "IN"
        assert report.partner_type == "exporter"
        assert len(report.missing_documents) == 0
    
    def test_india_exporter_missing_iec(self, checker):
        """Test Indian exporter without IEC is non-compliant"""
        report = checker.check_compliance(
            country="IN",
            partner_type="exporter",
            submitted_documents=["GST Certificate", "PAN Card"],
            tax_id_number="27AABCD1234E1Z5"
        )
        
        assert report.overall_status == ComplianceStatus.NON_COMPLIANT
        assert "IEC Certificate" in report.missing_documents
    
    def test_india_financer_no_gst_required(self, checker):
        """Test Indian financer exempted from GST"""
        report = checker.check_compliance(
            country="IN",
            partner_type="financer",
            submitted_documents=["PAN Card", "NBFC Certificate"]
        )
        
        # Find GST check
        gst_check = next((c for c in report.checks if "GST" in c.check_name), None)
        assert gst_check is not None
        assert gst_check.status == ComplianceStatus.EXEMPTED
    
    def test_usa_exporter_requirements(self, checker):
        """Test USA exporter compliance"""
        report = checker.check_compliance(
            country="US",
            partner_type="exporter",
            submitted_documents=["EIN Letter", "Business License", "Export License"],
            tax_id_number="12-3456789"
        )
        
        assert report.overall_status == ComplianceStatus.COMPLIANT
    
    def test_uk_gdpr_required_for_all(self, checker):
        """Test GDPR required for all UK partners"""
        report = checker.check_compliance(
            country="GB",
            partner_type="trader",
            submitted_documents=["VAT Certificate", "GDPR Policy"],
            tax_id_number="GB123456789"
        )
        
        gdpr_check = next((c for c in report.checks if "GDPR" in c.check_name), None)
        assert gdpr_check is not None
        assert gdpr_check.required is True
    
    def test_get_required_documents_india_importer(self, checker):
        """Test getting required documents for Indian importer"""
        docs = checker.get_required_documents("IN", "importer")
        
        assert "GST Certificate" in docs
        assert "IEC Certificate" in docs
        assert "PAN Card" in docs
        assert "NBFC Certificate" not in docs  # Only for financers
    
    def test_get_compliance_checklist_usa_financer(self, checker):
        """Test compliance checklist for USA financer"""
        checklist = checker.get_compliance_checklist("US", "financer")
        
        assert checklist["country"] == "US"
        assert checklist["partner_type"] == "financer"
        assert len(checklist["required_checks"]) > 0
        
        # Should have financial license check
        check_names = [c["name"] for c in checklist["required_checks"]]
        assert any("Financial License" in name for name in check_names)
    
    def test_bangladesh_irc_for_importer_only(self, checker):
        """Test Bangladesh IRC required for importers only"""
        # Importer - should require IRC
        importer_report = checker.check_compliance(
            country="BD",
            partner_type="importer",
            submitted_documents=["TIN Certificate", "IRC Certificate"]
        )
        
        irc_check = next((c for c in importer_report.checks if "IRC" in c.check_name), None)
        assert irc_check is not None
        assert irc_check.required is True
        
        # Exporter - IRC exempted
        exporter_report = checker.check_compliance(
            country="BD",
            partner_type="exporter",
            submitted_documents=["TIN Certificate"]
        )
        
        irc_check = next((c for c in exporter_report.checks if "IRC" in c.check_name), None)
        assert irc_check is not None
        assert irc_check.status == ComplianceStatus.EXEMPTED
    
    def test_partner_type_specific_checks(self, checker):
        """Test partner type checks apply regardless of country"""
        report = checker.check_compliance(
            country="IN",
            partner_type="financer",
            submitted_documents=["PAN Card", "NBFC Certificate"]
        )
        
        # Should have KYC and AML checks for financer
        check_names = [c.check_name for c in report.checks]
        assert any("KYC" in name for name in check_names)
        assert any("AML" in name for name in check_names)
    
    def test_overall_status_pending_review(self, checker):
        """Test pending review status"""
        report = checker.check_compliance(
            country="IN",
            partner_type="exporter",
            submitted_documents=["GST Certificate", "IEC Certificate"]
            # Missing PAN Card - required
        )
        
        # Should be non-compliant due to missing required doc
        assert report.overall_status == ComplianceStatus.NON_COMPLIANT


class TestIntegration:
    """Integration tests combining all three services"""
    
    @pytest.fixture
    def validator(self):
        return CountryValidatorService()
    
    @pytest.fixture
    def converter(self):
        return CurrencyConversionService()
    
    @pytest.fixture
    def checker(self):
        return ComplianceCheckerService()
    
    def test_complete_india_exporter_validation(self, validator, checker):
        """Test complete validation flow for Indian exporter"""
        # Step 1: Validate data format
        data = {
            "primary_state": "Maharashtra",
            "state": "Maharashtra",
            "primary_postal_code": "400001",
            "tax_id_number": "27AABCD1234E1Z5",
            "pan_number": "ABCDE1234F",
            "bank_routing_code": "SBIN0001234"
        }
        
        validation = validator.validate_onboarding_data("IN", data)
        assert validation.valid is True
        
        # Step 2: Check compliance
        compliance = checker.check_compliance(
            country="IN",
            partner_type="exporter",
            submitted_documents=[
                "GST Certificate", 
                "IEC Certificate", 
                "PAN Card",
                "Export Compliance"
            ],
            tax_id_number=data["tax_id_number"]
        )
        
        assert compliance.overall_status == ComplianceStatus.COMPLIANT
    
    @pytest.mark.asyncio
    async def test_complete_usa_exporter_with_currency(self, validator, converter, checker):
        """Test USA exporter with currency conversion"""
        # Step 1: Validate
        data = {
            "primary_state": "California",
            "state": "California",
            "primary_postal_code": "90001",
            "tax_id_number": "12-3456789"
        }
        
        validation = validator.validate_onboarding_data("US", data)
        assert validation.valid is True
        
        # Step 2: Check compliance
        compliance = checker.check_compliance(
            country="US",
            partner_type="exporter",
            submitted_documents=["EIN Letter", "Business License", "Export License"],
            tax_id_number=data["tax_id_number"]
        )
        
        assert compliance.overall_status == ComplianceStatus.COMPLIANT
        
        # Step 3: Convert currency for reporting
        trade_value_usd = Decimal("50000.00")
        inr_value = await converter.convert(trade_value_usd, "USD", "INR")
        
        assert inr_value > Decimal("1000000")  # Should be >1M INR
    
    def test_country_requirements_with_compliance_checklist(self, validator, checker):
        """Test getting requirements and checklist together"""
        country = "IN"
        partner_type = "importer"
        
        # Get validation requirements
        val_reqs = validator.get_country_requirements(country)
        
        # Get compliance checklist
        comp_checklist = checker.get_compliance_checklist(country, partner_type)
        
        # Both should have consistent country info
        assert val_reqs["country_code"] == comp_checklist["country"]
        
        # Should have required documents
        assert len(comp_checklist["required_documents"]) > 0
