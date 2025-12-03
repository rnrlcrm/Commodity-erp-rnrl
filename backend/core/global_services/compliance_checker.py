"""
Automated Compliance Checker Service

Validates partner compliance based on country and partner type.
Enforces regulatory requirements for global cotton trade.
"""

from typing import Dict, List, Optional
from enum import Enum
from pydantic import BaseModel
from datetime import datetime


class ComplianceStatus(str, Enum):
    """Compliance status"""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    EXEMPTED = "exempted"


class ComplianceCheck(BaseModel):
    """Single compliance check result"""
    check_name: str
    description: str
    status: ComplianceStatus
    required: bool
    details: Optional[str] = None
    remediation: Optional[str] = None


class ComplianceReport(BaseModel):
    """Complete compliance report"""
    partner_id: Optional[int] = None
    country: str
    partner_type: str
    overall_status: ComplianceStatus
    checks: List[ComplianceCheck]
    missing_documents: List[str]
    timestamp: datetime


class ComplianceCheckerService:
    """
    Automated compliance checking for global partner onboarding.
    
    Features:
    - Country-specific regulations (GDPR, tax, licenses)
    - Partner-type specific checks (importer IEC, financer NBFC)
    - Document requirement validation
    - Automated compliance scoring
    - Remediation guidance
    """
    
    # Country-specific compliance rules
    COUNTRY_COMPLIANCE = {
        "IN": {
            "name": "India",
            "checks": [
                {
                    "name": "GST Registration",
                    "description": "Valid GST number required for Indian entities",
                    "required_for": ["exporter", "importer", "trader"],
                    "exempted_for": ["financer"],
                    "document": "GST Certificate"
                },
                {
                    "name": "IEC Code",
                    "description": "Import Export Code required for import/export",
                    "required_for": ["exporter", "importer"],
                    "exempted_for": ["financer", "trader"],
                    "document": "IEC Certificate"
                },
                {
                    "name": "PAN Card",
                    "description": "Permanent Account Number required for all entities",
                    "required_for": ["exporter", "importer", "trader", "financer"],
                    "exempted_for": [],
                    "document": "PAN Card"
                },
                {
                    "name": "NBFC License",
                    "description": "RBI license for financial services",
                    "required_for": ["financer"],
                    "exempted_for": ["exporter", "importer", "trader"],
                    "document": "NBFC Certificate"
                }
            ]
        },
        "US": {
            "name": "United States",
            "checks": [
                {
                    "name": "EIN Registration",
                    "description": "Employer Identification Number required",
                    "required_for": ["exporter", "importer", "trader", "financer"],
                    "exempted_for": [],
                    "document": "EIN Letter"
                },
                {
                    "name": "Business License",
                    "description": "State business license required",
                    "required_for": ["exporter", "importer", "trader"],
                    "exempted_for": [],
                    "document": "Business License"
                },
                {
                    "name": "Export License",
                    "description": "ITAR/EAR compliance for exports",
                    "required_for": ["exporter"],
                    "exempted_for": ["importer", "trader", "financer"],
                    "document": "Export License"
                }
            ]
        },
        "GB": {
            "name": "United Kingdom",
            "checks": [
                {
                    "name": "VAT Registration",
                    "description": "VAT number required for UK businesses",
                    "required_for": ["exporter", "importer", "trader"],
                    "exempted_for": ["financer"],
                    "document": "VAT Certificate"
                },
                {
                    "name": "GDPR Compliance",
                    "description": "Data protection compliance required",
                    "required_for": ["exporter", "importer", "trader", "financer"],
                    "exempted_for": [],
                    "document": "GDPR Policy"
                },
                {
                    "name": "EORI Number",
                    "description": "Economic Operator Registration for customs",
                    "required_for": ["exporter", "importer"],
                    "exempted_for": ["trader", "financer"],
                    "document": "EORI Certificate"
                }
            ]
        },
        "CN": {
            "name": "China",
            "checks": [
                {
                    "name": "Business License",
                    "description": "Chinese business license required",
                    "required_for": ["exporter", "importer", "trader"],
                    "exempted_for": [],
                    "document": "Business License"
                },
                {
                    "name": "Import/Export License",
                    "description": "Customs registration certificate",
                    "required_for": ["exporter", "importer"],
                    "exempted_for": ["trader", "financer"],
                    "document": "Import/Export License"
                }
            ]
        },
        "AE": {
            "name": "United Arab Emirates",
            "checks": [
                {
                    "name": "Trade License",
                    "description": "Dubai/Abu Dhabi trade license required",
                    "required_for": ["exporter", "importer", "trader"],
                    "exempted_for": [],
                    "document": "Trade License"
                },
                {
                    "name": "TRN Registration",
                    "description": "Tax Registration Number for VAT",
                    "required_for": ["exporter", "importer", "trader", "financer"],
                    "exempted_for": [],
                    "document": "TRN Certificate"
                }
            ]
        },
        "BD": {
            "name": "Bangladesh",
            "checks": [
                {
                    "name": "TIN Certificate",
                    "description": "Tax Identification Number required",
                    "required_for": ["exporter", "importer", "trader", "financer"],
                    "exempted_for": [],
                    "document": "TIN Certificate"
                },
                {
                    "name": "IRC License",
                    "description": "Import Registration Certificate",
                    "required_for": ["importer"],
                    "exempted_for": ["exporter", "trader", "financer"],
                    "document": "IRC Certificate"
                }
            ]
        },
        "PK": {
            "name": "Pakistan",
            "checks": [
                {
                    "name": "NTN Registration",
                    "description": "National Tax Number required",
                    "required_for": ["exporter", "importer", "trader", "financer"],
                    "exempted_for": [],
                    "document": "NTN Certificate"
                },
                {
                    "name": "Sales Tax Registration",
                    "description": "Sales tax registration for businesses",
                    "required_for": ["exporter", "importer", "trader"],
                    "exempted_for": ["financer"],
                    "document": "Sales Tax Certificate"
                }
            ]
        }
    }
    
    # Partner type specific checks (applicable globally)
    PARTNER_TYPE_CHECKS = {
        "exporter": [
            {
                "name": "Export Compliance",
                "description": "Compliance with export regulations",
                "required": True
            },
            {
                "name": "Quality Certifications",
                "description": "BCI, GOTS, or other quality certifications",
                "required": False
            }
        ],
        "importer": [
            {
                "name": "Import Compliance",
                "description": "Compliance with import regulations",
                "required": True
            },
            {
                "name": "Customs Bond",
                "description": "Customs bond for import duties",
                "required": False
            }
        ],
        "financer": [
            {
                "name": "Financial License",
                "description": "Valid financial services license",
                "required": True
            },
            {
                "name": "KYC Compliance",
                "description": "Know Your Customer compliance",
                "required": True
            },
            {
                "name": "AML Compliance",
                "description": "Anti-Money Laundering compliance",
                "required": True
            }
        ],
        "trader": [
            {
                "name": "Trading License",
                "description": "Valid commodity trading license",
                "required": True
            }
        ]
    }
    
    def check_compliance(
        self,
        country: str,
        partner_type: str,
        submitted_documents: List[str],
        tax_id_number: Optional[str] = None,
        business_license_number: Optional[str] = None
    ) -> ComplianceReport:
        """
        Run automated compliance checks for partner.
        
        Args:
            country: Country code (IN, US, GB, etc.)
            partner_type: exporter, importer, trader, financer
            submitted_documents: List of document types submitted
            tax_id_number: Tax ID if available
            business_license_number: Business license if available
        
        Returns:
            ComplianceReport with all checks
        """
        country = country.upper()
        partner_type = partner_type.lower()
        
        checks = []
        missing_documents = []
        
        # Country-specific checks
        country_rules = self.COUNTRY_COMPLIANCE.get(country)
        if country_rules:
            for rule in country_rules["checks"]:
                check = self._run_country_check(
                    rule,
                    partner_type,
                    submitted_documents,
                    tax_id_number,
                    business_license_number
                )
                checks.append(check)
                
                if check.status == ComplianceStatus.NON_COMPLIANT and check.required:
                    if rule["document"] not in submitted_documents:
                        missing_documents.append(rule["document"])
        
        # Partner type specific checks
        type_checks = self.PARTNER_TYPE_CHECKS.get(partner_type, [])
        for rule in type_checks:
            check = self._run_type_check(rule, submitted_documents)
            checks.append(check)
        
        # Determine overall status
        overall_status = self._calculate_overall_status(checks)
        
        return ComplianceReport(
            country=country,
            partner_type=partner_type,
            overall_status=overall_status,
            checks=checks,
            missing_documents=missing_documents,
            timestamp=datetime.utcnow()
        )
    
    def _run_country_check(
        self,
        rule: Dict,
        partner_type: str,
        submitted_docs: List[str],
        tax_id: Optional[str],
        license: Optional[str]
    ) -> ComplianceCheck:
        """Run single country compliance check"""
        
        # Check if exempted
        if partner_type in rule["exempted_for"]:
            return ComplianceCheck(
                check_name=rule["name"],
                description=rule["description"],
                status=ComplianceStatus.EXEMPTED,
                required=False,
                details=f"Exempted for {partner_type}"
            )
        
        # Check if required
        required = partner_type in rule["required_for"]
        
        # Check document submission
        doc_submitted = rule["document"] in submitted_docs
        
        # Special checks
        if rule["name"] == "GST Registration" and tax_id:
            # GST number provided
            status = ComplianceStatus.COMPLIANT
            details = "GST number provided"
        elif rule["name"] == "EIN Registration" and tax_id:
            status = ComplianceStatus.COMPLIANT
            details = "EIN provided"
        elif rule["name"] == "VAT Registration" and tax_id:
            status = ComplianceStatus.COMPLIANT
            details = "VAT number provided"
        elif doc_submitted:
            status = ComplianceStatus.COMPLIANT
            details = f"{rule['document']} submitted"
        elif required:
            status = ComplianceStatus.NON_COMPLIANT
            details = f"{rule['document']} not submitted"
        else:
            status = ComplianceStatus.PENDING_REVIEW
            details = "Optional document not submitted"
        
        # Remediation
        remediation = None
        if status == ComplianceStatus.NON_COMPLIANT:
            remediation = f"Please upload {rule['document']}"
        
        return ComplianceCheck(
            check_name=rule["name"],
            description=rule["description"],
            status=status,
            required=required,
            details=details,
            remediation=remediation
        )
    
    def _run_type_check(
        self,
        rule: Dict,
        submitted_docs: List[str]
    ) -> ComplianceCheck:
        """Run partner type specific check"""
        
        # Simplified check - assume compliant if any relevant doc submitted
        doc_keywords = rule["name"].lower().split()
        relevant_docs = [
            doc for doc in submitted_docs
            if any(keyword in doc.lower() for keyword in doc_keywords)
        ]
        
        if relevant_docs:
            status = ComplianceStatus.COMPLIANT
            details = f"Documents submitted: {', '.join(relevant_docs)}"
            remediation = None
        elif rule["required"]:
            status = ComplianceStatus.NON_COMPLIANT
            details = "Required check not satisfied"
            remediation = f"Please ensure {rule['name']} requirements are met"
        else:
            status = ComplianceStatus.PENDING_REVIEW
            details = "Optional check pending review"
            remediation = None
        
        return ComplianceCheck(
            check_name=rule["name"],
            description=rule["description"],
            status=status,
            required=rule["required"],
            details=details,
            remediation=remediation
        )
    
    def _calculate_overall_status(self, checks: List[ComplianceCheck]) -> ComplianceStatus:
        """Calculate overall compliance status"""
        
        # Any required check non-compliant = overall non-compliant
        required_checks = [c for c in checks if c.required]
        if any(c.status == ComplianceStatus.NON_COMPLIANT for c in required_checks):
            return ComplianceStatus.NON_COMPLIANT
        
        # All required checks compliant = overall compliant
        if all(c.status in [ComplianceStatus.COMPLIANT, ComplianceStatus.EXEMPTED] for c in required_checks):
            return ComplianceStatus.COMPLIANT
        
        # Otherwise pending review
        return ComplianceStatus.PENDING_REVIEW
    
    def get_required_documents(self, country: str, partner_type: str) -> List[str]:
        """
        Get list of required documents for country and partner type.
        
        Args:
            country: Country code
            partner_type: Partner type
        
        Returns:
            List of required document names
        """
        country = country.upper()
        partner_type = partner_type.lower()
        
        required_docs = []
        
        # Country-specific documents
        country_rules = self.COUNTRY_COMPLIANCE.get(country)
        if country_rules:
            for rule in country_rules["checks"]:
                if partner_type in rule["required_for"]:
                    required_docs.append(rule["document"])
        
        return required_docs
    
    def get_compliance_checklist(self, country: str, partner_type: str) -> Dict:
        """
        Get compliance checklist for UI display.
        
        Args:
            country: Country code
            partner_type: Partner type
        
        Returns:
            Dict with checklist items
        """
        country = country.upper()
        partner_type = partner_type.lower()
        
        checklist = {
            "country": country,
            "partner_type": partner_type,
            "required_checks": [],
            "optional_checks": [],
            "required_documents": self.get_required_documents(country, partner_type)
        }
        
        # Country checks
        country_rules = self.COUNTRY_COMPLIANCE.get(country, {})
        if country_rules:
            for rule in country_rules.get("checks", []):
                item = {
                    "name": rule["name"],
                    "description": rule["description"],
                    "document": rule["document"]
                }
                
                if partner_type in rule["required_for"]:
                    checklist["required_checks"].append(item)
                elif partner_type not in rule["exempted_for"]:
                    checklist["optional_checks"].append(item)
        
        # Type checks
        type_checks = self.PARTNER_TYPE_CHECKS.get(partner_type, [])
        for rule in type_checks:
            item = {
                "name": rule["name"],
                "description": rule["description"]
            }
            
            if rule["required"]:
                checklist["required_checks"].append(item)
            else:
                checklist["optional_checks"].append(item)
        
        return checklist
