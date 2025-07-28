"""
TLD Documentation Generator
Generates comprehensive documentation for administrators about TLD requirements
"""

import sys

sys.path.append(".")

from apis.tld_requirements import tld_requirements_db, RequirementType


def generate_admin_documentation():
    """Generate comprehensive TLD requirements documentation for administrators"""

    doc = """# TLD Registration Requirements Documentation
## Nomadly Domain Registration System

This document provides comprehensive information about country-specific Top-Level Domain (ccTLD) registration requirements.

## Quick Reference Summary

### Complexity Levels:
- **Open**: No special requirements
- **Low**: 1 mandatory requirement  
- **Medium**: 2-3 mandatory requirements
- **High**: 4+ mandatory requirements

---

"""

    # Get all supported TLDs and group by complexity
    supported_tlds = tld_requirements_db.get_supported_tlds()
    complexity_groups = {"Open": [], "Low": [], "Medium": [], "High": []}

    for tld in supported_tlds:
        summary = tld_requirements_db.get_tld_summary(tld)
        complexity_groups[summary["complexity_level"]].append((tld, summary))

    # Generate overview table
    doc += "## TLD Overview Table\n\n"
    doc += "| TLD | Country | Complexity | Mandatory Docs | Key Requirements |\n"
    doc += "|-----|---------|------------|----------------|------------------|\n"

    country_names = {
        "ru": "Russia",
        "es": "Spain",
        "fr": "France",
        "de": "Germany",
        "us": "United States",
        "pt": "Portugal",
        "ro": "Romania",
        "fi": "Finland",
        "hk": "Hong Kong",
        "id": "Indonesia",
        "se": "Sweden",
        "eu": "European Union",
        "br": "Brazil",
        "cl": "Chile",
        "ca": "Canada",
        "jp": "Japan",
        "io": "British Indian Ocean",
        "co": "Colombia",
        "ai": "Anguilla",
        "ph": "Philippines",
        "bz": "Belize",
        "cc": "Cocos Islands",
        "sr": "Suriname",
        "in": "India",
    }

    # Sort TLDs by complexity (high to low)
    all_tlds = []
    for complexity in ["High", "Medium", "Low", "Open"]:
        for tld, summary in complexity_groups[complexity]:
            all_tlds.append((tld, summary))

    for tld, summary in all_tlds:
        country = country_names.get(tld, tld.upper())
        requirements = tld_requirements_db.get_mandatory_requirements(tld)
        key_docs = ", ".join(
            [
                req.requirement_type.value.replace("_", " ").title()
                for req in requirements[:3]
            ]
        )
        if len(requirements) > 3:
            key_docs += "..."
        if not key_docs:
            key_docs = "None"

        doc += f"| .{tld} | {country} | {summary['complexity_level']} | {summary['mandatory_requirements']} | {key_docs} |\n"

    doc += "\n---\n\n"

    # Detailed requirements by complexity
    for complexity in ["High", "Medium", "Low"]:
        if complexity_groups[complexity]:
            doc += f"## {complexity} Complexity TLDs\n\n"

            for tld, summary in complexity_groups[complexity]:
                country = country_names.get(tld, tld.upper())
                requirements = tld_requirements_db.get_requirements(tld)

                doc += f"### .{tld} - {country}\n\n"
                doc += f"**Complexity Level:** {complexity}  \n"
                doc += f"**Total Requirements:** {summary['total_requirements']}  \n"
                doc += f"**Mandatory:** {summary['mandatory_requirements']}  \n\n"

                if requirements:
                    doc += "**Required Documentation:**\n\n"
                    for req in requirements:
                        status = (
                            "✅ **Mandatory**" if req.is_mandatory else "🔹 Optional"
                        )
                        doc += f"- {status}: **{req.requirement_type.value.replace('_', ' ').title()}**\n"
                        doc += f"  - Description: {req.description}\n"
                        doc += f"  - API Field: `{req.field_name}`\n"
                        if req.example_value:
                            doc += f"  - Example: `{req.example_value}`\n"
                        if req.validation_pattern:
                            doc += f"  - Pattern: `{req.validation_pattern}`\n"
                        doc += "\n"

                doc += "---\n\n"

    # Open TLDs section
    if complexity_groups["Open"]:
        doc += "## Open TLDs (No Special Requirements)\n\n"
        doc += "These TLDs can be registered without special documentation:\n\n"

        for tld, summary in complexity_groups["Open"]:
            country = country_names.get(tld, tld.upper())
            doc += f"- **.{tld}** - {country}\n"

        doc += "\n---\n\n"

    # Implementation guide
    doc += """## Implementation Guide for Developers

### Using the TLD Requirements System

```python
from apis.tld_requirements import tld_requirements_db

# Check if TLD has special requirements
is_open = tld_requirements_db.is_open_tld('io')  # True
is_open = tld_requirements_db.is_open_tld('ru')  # False

# Get requirements for a TLD
requirements = tld_requirements_db.get_requirements('ru')
mandatory_only = tld_requirements_db.get_mandatory_requirements('ru')

# Validate user data
user_data = {'inn': '1231767006', 'birth_date': '1991-01-05'}
validation = tld_requirements_db.validate_requirements('ru', user_data)

# Generate API additional_data
additional_data = tld_requirements_db.get_additional_data_for_tld('ru', user_data)
```

### Customer Data Collection

For high-complexity TLDs, ensure you collect:

1. **Tax ID/National ID**: Required for most restricted TLDs
2. **Birth Date**: Common requirement for individual registrants
3. **Passport/ID Number**: Identity verification
4. **Proof of Residency**: For geo-restricted TLDs

### Error Handling

Always validate requirements before attempting registration:

```python
validation = tld_requirements_db.validate_requirements(tld, user_data)
if validation['errors']:
    # Handle missing or invalid data
    return error_response(validation['errors'])
```

---

## Common Requirement Types

"""

    # Document requirement types
    req_type_descriptions = {
        RequirementType.PASSPORT: "Identity document (passport, ID card, driver's license)",
        RequirementType.TAX_ID: "National tax identification number (INN, NIF, CNPJ, etc.)",
        RequirementType.BIRTH_DATE: "Date of birth for identity verification",
        RequirementType.RESIDENCY_PROOF: "Proof of legal residence or citizenship",
        RequirementType.BUSINESS_REG: "Business registration documents",
        RequirementType.VAT_NUMBER: "Value Added Tax registration number",
        RequirementType.PHONE_VERIFICATION: "Phone number verification process",
        RequirementType.EMAIL_VERIFICATION: "Email address verification process",
        RequirementType.LOCAL_CONTACT: "Local representative or contact person",
        RequirementType.NAMESERVER_LOCATION: "Geographic nameserver requirements",
    }

    for req_type, description in req_type_descriptions.items():
        doc += f"### {req_type.value.replace('_', ' ').title()}\n"
        doc += f"{description}\n\n"

        # Find TLDs that require this
        requiring_tlds = []
        for tld in supported_tlds:
            requirements = tld_requirements_db.get_requirements(tld)
            if any(req.requirement_type == req_type for req in requirements):
                requiring_tlds.append(tld)

        if requiring_tlds:
            doc += f"**Required by:** {', '.join([f'.{tld}' for tld in requiring_tlds])}\n\n"

        doc += "---\n\n"

    doc += """
## Support Resources

- **OpenProvider Documentation**: https://support.openprovider.eu/hc/en-us/sections/360005841014-Documentation-per-TLD
- **ICANN ccTLD Information**: https://www.icann.org/resources/pages/cctlds-21-2012-02-25-en
- **TLD Requirements Database**: Updated based on registry policies as of 2025

---

*Last Updated: January 2025*  
*Nomadly Domain Registration System*
"""

    return doc


if __name__ == "__main__":
    documentation = generate_admin_documentation()

    # Write to file
    with open("TLD_REQUIREMENTS_DOCUMENTATION.md", "w", encoding="utf-8") as f:
        f.write(documentation)

    print("✅ TLD Requirements Documentation generated successfully!")
    print("📄 File: TLD_REQUIREMENTS_DOCUMENTATION.md")
    print(f"📊 Total supported TLDs: {len(tld_requirements_db.get_supported_tlds())}")
