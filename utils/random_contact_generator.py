"""
Random Contact Generator for Nameword Domain Registration
Generates realistic random contact information for domain registrations
"""

import random
import string
from datetime import datetime, timedelta
from typing import Dict


class RandomContactGenerator:
    """Generate random contact information for domain registration"""

    # First names (popular names)
    FIRST_NAMES = [
        "James",
        "Mary",
        "Robert",
        "Patricia",
        "John",
        "Jennifer",
        "Michael",
        "Linda",
        "William",
        "Elizabeth",
        "David",
        "Barbara",
        "Richard",
        "Susan",
        "Joseph",
        "Jessica",
        "Thomas",
        "Sarah",
        "Christopher",
        "Karen",
        "Charles",
        "Nancy",
        "Daniel",
        "Lisa",
        "Matthew",
        "Betty",
        "Anthony",
        "Helen",
        "Mark",
        "Sandra",
        "Donald",
        "Donna",
        "Steven",
        "Carol",
        "Paul",
        "Ruth",
        "Andrew",
        "Sharon",
        "Kenneth",
        "Michelle",
        "Joshua",
        "Laura",
        "Kevin",
        "Sarah",
        "Brian",
        "Kimberly",
        "George",
        "Deborah",
        "Timothy",
        "Dorothy",
        "Ronald",
        "Lisa",
        "Edward",
        "Nancy",
        "Jason",
        "Karen",
    ]

    # Last names (common surnames)
    LAST_NAMES = [
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Garcia",
        "Miller",
        "Davis",
        "Rodriguez",
        "Martinez",
        "Hernandez",
        "Lopez",
        "Gonzalez",
        "Wilson",
        "Anderson",
        "Thomas",
        "Taylor",
        "Moore",
        "Jackson",
        "Martin",
        "Lee",
        "Perez",
        "Thompson",
        "White",
        "Harris",
        "Sanchez",
        "Clark",
        "Ramirez",
        "Lewis",
        "Robinson",
        "Walker",
        "Young",
        "Allen",
        "King",
        "Wright",
        "Scott",
        "Torres",
        "Nguyen",
        "Hill",
        "Flores",
        "Green",
        "Adams",
        "Nelson",
        "Baker",
        "Hall",
        "Rivera",
        "Campbell",
        "Mitchell",
        "Carter",
        "Roberts",
        "Gomez",
        "Phillips",
        "Evans",
        "Turner",
        "Diaz",
        "Parker",
    ]

    # States with abbreviations
    US_STATES = [
        ("Alabama", "AL"),
        ("Alaska", "AK"),
        ("Arizona", "AZ"),
        ("Arkansas", "AR"),
        ("California", "CA"),
        ("Colorado", "CO"),
        ("Connecticut", "CT"),
        ("Delaware", "DE"),
        ("Florida", "FL"),
        ("Georgia", "GA"),
        ("Hawaii", "HI"),
        ("Idaho", "ID"),
        ("Illinois", "IL"),
        ("Indiana", "IN"),
        ("Iowa", "IA"),
        ("Kansas", "KS"),
        ("Kentucky", "KY"),
        ("Louisiana", "LA"),
        ("Maine", "ME"),
        ("Maryland", "MD"),
        ("Massachusetts", "MA"),
        ("Michigan", "MI"),
        ("Minnesota", "MN"),
        ("Mississippi", "MS"),
        ("Missouri", "MO"),
        ("Montana", "MT"),
        ("Nebraska", "NE"),
        ("Nevada", "NV"),
        ("New Hampshire", "NH"),
        ("New Jersey", "NJ"),
        ("New Mexico", "NM"),
        ("New York", "NY"),
        ("North Carolina", "NC"),
        ("North Dakota", "ND"),
        ("Ohio", "OH"),
        ("Oklahoma", "OK"),
        ("Oregon", "OR"),
        ("Pennsylvania", "PA"),
        ("Rhode Island", "RI"),
        ("South Carolina", "SC"),
        ("South Dakota", "SD"),
        ("Tennessee", "TN"),
        ("Texas", "TX"),
        ("Utah", "UT"),
        ("Vermont", "VT"),
        ("Virginia", "VA"),
        ("Washington", "WA"),
        ("West Virginia", "WV"),
        ("Wisconsin", "WI"),
        ("Wyoming", "WY"),
    ]

    # Common US cities by state (subset for realism)
    US_CITIES = {
        "CA": ["Los Angeles", "San Francisco", "San Diego", "Sacramento", "Fresno"],
        "TX": ["Houston", "Dallas", "Austin", "San Antonio", "Fort Worth"],
        "FL": ["Miami", "Tampa", "Orlando", "Jacksonville", "St. Petersburg"],
        "NY": ["New York", "Buffalo", "Rochester", "Syracuse", "Albany"],
        "IL": ["Chicago", "Aurora", "Peoria", "Rockford", "Elgin"],
        "PA": ["Philadelphia", "Pittsburgh", "Allentown", "Erie", "Reading"],
        "OH": ["Columbus", "Cleveland", "Cincinnati", "Toledo", "Akron"],
        "GA": ["Atlanta", "Augusta", "Columbus", "Savannah", "Athens"],
        "NC": ["Charlotte", "Raleigh", "Greensboro", "Durham", "Winston-Salem"],
        "MI": ["Detroit", "Grand Rapids", "Warren", "Sterling Heights", "Lansing"],
    }

    # Street name components
    STREET_NAMES = [
        "Main",
        "Oak",
        "Pine",
        "Maple",
        "Cedar",
        "Elm",
        "Washington",
        "Park",
        "Hill",
        "Church",
        "Spring",
        "River",
        "Lake",
        "First",
        "Second",
        "Third",
        "Fourth",
        "Fifth",
        "Sixth",
        "Lincoln",
        "Madison",
        "Jefferson",
        "Franklin",
        "Jackson",
        "Wilson",
        "Johnson",
        "Davis",
    ]

    STREET_TYPES = ["St", "Ave", "Rd", "Dr", "Ln", "Ct", "Pl", "Way", "Blvd"]

    @classmethod
    def generate_random_contact(cls, email: str) -> Dict[str, str]:
        """Generate a complete random US contact information"""

        # Basic personal info
        first_name = random.choice(cls.FIRST_NAMES)
        last_name = random.choice(cls.LAST_NAMES)

        # Address generation
        state_name, state_code = random.choice(cls.US_STATES)

        # Get city for state or use generic if not in our list
        if state_code in cls.US_CITIES:
            city = random.choice(cls.US_CITIES[state_code])
        else:
            city = f"{random.choice(['Spring', 'River', 'Lake', 'Hill'])}field"

        # Street address
        street_number = random.randint(100, 9999)
        street_name = random.choice(cls.STREET_NAMES)
        street_type = random.choice(cls.STREET_TYPES)
        address = f"{street_number} {street_name} {street_type}"

        # ZIP code (5 digit format)
        zip_code = f"{random.randint(10000, 99999)}"

        # Phone number (US format)
        area_code = random.randint(200, 999)  # Valid area codes start from 200
        exchange = random.randint(200, 999)
        number = random.randint(1000, 9999)
        phone = f"+1.{area_code}{exchange}{number}"

        # Date of birth (18-80 years old)
        birth_year = random.randint(1943, 2005)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)  # Safe day range for all months
        date_of_birth = f"{birth_year:04d}-{birth_month:02d}-{birth_day:02d}"

        # Passport number (9 characters: 2 letters + 7 digits)
        passport_letters = "".join(random.choices(string.ascii_uppercase, k=2))
        passport_digits = "".join(random.choices(string.digits, k=7))
        passport_number = f"{passport_letters}{passport_digits}"

        return {
            "firstName": first_name,
            "lastName": last_name,
            "email": email,
            "phone": phone,
            "address": address,
            "city": city,
            "state": state_name,
            "zipCode": zip_code,
            "country": "United States",
            "countryCode": "US",
            "dateOfBirth": date_of_birth,
            "passportNumber": passport_number,
            "fullName": f"{first_name} {last_name}",
        }

    @classmethod
    def generate_company_contact(cls, email: str) -> Dict[str, str]:
        """Generate random company contact (alternative format)"""
        contact = cls.generate_random_contact(email)

        # Add company-specific fields
        company_suffixes = [
            "LLC",
            "Inc",
            "Corp",
            "Co",
            "Solutions",
            "Services",
            "Group",
        ]
        company_prefixes = ["Digital", "Tech", "Global", "Advanced", "Premier", "Elite"]

        company_name = f"{random.choice(company_prefixes)} {contact['lastName']} {random.choice(company_suffixes)}"

        contact.update(
            {
                "companyName": company_name,
                "organizationName": company_name,
                "type": "organization",
            }
        )

        return contact
