"""
AWS3 API Integration
Handles URL shortening with custom domains and analytics
"""

import requests
import logging
from typing import Dict, List, Optional, Tuple
import json

logger = logging.getLogger(__name__)


class AWS3API:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://aws3.link/api"

    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def shorten_url(
        self, long_url: str, custom_domain: str = "aws3.link", custom_slug: str = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """Shorten a URL and return success, short_url, and short_code"""
        try:
            url = f"{self.base_url}/shorten"
            data = {"url": long_url, "domain": custom_domain}

            if custom_slug:
                data["custom"] = custom_slug

            response = requests.post(url, json=data, headers=self._get_headers())

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    short_url = result.get("short_url")
                    short_code = result.get("short_code") or short_url.split("/")[-1]

                    logger.info(
                        f"URL shortened successfully: {long_url} -> {short_url}"
                    )
                    return True, short_url, short_code
                else:
                    error_msg = result.get("message", "URL shortening failed")
                    logger.error(f"URL shortening failed: {error_msg}")
                    return False, None, None
            else:
                logger.error(f"URL shortening failed: {response.status_code}")
                return False, None, None

        except Exception as e:
            logger.error(f"URL shortening error: {e}")
            return False, None, None

    def update_url(
        self, short_code: str, new_long_url: str, domain: str = "aws3.link"
    ) -> bool:
        """Update the destination URL of an existing short URL"""
        try:
            url = f"{self.base_url}/update/{short_code}"
            data = {"url": new_long_url, "domain": domain}

            response = requests.put(url, json=data, headers=self._get_headers())

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(
                        f"URL updated successfully: {short_code} -> {new_long_url}"
                    )
                    return True
                else:
                    error_msg = result.get("message", "URL update failed")
                    logger.error(f"URL update failed: {error_msg}")
                    return False
            else:
                logger.error(f"URL update failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"URL update error: {e}")
            return False

    def get_url_analytics(
        self, short_code: str, domain: str = "aws3.link"
    ) -> Optional[Dict]:
        """Get analytics for a short URL"""
        try:
            url = f"{self.base_url}/stats/{short_code}"
            params = {"domain": domain}

            response = requests.get(url, params=params, headers=self._get_headers())

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result.get("data", {})
                else:
                    logger.error(f"Analytics retrieval failed: {result.get('message')}")
                    return None
            else:
                logger.error(f"Analytics retrieval failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Analytics retrieval error: {e}")
            return None

    def delete_url(self, short_code: str, domain: str = "aws3.link") -> bool:
        """Delete a short URL"""
        try:
            url = f"{self.base_url}/delete/{short_code}"
            params = {"domain": domain}

            response = requests.delete(url, params=params, headers=self._get_headers())

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    logger.info(f"URL deleted successfully: {short_code}")
                    return True
                else:
                    logger.error(f"URL deletion failed: {result.get('message')}")
                    return False
            else:
                logger.error(f"URL deletion failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"URL deletion error: {e}")
            return False

    def list_user_urls(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """List URLs for the authenticated user"""
        try:
            url = f"{self.base_url}/urls"
            params = {"limit": limit, "offset": offset}

            response = requests.get(url, params=params, headers=self._get_headers())

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result.get("data", {}).get("urls", [])
                else:
                    logger.error(f"URL listing failed: {result.get('message')}")
                    return []
            else:
                logger.error(f"URL listing failed: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"URL listing error: {e}")
            return []

    def get_available_domains(self) -> List[str]:
        """Get list of available domains for URL shortening"""
        try:
            url = f"{self.base_url}/domains"
            response = requests.get(url, headers=self._get_headers())

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result.get("data", {}).get("domains", [])
                else:
                    logger.error(f"Domain listing failed: {result.get('message')}")
                    return ["aws3.link"]  # Fallback
            else:
                logger.error(f"Domain listing failed: {response.status_code}")
                return ["aws3.link"]  # Fallback

        except Exception as e:
            logger.error(f"Domain listing error: {e}")
            return ["aws3.link"]  # Fallback

    def check_slug_availability(self, slug: str, domain: str = "aws3.link") -> bool:
        """Check if a custom slug is available"""
        try:
            url = f"{self.base_url}/check"
            params = {"slug": slug, "domain": domain}

            response = requests.get(url, params=params, headers=self._get_headers())

            if response.status_code == 200:
                result = response.json()
                return result.get("available", False)
            else:
                logger.error(f"Slug availability check failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Slug availability check error: {e}")
            return False

    def get_click_analytics(
        self, short_code: str, domain: str = "aws3.link", days: int = 30
    ) -> Optional[Dict]:
        """Get detailed click analytics for a URL"""
        try:
            url = f"{self.base_url}/analytics/{short_code}"
            params = {"domain": domain, "days": days}

            response = requests.get(url, params=params, headers=self._get_headers())

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    analytics_data = result.get("data", {})

                    # Format analytics data
                    formatted_data = {
                        "total_clicks": analytics_data.get("total_clicks", 0),
                        "unique_clicks": analytics_data.get("unique_clicks", 0),
                        "countries": analytics_data.get("countries", {}),
                        "browsers": analytics_data.get("browsers", {}),
                        "operating_systems": analytics_data.get("os", {}),
                        "referrers": analytics_data.get("referrers", {}),
                        "devices": analytics_data.get("devices", {}),
                        "daily_clicks": analytics_data.get("daily_clicks", []),
                    }

                    return formatted_data
                else:
                    logger.error(
                        f"Click analytics retrieval failed: {result.get('message')}"
                    )
                    return None
            else:
                logger.error(
                    f"Click analytics retrieval failed: {response.status_code}"
                )
                return None

        except Exception as e:
            logger.error(f"Click analytics retrieval error: {e}")
            return None

    def get_account_stats(self) -> Optional[Dict]:
        """Get account-level statistics"""
        try:
            url = f"{self.base_url}/account/stats"
            response = requests.get(url, headers=self._get_headers())

            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result.get("data", {})
                else:
                    logger.error(
                        f"Account stats retrieval failed: {result.get('message')}"
                    )
                    return None
            else:
                logger.error(f"Account stats retrieval failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Account stats retrieval error: {e}")
            return None
