"""
TLD Registration Requirements System
Comprehensive database of country-specific documentation requirements for domain registration
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RequirementType(Enum):
    PASSPORT = "passport"
    TAX_ID = "tax_id"
    BIRTH_DATE = "birth_date"
    RESIDENCY_PROOF = "residency_proof"
    BUSINESS_REG = "business_registration"
    VAT_NUMBER = "vat_number"
    PHONE_VERIFICATION = "phone_verification"
    EMAIL_VERIFICATION = "email_verification"
    LOCAL_CONTACT = "local_contact"
    NAMESERVER_LOCATION = "nameserver_location"


@dataclass
class TLDRequirement:
    """Represents a specific requirement for a TLD"""

    tld: str
    country: str
    requirement_type: RequirementType
    is_mandatory: bool
    field_name: str  # API field name for OpenProvider
    description: str
    validation_pattern: Optional[str] = None
    example_value: Optional[str] = None


class TLDRequirementsDatabase:
    """Database of TLD registration requirements by country"""

    def __init__(self):
        self.requirements = self._initialize_requirements()

    def _initialize_requirements(self) -> Dict[str, List[TLDRequirement]]:
        """Initialize comprehensive TLD requirements database"""

        requirements = {}

        # RUSSIA (.ru) - High Documentation Requirements
        requirements["ru"] = [
            TLDRequirement(
                tld="ru",
                country="Russia",
                requirement_type=RequirementType.TAX_ID,
                is_mandatory=True,
                field_name="inn",
                description="Russian Individual Taxpayer Number (INN)",
                validation_pattern=r"^\d{10,12}$",
                example_value="1231767006",
            ),
            TLDRequirement(
                tld="ru",
                country="Russia",
                requirement_type=RequirementType.BIRTH_DATE,
                is_mandatory=True,
                field_name="birth_date",
                description="Date of birth in YYYY-MM-DD format",
                validation_pattern=r"^\d{4}-\d{2}-\d{2}$",
                example_value="1991-01-05",
            ),
            TLDRequirement(
                tld="ru",
                country="Russia",
                requirement_type=RequirementType.PASSPORT,
                is_mandatory=True,
                field_name="passport_number",
                description="Russian passport number",
                validation_pattern=r"^[A-Z]\d{8}$",
                example_value="V76933800",
            ),
        ]

        # SPAIN (.es) - EU/EEA Residency + Tax ID
        requirements["es"] = [
            TLDRequirement(
                tld="es",
                country="Spain",
                requirement_type=RequirementType.TAX_ID,
                is_mandatory=True,
                field_name="nif_nie",
                description="Spanish Tax ID (NIF/NIE)",
                validation_pattern=r"^[XYZ]?\d{7,8}[A-Z]$",
                example_value="12345678Z",
            ),
            TLDRequirement(
                tld="es",
                country="Spain",
                requirement_type=RequirementType.RESIDENCY_PROOF,
                is_mandatory=True,
                field_name="eu_residency",
                description="Proof of EU/EEA residency with Spanish address",
                example_value="ES",
            ),
            TLDRequirement(
                tld="es",
                country="Spain",
                requirement_type=RequirementType.BIRTH_DATE,
                is_mandatory=True,
                field_name="birth_date",
                description="Date of birth for verification",
                validation_pattern=r"^\d{4}-\d{2}-\d{2}$",
                example_value="1990-01-01",
            ),
        ]

        # FRANCE (.fr) - EU/Switzerland/Norway/Iceland/Liechtenstein
        requirements["fr"] = [
            TLDRequirement(
                tld="fr",
                country="France",
                requirement_type=RequirementType.BIRTH_DATE,
                is_mandatory=True,
                field_name="birth_date",
                description="Date of birth (mandatory)",
                validation_pattern=r"^\d{4}-\d{2}-\d{2}$",
                example_value="1985-03-15",
            ),
            TLDRequirement(
                tld="fr",
                country="France",
                requirement_type=RequirementType.RESIDENCY_PROOF,
                is_mandatory=True,
                field_name="eu_presence",
                description="Presence in EU/Switzerland/Norway/Iceland/Liechtenstein",
                example_value="FR",
            ),
        ]

        # GERMANY (.de) - Administrative Contact Requirement
        requirements["de"] = [
            TLDRequirement(
                tld="de",
                country="Germany",
                requirement_type=RequirementType.LOCAL_CONTACT,
                is_mandatory=True,
                field_name="admin_contact_de",
                description="Administrative contact residing in Germany",
                example_value="DE",
            )
        ]

        # UNITED STATES (.us) - US Nexus Requirement
        requirements["us"] = [
            TLDRequirement(
                tld="us",
                country="United States",
                requirement_type=RequirementType.PASSPORT,
                is_mandatory=True,
                field_name="us_nexus_id",
                description="Valid US ID (driver's license, passport, etc.)",
                example_value="123456789",
            ),
            TLDRequirement(
                tld="us",
                country="United States",
                requirement_type=RequirementType.RESIDENCY_PROOF,
                is_mandatory=True,
                field_name="us_nexus",
                description="US citizenship/residency or bona fide US presence",
                example_value="US",
            ),
        ]

        # PORTUGAL (.pt) - Tax Number + ID Required
        requirements["pt"] = [
            TLDRequirement(
                tld="pt",
                country="Portugal",
                requirement_type=RequirementType.TAX_ID,
                is_mandatory=True,
                field_name="pt_tax_number",
                description="Portuguese tax number",
                validation_pattern=r"^\d{9}$",
                example_value="123456789",
            ),
            TLDRequirement(
                tld="pt",
                country="Portugal",
                requirement_type=RequirementType.PASSPORT,
                is_mandatory=True,
                field_name="pt_id_card",
                description="Portuguese ID card number",
                example_value="12345678",
            ),
        ]

        # ROMANIA (.ro) - ID/VAT Number
        requirements["ro"] = [
            TLDRequirement(
                tld="ro",
                country="Romania",
                requirement_type=RequirementType.PASSPORT,
                is_mandatory=True,
                field_name="ro_id_card",
                description="ID card for individuals",
                example_value="AB123456",
            ),
            TLDRequirement(
                tld="ro",
                country="Romania",
                requirement_type=RequirementType.VAT_NUMBER,
                is_mandatory=False,
                field_name="ro_vat_number",
                description="Registration/VAT number for organizations",
                example_value="RO12345678",
            ),
        ]

        # FINLAND (.fi) - Birth Date Required
        requirements["fi"] = [
            TLDRequirement(
                tld="fi",
                country="Finland",
                requirement_type=RequirementType.BIRTH_DATE,
                is_mandatory=True,
                field_name="birth_date",
                description="Birth date for foreign individuals",
                validation_pattern=r"^\d{4}-\d{2}-\d{2}$",
                example_value="1988-07-20",
            ),
            TLDRequirement(
                tld="fi",
                country="Finland",
                requirement_type=RequirementType.PASSPORT,
                is_mandatory=False,
                field_name="fi_personal_id",
                description="Finnish personal ID for locals",
                example_value="010188-123A",
            ),
        ]

        # HONG KONG (.hk) - ID + Birth Date
        requirements["hk"] = [
            TLDRequirement(
                tld="hk",
                country="Hong Kong",
                requirement_type=RequirementType.PASSPORT,
                is_mandatory=True,
                field_name="hk_id_card",
                description="Hong Kong ID card number",
                validation_pattern=r"^[A-Z]\d{6}\(\d\)$",
                example_value="A123456(7)",
            ),
            TLDRequirement(
                tld="hk",
                country="Hong Kong",
                requirement_type=RequirementType.BIRTH_DATE,
                is_mandatory=True,
                field_name="birth_date",
                description="Date of birth for individuals",
                validation_pattern=r"^\d{4}-\d{2}-\d{2}$",
                example_value="1992-11-10",
            ),
        ]

        # INDONESIA (.id) - Multiple Permits Required
        requirements["id"] = [
            TLDRequirement(
                tld="id",
                country="Indonesia",
                requirement_type=RequirementType.BUSINESS_REG,
                is_mandatory=True,
                field_name="id_business_permits",
                description="SIUP, TDP, AKTA, NPWP permits required",
                example_value="SIUP123456789",
            ),
            TLDRequirement(
                tld="id",
                country="Indonesia",
                requirement_type=RequirementType.TAX_ID,
                is_mandatory=True,
                field_name="id_npwp",
                description="Indonesian tax number (NPWP)",
                validation_pattern=r"^\d{2}\.\d{3}\.\d{3}\.\d{1}-\d{3}\.\d{3}$",
                example_value="01.234.567.8-901.000",
            ),
        ]

        # SWEDEN (.se) - Unrestricted but VAT for non-residents
        requirements["se"] = [
            TLDRequirement(
                tld="se",
                country="Sweden",
                requirement_type=RequirementType.VAT_NUMBER,
                is_mandatory=False,
                field_name="se_vat_id",
                description="VAT ID for non-Swedish organizations",
                validation_pattern=r"^SE\d{12}01$",
                example_value="SE123456789001",
            )
        ]

        # EUROPEAN UNION (.eu) - EU/EEA Citizenship/Residency
        requirements["eu"] = [
            TLDRequirement(
                tld="eu",
                country="European Union",
                requirement_type=RequirementType.RESIDENCY_PROOF,
                is_mandatory=True,
                field_name="eu_eligibility",
                description="EU/EEA residency or EU citizenship",
                example_value="DE",
            ),
            TLDRequirement(
                tld="eu",
                country="European Union",
                requirement_type=RequirementType.EMAIL_VERIFICATION,
                is_mandatory=True,
                field_name="email_verification",
                description="Direct email verification from EURid registry",
                example_value="verified@domain.com",
            ),
        ]

        # BRAZIL (.com.br) - CPF/CNPJ Required
        requirements["br"] = [
            TLDRequirement(
                tld="com.br",
                country="Brazil",
                requirement_type=RequirementType.TAX_ID,
                is_mandatory=True,
                field_name="br_cpf_cnpj",
                description="CPF (individuals) or CNPJ (companies)",
                validation_pattern=r"^\d{11}$|^\d{14}$",
                example_value="12345678901",  # CPF format
            )
        ]

        # CHILE (.cl) - Local Requirement with ID/Tax Number
        requirements["cl"] = [
            TLDRequirement(
                tld="cl",
                country="Chile",
                requirement_type=RequirementType.PASSPORT,
                is_mandatory=True,
                field_name="cl_id_card",
                description="Chilean ID card number for individuals",
                validation_pattern=r"^\d{7,8}-[\dK]$",
                example_value="12345678-9",
            ),
            TLDRequirement(
                tld="cl",
                country="Chile",
                requirement_type=RequirementType.TAX_ID,
                is_mandatory=True,
                field_name="cl_tax_number",
                description="Tax number for organizations",
                example_value="76123456-7",
            ),
        ]

        # CANADA (.ca) - Canadian Presence Required
        requirements["ca"] = [
            TLDRequirement(
                tld="ca",
                country="Canada",
                requirement_type=RequirementType.RESIDENCY_PROOF,
                is_mandatory=True,
                field_name="ca_presence",
                description="Canadian presence required",
                example_value="CA",
            )
        ]

        # JAPAN (.jp) - Local Contact Required
        requirements["jp"] = [
            TLDRequirement(
                tld="jp",
                country="Japan",
                requirement_type=RequirementType.LOCAL_CONTACT,
                is_mandatory=True,
                field_name="jp_local_contact",
                description="Local contact in Japan required",
                example_value="JP",
            )
        ]

        # Open TLDs (No Special Requirements)
        open_tlds = ["io", "co", "ai", "ph", "bz", "cc", "sr", "in"]
        for tld in open_tlds:
            requirements[tld] = []  # No special requirements

        return requirements

    def get_requirements(self, tld: str) -> List[TLDRequirement]:
        """Get requirements for a specific TLD"""
        # Remove leading dot if present
        clean_tld = tld.lstrip(".")
        return self.requirements.get(clean_tld, [])

    def get_mandatory_requirements(self, tld: str) -> List[TLDRequirement]:
        """Get only mandatory requirements for a TLD"""
        all_requirements = self.get_requirements(tld)
        return [req for req in all_requirements if req.is_mandatory]

    def get_additional_data_for_tld(
        self, tld: str, user_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate additional_data dictionary for OpenProvider API based on TLD requirements
        """
        requirements = self.get_requirements(tld)
        additional_data = {}

        for req in requirements:
            if req.field_name in user_data:
                additional_data[req.field_name] = str(user_data[req.field_name])
            elif req.is_mandatory and req.example_value:
                # Use example value for mandatory fields if not provided
                additional_data[req.field_name] = req.example_value
                logger.warning(
                    f"Using example value for mandatory field {req.field_name} in {tld} domain"
                )

        return additional_data

    def validate_requirements(
        self, tld: str, user_data: Dict[str, Any]
    ) -> Dict[str, List[str]]:
        """
        Validate user data against TLD requirements
        Returns dict with 'errors' and 'warnings' lists
        """
        requirements = self.get_requirements(tld)
        errors = []
        warnings = []

        for req in requirements:
            if req.is_mandatory and req.field_name not in user_data:
                errors.append(f"Missing mandatory field for {tld}: {req.description}")
            elif req.field_name in user_data and req.validation_pattern:
                import re

                value = str(user_data[req.field_name])
                if not re.match(req.validation_pattern, value):
                    errors.append(
                        f"Invalid format for {req.field_name}: {req.description}"
                    )

        return {"errors": errors, "warnings": warnings}

    def get_supported_tlds(self) -> List[str]:
        """Get list of all supported TLDs with specific requirements"""
        return list(self.requirements.keys())

    def is_open_tld(self, tld: str) -> bool:
        """Check if TLD has no special registration requirements"""
        clean_tld = tld.lstrip(".")
        requirements = self.get_requirements(clean_tld)
        return len(requirements) == 0

    def get_tld_summary(self, tld: str) -> Dict[str, Any]:
        """Get comprehensive summary of TLD requirements"""
        requirements = self.get_requirements(tld)
        mandatory_count = len([req for req in requirements if req.is_mandatory])

        return {
            "tld": tld,
            "is_open": self.is_open_tld(tld),
            "total_requirements": len(requirements),
            "mandatory_requirements": mandatory_count,
            "optional_requirements": len(requirements) - mandatory_count,
            "required_documents": [
                req.requirement_type.value for req in requirements if req.is_mandatory
            ],
            "complexity_level": (
                "Open"
                if len(requirements) == 0
                else (
                    "Low"
                    if mandatory_count <= 1
                    else "Medium" if mandatory_count <= 3 else "High"
                )
            ),
        }


# Global instance
tld_requirements_db = TLDRequirementsDatabase()
