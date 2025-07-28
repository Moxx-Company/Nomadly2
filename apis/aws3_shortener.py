"""
AWS3.link URL shortener API client
"""

import os
import logging
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class AWS3UrlShortener:
    """AWS3.link URL shortener API client"""

    def __init__(self):
        """Initialize AWS3 URL shortener client"""
        self.api_key = os.getenv("AWS3_API_KEY")
        self.base_url = "https://api.aws3.link"
        self.headers = {"x-api-key": self.api_key, "Content-Type": "application/json"}

        if not self.api_key:
            logger.warning(
                "AWS3_API_KEY not found - URL shortening will not be available"
            )

    def is_available(self) -> bool:
        """Check if AWS3 service is available"""
        return bool(self.api_key)

    def shorten_url(
        self,
        long_url: str,
        custom_domain: Optional[str] = None,
        custom_slug: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Shorten a URL using AWS3.link service

        Args:
            long_url: The destination URL to shorten
            custom_domain: Custom domain to use (aws3.link, goog.link, an.si)
            custom_slug: Custom slug for the shortened URL

        Returns:
            Dict with success status and shortened URL data
        """
        if not self.api_key:
            return {"success": False, "error": "AWS3 API key not configured"}

        # Prepare request body
        body = {"longUrl": long_url}

        # Add custom domain if specified
        if custom_domain:
            body["domain"] = custom_domain

        # Add custom slug if specified
        if custom_slug:
            body["customSlug"] = custom_slug

        try:
            response = requests.post(
                f"{self.base_url}/shorten", headers=self.headers, json=body, timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                logger.info(
                    f"URL shortened successfully: {long_url} -> {data.get('shortUrl')}"
                )
                return {
                    "success": True,
                    "short_url": data.get("shortUrl"),
                    "slug": data.get("metadata", {}).get("slug"),
                    "domain": "aws3.link",
                }
            else:
                error_msg = f"AWS3 API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}

        except requests.RequestException as e:
            error_msg = f"AWS3 API request failed: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def update_url(self, slug: str, new_long_url: str) -> Dict[str, Any]:
        """
        Update the destination URL for an existing shortened URL

        Args:
            slug: The slug of the shortened URL to update
            new_long_url: The new destination URL

        Returns:
            Dict with success status and update result
        """
        if not self.api_key:
            return {"success": False, "error": "AWS3 API key not configured"}

        try:
            # Based on API testing, use POST /update endpoint with newLongUrl parameter
            response = requests.post(
                f"{self.base_url}/update",
                headers=self.headers,
                json={"slug": slug, "newLongUrl": new_long_url},
                timeout=30,
            )

            logger.info(
                f"AWS3 update request: POST /update with slug={slug}, newLongUrl={new_long_url}"
            )
            logger.info(
                f"AWS3 update response: {response.status_code} - {response.text[:200]}"
            )

            if response.status_code == 200:
                data = response.json()
                logger.info(f"URL updated successfully: {slug} -> {new_long_url}")
                return {
                    "success": True,
                    "updated_url": data.get("shortUrl"),
                    "new_destination": new_long_url,
                }
            else:
                error_msg = (
                    f"AWS3 API update error: {response.status_code} - {response.text}"
                )
                logger.error(error_msg)
                return {"success": False, "error": error_msg}

        except requests.RequestException as e:
            error_msg = f"AWS3 API update request failed: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
