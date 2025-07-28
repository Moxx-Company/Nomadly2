"""
Country-Specific TLD Service for Nomadly2
Enhanced TLD management with country-specific features and pricing
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from database import get_db_manager
from utils.translation_helper import t_user
import re

logger = logging.getLogger(__name__)


class CountryTLDService:
    """Country-specific TLD management and enhanced features"""

    def __init__(self):
        self.db = get_db_manager()

        # Country-specific TLD configurations
        self.country_tlds = {
            # Popular country TLDs with special features
            "uk": {
                "extensions": [".co.uk", ".org.uk", ".me.uk", ".ltd.uk"],
                "requirements": {
                    "local_presence": False,
                    "documentation": None,
                    "restrictions": "Open registration",
                },
                "pricing": {
                    "co.uk": 12.99,
                    "org.uk": 11.99,
                    "me.uk": 9.99,
                    "ltd.uk": 15.99,
                },
                "features": ["Privacy by default", "Fast DNS", "EU compliance"],
                "flag": "🇬🇧",
                "popularity": 95,
            },
            "de": {
                "extensions": [".de"],
                "requirements": {
                    "local_presence": True,
                    "documentation": "German address required",
                    "restrictions": "Local presence mandatory",
                },
                "pricing": {"de": 18.99},
                "features": ["High trust", "German hosting", "GDPR compliant"],
                "flag": "🇩🇪",
                "popularity": 90,
            },
            "ca": {
                "extensions": [".ca"],
                "requirements": {
                    "local_presence": True,
                    "documentation": "Canadian presence required",
                    "restrictions": "Canadian residents/businesses only",
                },
                "pricing": {"ca": 16.99},
                "features": [
                    "Canadian identity",
                    "Privacy protection",
                    "Bilingual support",
                ],
                "flag": "🇨🇦",
                "popularity": 85,
            },
            "au": {
                "extensions": [".com.au", ".org.au", ".net.au"],
                "requirements": {
                    "local_presence": True,
                    "documentation": "Australian presence required",
                    "restrictions": "Australian residents/businesses only",
                },
                "pricing": {"com.au": 19.99, "org.au": 17.99, "net.au": 17.99},
                "features": ["Australian identity", "Local SEO", "Trusted domains"],
                "flag": "🇦🇺",
                "popularity": 80,
            },
            "fr": {
                "extensions": [".fr"],
                "requirements": {
                    "local_presence": True,
                    "documentation": "French/EU address required",
                    "restrictions": "EU residents only",
                },
                "pricing": {"fr": 14.99},
                "features": ["French identity", "EU compliance", "Privacy protection"],
                "flag": "🇫🇷",
                "popularity": 88,
            },
            "nl": {
                "extensions": [".nl"],
                "requirements": {
                    "local_presence": False,
                    "documentation": None,
                    "restrictions": "Open registration",
                },
                "pricing": {"nl": 13.99},
                "features": ["Dutch identity", "High availability", "No restrictions"],
                "flag": "🇳🇱",
                "popularity": 82,
            },
            "it": {
                "extensions": [".it"],
                "requirements": {
                    "local_presence": True,
                    "documentation": "EU address required",
                    "restrictions": "EU residents only",
                },
                "pricing": {"it": 15.99},
                "features": ["Italian identity", "EU compliance", "High trust"],
                "flag": "🇮🇹",
                "popularity": 78,
            },
            "es": {
                "extensions": [".es"],
                "requirements": {
                    "local_presence": False,
                    "documentation": None,
                    "restrictions": "Open registration",
                },
                "pricing": {"es": 12.99},
                "features": ["Spanish identity", "Latin market", "No restrictions"],
                "flag": "🇪🇸",
                "popularity": 85,
            },
            "ch": {
                "extensions": [".ch"],
                "requirements": {
                    "local_presence": True,
                    "documentation": "Swiss address required",
                    "restrictions": "Swiss presence required",
                },
                "pricing": {"ch": 24.99},
                "features": ["Swiss identity", "High trust", "Banking grade"],
                "flag": "🇨🇭",
                "popularity": 75,
            },
            "se": {
                "extensions": [".se"],
                "requirements": {
                    "local_presence": False,
                    "documentation": None,
                    "restrictions": "Open registration",
                },
                "pricing": {"se": 16.99},
                "features": ["Swedish identity", "High tech", "Privacy focused"],
                "flag": "🇸🇪",
                "popularity": 77,
            },
        }

        # Generic TLD categories with enhanced features
        self.generic_tlds = {
            "premium": {
                "extensions": [".io", ".co", ".ai", ".dev", ".app"],
                "pricing": {
                    ".io": 49.99,
                    ".co": 29.99,
                    ".ai": 89.99,
                    ".dev": 19.99,
                    ".app": 19.99,
                },
                "features": ["Tech identity", "High value", "Developer friendly"],
                "category": "Technology & Innovation",
            },
            "business": {
                "extensions": [".biz", ".company", ".enterprises", ".solutions"],
                "pricing": {
                    ".biz": 18.99,
                    ".company": 24.99,
                    ".enterprises": 34.99,
                    ".solutions": 29.99,
                },
                "features": ["Professional", "Business focus", "Corporate identity"],
                "category": "Business & Professional",
            },
            "creative": {
                "extensions": [".design", ".art", ".studio", ".gallery"],
                "pricing": {
                    ".design": 39.99,
                    ".art": 24.99,
                    ".studio": 34.99,
                    ".gallery": 29.99,
                },
                "features": ["Creative identity", "Artistic focus", "Visual appeal"],
                "category": "Creative & Arts",
            },
            "lifestyle": {
                "extensions": [".life", ".style", ".fashion", ".beauty"],
                "pricing": {
                    ".life": 24.99,
                    ".style": 29.99,
                    ".fashion": 39.99,
                    ".beauty": 34.99,
                },
                "features": ["Lifestyle brand", "Personal identity", "Consumer focus"],
                "category": "Lifestyle & Personal",
            },
        }

        # Special offshore TLDs for privacy
        self.offshore_tlds = {
            "privacy_focused": {
                "extensions": [".sbs", ".pm", ".cc", ".ws"],
                "pricing": {".sbs": 2.99, ".pm": 89.99, ".cc": 19.99, ".ws": 34.99},
                "features": [
                    "Maximum privacy",
                    "Offshore hosting",
                    "Anonymous registration",
                ],
                "category": "Privacy & Offshore",
                "special_benefits": [
                    "WHOIS protection included",
                    "Anonymous contacts",
                    "Offshore servers",
                ],
            }
        }

        # TLD recommendation engine weights
        self.recommendation_weights = {
            "price": 0.3,
            "popularity": 0.2,
            "features": 0.2,
            "requirements": 0.15,
            "user_preference": 0.15,
        }

    async def get_country_tld_recommendations(
        self,
        user_country: str = None,
        business_type: str = None,
        budget_range: str = "medium",
    ) -> List[Dict[str, Any]]:
        """
        Get intelligent TLD recommendations based on user profile

        Args:
            user_country: User's country code
            business_type: Type of business (tech, creative, business, etc.)
            budget_range: Budget preference (low, medium, high, premium)

        Returns:
            Ranked list of TLD recommendations
        """
        try:
            recommendations = []

            # Add country-specific recommendations
            if user_country and user_country.lower() in self.country_tlds:
                country_info = self.country_tlds[user_country.lower()]
                for ext in country_info["extensions"]:
                    tld_name = ext.lstrip(".")
                    price = country_info["pricing"].get(tld_name, 15.99)

                    recommendations.append(
                        {
                            "tld": ext,
                            "price": price,
                            "category": "Country-Specific",
                            "country": user_country.upper(),
                            "flag": country_info["flag"],
                            "features": country_info["features"],
                            "requirements": country_info["requirements"],
                            "popularity": country_info["popularity"],
                            "score": self._calculate_tld_score(
                                ext,
                                price,
                                country_info["popularity"],
                                business_type,
                                budget_range,
                            ),
                            "recommendation_reason": f"Perfect for {user_country.upper()} presence",
                        }
                    )

            # Add generic TLD recommendations based on business type
            if business_type:
                category_map = {
                    "tech": "premium",
                    "technology": "premium",
                    "startup": "premium",
                    "business": "business",
                    "corporate": "business",
                    "creative": "creative",
                    "art": "creative",
                    "personal": "lifestyle",
                    "blog": "lifestyle",
                }

                category = category_map.get(business_type.lower(), "business")
                if category in self.generic_tlds:
                    generic_info = self.generic_tlds[category]
                    for ext, price in generic_info["pricing"].items():
                        recommendations.append(
                            {
                                "tld": ext,
                                "price": price,
                                "category": generic_info["category"],
                                "country": "Global",
                                "flag": "🌍",
                                "features": generic_info["features"],
                                "requirements": {
                                    "local_presence": False,
                                    "restrictions": "Open registration",
                                },
                                "popularity": 70,  # Generic popularity
                                "score": self._calculate_tld_score(
                                    ext, price, 70, business_type, budget_range
                                ),
                                "recommendation_reason": f"Ideal for {business_type} businesses",
                            }
                        )

            # Add offshore privacy TLDs (always recommended for Nomadly)
            privacy_info = self.offshore_tlds["privacy_focused"]
            for ext, price in privacy_info["pricing"].items():
                recommendations.append(
                    {
                        "tld": ext,
                        "price": price,
                        "category": privacy_info["category"],
                        "country": "Offshore",
                        "flag": "🏴‍☠️",
                        "features": privacy_info["features"],
                        "special_benefits": privacy_info.get("special_benefits", []),
                        "requirements": {
                            "local_presence": False,
                            "restrictions": "Privacy focused",
                        },
                        "popularity": 60,
                        "score": self._calculate_tld_score(
                            ext, price, 60, "privacy", budget_range
                        )
                        + 10,  # Bonus for privacy
                        "recommendation_reason": "Maximum privacy and offshore hosting",
                    }
                )

            # Add popular generic TLDs as fallback
            popular_tlds = [
                (".com", 11.98, 100),
                (".net", 15.53, 85),
                (".org", 8.99, 80),
                (".info", 3.99, 60),
                (".biz", 18.99, 55),
            ]

            for ext, price, popularity in popular_tlds:
                if not any(r["tld"] == ext for r in recommendations):
                    recommendations.append(
                        {
                            "tld": ext,
                            "price": price,
                            "category": "Popular Generic",
                            "country": "Global",
                            "flag": "🌐",
                            "features": [
                                "Universal recognition",
                                "High trust",
                                "SEO friendly",
                            ],
                            "requirements": {
                                "local_presence": False,
                                "restrictions": "Open registration",
                            },
                            "popularity": popularity,
                            "score": self._calculate_tld_score(
                                ext, price, popularity, business_type, budget_range
                            ),
                            "recommendation_reason": "Universally recognized and trusted",
                        }
                    )

            # Sort by score and limit results
            recommendations.sort(key=lambda x: x["score"], reverse=True)
            return recommendations[:12]  # Top 12 recommendations

        except Exception as e:
            logger.error(f"Error getting TLD recommendations: {e}")
            return [
                {
                    "tld": ".com",
                    "price": 11.98,
                    "category": "Generic",
                    "country": "Global",
                    "flag": "🌐",
                    "features": ["Universal", "Trusted"],
                    "requirements": {"local_presence": False},
                    "popularity": 100,
                    "score": 85,
                    "recommendation_reason": "Most popular and trusted",
                }
            ]

    async def check_tld_availability_batch(
        self, domain_name: str, tlds: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """
        Check availability for domain across multiple TLDs

        Args:
            domain_name: Base domain name (without TLD)
            tlds: List of TLDs to check

        Returns:
            Availability results for each TLD
        """
        try:
            results = {}

            for tld in tlds:
                full_domain = f"{domain_name}{tld}"

                # This would typically use the OpenProvider API
                # For now, simulate availability checking
                is_available = await self._check_single_domain_availability(full_domain)

                tld_info = self._get_tld_info(tld)

                results[tld] = {
                    "domain": full_domain,
                    "available": is_available,
                    "price": tld_info.get("price", 15.99),
                    "category": tld_info.get("category", "Generic"),
                    "features": tld_info.get("features", []),
                    "requirements": tld_info.get("requirements", {}),
                    "recommendation_score": tld_info.get("score", 50),
                }

            return results

        except Exception as e:
            logger.error(f"Error checking TLD availability: {e}")
            return {}

    async def get_tld_registration_requirements(self, tld: str) -> Dict[str, Any]:
        """
        Get detailed registration requirements for specific TLD

        Args:
            tld: Top-level domain

        Returns:
            Registration requirements and procedures
        """
        try:
            tld_clean = tld.lstrip(".")

            # Check country TLDs
            for country, info in self.country_tlds.items():
                for ext in info["extensions"]:
                    if ext.lstrip(".") == tld_clean:
                        return {
                            "tld": tld,
                            "country": country.upper(),
                            "flag": info["flag"],
                            "requirements": info["requirements"],
                            "pricing": info["pricing"].get(tld_clean, 15.99),
                            "features": info["features"],
                            "registration_process": self._get_registration_process(
                                info["requirements"]
                            ),
                            "verification_needed": info["requirements"].get(
                                "local_presence", False
                            ),
                            "documents_required": info["requirements"].get(
                                "documentation"
                            ),
                            "processing_time": (
                                "1-3 business days"
                                if info["requirements"].get("local_presence")
                                else "Immediate"
                            ),
                        }

            # Check generic TLDs
            for category, info in self.generic_tlds.items():
                if tld in info["extensions"]:
                    return {
                        "tld": tld,
                        "category": info["category"],
                        "requirements": {
                            "local_presence": False,
                            "restrictions": "Open registration",
                        },
                        "pricing": info["pricing"].get(tld, 25.99),
                        "features": info["features"],
                        "registration_process": [
                            "Submit order",
                            "Make payment",
                            "Instant activation",
                        ],
                        "verification_needed": False,
                        "documents_required": None,
                        "processing_time": "Immediate",
                    }

            # Check offshore TLDs
            for category, info in self.offshore_tlds.items():
                if tld in info["extensions"]:
                    return {
                        "tld": tld,
                        "category": info["category"],
                        "requirements": {
                            "local_presence": False,
                            "restrictions": "Privacy focused",
                        },
                        "pricing": info["pricing"].get(tld, 15.99),
                        "features": info["features"],
                        "special_benefits": info.get("special_benefits", []),
                        "registration_process": [
                            "Anonymous order",
                            "Crypto payment",
                            "Privacy activation",
                        ],
                        "verification_needed": False,
                        "documents_required": None,
                        "processing_time": "Immediate",
                        "privacy_level": "Maximum",
                    }

            # Default for unknown TLDs
            return {
                "tld": tld,
                "category": "Generic",
                "requirements": {
                    "local_presence": False,
                    "restrictions": "Standard registration",
                },
                "pricing": 19.99,
                "features": ["Standard features"],
                "registration_process": [
                    "Submit order",
                    "Make payment",
                    "Standard activation",
                ],
                "verification_needed": False,
                "documents_required": None,
                "processing_time": "Standard",
            }

        except Exception as e:
            logger.error(f"Error getting TLD requirements: {e}")
            return {
                "tld": tld,
                "category": "Unknown",
                "requirements": {},
                "pricing": 19.99,
                "features": [],
                "registration_process": [],
                "verification_needed": False,
                "processing_time": "Unknown",
            }

    async def get_country_specific_search_suggestions(
        self, query: str, user_country: str = None
    ) -> List[Dict[str, Any]]:
        """
        Get country-specific domain suggestions based on search query

        Args:
            query: Search query/domain name
            user_country: User's country for localized suggestions

        Returns:
            Country-specific domain suggestions
        """
        try:
            suggestions = []

            # Clean query
            base_name = re.sub(r"[^a-zA-Z0-9-]", "", query.lower())

            # Add user's country TLD if available
            if user_country and user_country.lower() in self.country_tlds:
                country_info = self.country_tlds[user_country.lower()]
                for ext in country_info["extensions"]:
                    suggestions.append(
                        {
                            "domain": f"{base_name}{ext}",
                            "tld": ext,
                            "country": user_country.upper(),
                            "flag": country_info["flag"],
                            "price": country_info["pricing"].get(
                                ext.lstrip("."), 15.99
                            ),
                            "category": "Local Country",
                            "benefits": [f"Perfect for {user_country.upper()} market"]
                            + country_info["features"],
                        }
                    )

            # Add popular country TLDs based on query relevance
            popular_countries = ["uk", "de", "ca", "au", "fr"]
            for country in popular_countries:
                if country != user_country:
                    country_info = self.country_tlds[country]
                    primary_ext = country_info["extensions"][0]
                    suggestions.append(
                        {
                            "domain": f"{base_name}{primary_ext}",
                            "tld": primary_ext,
                            "country": country.upper(),
                            "flag": country_info["flag"],
                            "price": country_info["pricing"].get(
                                primary_ext.lstrip("."), 15.99
                            ),
                            "category": "International",
                            "benefits": [f"Expand to {country.upper()} market"]
                            + country_info["features"][:2],
                        }
                    )

            # Add variations with prefixes/suffixes
            variations = [
                f"my{base_name}",
                f"get{base_name}",
                f"{base_name}online",
                f"{base_name}pro",
                f"{base_name}hub",
            ]

            for variation in variations:
                # Add with popular TLD
                suggestions.append(
                    {
                        "domain": f"{variation}.com",
                        "tld": ".com",
                        "country": "Global",
                        "flag": "🌐",
                        "price": 11.98,
                        "category": "Variation",
                        "benefits": ["Creative alternative", "Universal recognition"],
                    }
                )

            return suggestions[:10]  # Limit to top 10

        except Exception as e:
            logger.error(f"Error getting country suggestions: {e}")
            return []

    def get_tld_categories_overview(self) -> Dict[str, Any]:
        """
        Get comprehensive overview of all TLD categories

        Returns:
            Complete TLD categories information
        """
        try:
            categories = {
                "country_specific": {
                    "title": "Country-Specific Domains",
                    "description": "Perfect for local businesses and country-specific presence",
                    "icon": "🌍",
                    "count": sum(
                        len(info["extensions"]) for info in self.country_tlds.values()
                    ),
                    "price_range": "€12.99 - €89.99",
                    "popular_tlds": [".co.uk", ".de", ".ca", ".au", ".fr"],
                    "benefits": [
                        "Local SEO advantage",
                        "Country identity",
                        "Trust building",
                    ],
                },
                "generic_premium": {
                    "title": "Premium Generic Domains",
                    "description": "High-value domains for technology and innovation",
                    "icon": "💎",
                    "count": len(self.generic_tlds["premium"]["extensions"]),
                    "price_range": "€19.99 - €89.99",
                    "popular_tlds": [".io", ".co", ".ai", ".dev"],
                    "benefits": ["Tech identity", "High value", "Modern appeal"],
                },
                "business_professional": {
                    "title": "Business & Professional",
                    "description": "Corporate and professional domain extensions",
                    "icon": "💼",
                    "count": len(self.generic_tlds["business"]["extensions"]),
                    "price_range": "€18.99 - €34.99",
                    "popular_tlds": [".biz", ".company", ".solutions"],
                    "benefits": [
                        "Professional image",
                        "Business focus",
                        "Corporate trust",
                    ],
                },
                "privacy_offshore": {
                    "title": "Privacy & Offshore",
                    "description": "Maximum privacy and anonymous registration",
                    "icon": "🏴‍☠️",
                    "count": len(self.offshore_tlds["privacy_focused"]["extensions"]),
                    "price_range": "€2.99 - €89.99",
                    "popular_tlds": [".sbs", ".cc", ".ws"],
                    "benefits": [
                        "Maximum privacy",
                        "Anonymous contacts",
                        "Offshore hosting",
                    ],
                },
                "creative_lifestyle": {
                    "title": "Creative & Lifestyle",
                    "description": "Perfect for creative professionals and lifestyle brands",
                    "icon": "🎨",
                    "count": len(self.generic_tlds["creative"]["extensions"])
                    + len(self.generic_tlds["lifestyle"]["extensions"]),
                    "price_range": "€24.99 - €39.99",
                    "popular_tlds": [".design", ".art", ".style", ".life"],
                    "benefits": [
                        "Creative identity",
                        "Artistic appeal",
                        "Personal branding",
                    ],
                },
            }

            return categories

        except Exception as e:
            logger.error(f"Error getting TLD overview: {e}")
            return {}

    # Helper methods
    def _calculate_tld_score(
        self,
        tld: str,
        price: float,
        popularity: int,
        business_type: str = None,
        budget_range: str = "medium",
    ) -> float:
        """Calculate recommendation score for TLD"""
        try:
            score = 0

            # Price component (lower price = higher score)
            price_score = max(0, 100 - (price / 100 * 100))
            score += price_score * self.recommendation_weights["price"]

            # Popularity component
            score += popularity * self.recommendation_weights["popularity"]

            # Budget range adjustment
            budget_multipliers = {
                "low": 1.2,
                "medium": 1.0,
                "high": 0.9,
                "premium": 0.8,
            }
            if price <= 10 and budget_range == "low":
                score += 15
            elif price >= 30 and budget_range == "premium":
                score += 10

            # Business type bonus
            if business_type:
                if business_type.lower() in ["tech", "startup"] and tld in [
                    ".io",
                    ".ai",
                    ".dev",
                ]:
                    score += 20
                elif business_type.lower() in ["business", "corporate"] and tld in [
                    ".com",
                    ".biz",
                ]:
                    score += 15
                elif business_type.lower() in ["creative", "art"] and tld in [
                    ".design",
                    ".art",
                ]:
                    score += 15

            return min(100, max(0, score))

        except Exception as e:
            logger.error(f"Error calculating TLD score: {e}")
            return 50

    async def _check_single_domain_availability(self, domain: str) -> bool:
        """Check availability of single domain"""
        # This would typically use the OpenProvider API
        # For now, simulate based on common patterns
        common_unavailable = [
            "google",
            "facebook",
            "microsoft",
            "apple",
            "amazon",
            "test",
            "example",
            "localhost",
            "admin",
        ]

        domain_name = domain.split(".")[0].lower()
        return domain_name not in common_unavailable

    def _get_tld_info(self, tld: str) -> Dict[str, Any]:
        """Get basic info for TLD"""
        tld_clean = tld.lstrip(".")

        # Check all TLD sources
        for country, info in self.country_tlds.items():
            for ext in info["extensions"]:
                if ext.lstrip(".") == tld_clean:
                    return {
                        "price": info["pricing"].get(tld_clean, 15.99),
                        "category": "Country-Specific",
                        "features": info["features"],
                        "requirements": info["requirements"],
                        "score": info["popularity"],
                    }

        for category, info in self.generic_tlds.items():
            if tld in info["extensions"]:
                return {
                    "price": info["pricing"].get(tld, 25.99),
                    "category": info["category"],
                    "features": info["features"],
                    "requirements": {"local_presence": False},
                    "score": 70,
                }

        for category, info in self.offshore_tlds.items():
            if tld in info["extensions"]:
                return {
                    "price": info["pricing"].get(tld, 15.99),
                    "category": info["category"],
                    "features": info["features"],
                    "requirements": {"local_presence": False},
                    "score": 60,
                }

        # Default for unknown TLD
        return {
            "price": 19.99,
            "category": "Generic",
            "features": ["Standard features"],
            "requirements": {"local_presence": False},
            "score": 50,
        }

    def _get_registration_process(self, requirements: Dict[str, Any]) -> List[str]:
        """Get registration process steps based on requirements"""
        process = ["Submit registration order"]

        if requirements.get("local_presence"):
            process.extend(
                [
                    "Provide local address documentation",
                    "Verify presence requirements",
                    "Processing review (1-3 days)",
                ]
            )

        process.extend(["Complete payment", "Domain activation"])

        return process


# Global country TLD service instance
_country_tld_service = None


def get_country_tld_service() -> CountryTLDService:
    """Get global country TLD service instance"""
    global _country_tld_service
    if _country_tld_service is None:
        _country_tld_service = CountryTLDService()
    return _country_tld_service
