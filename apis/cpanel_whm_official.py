"""
Official WHM API Implementation
Based on https://api.docs.cpanel.net/whm/introduction/
Uses correct WHM API format with api.version=1 parameter and URL parameters
"""

import requests
import logging
import urllib.parse
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)


class OfficialWHMAPI:
    """Official WHM API implementation following cpanel.net documentation"""

    def __init__(
        self, whm_host: str, username: str, api_token: str, use_ssl: bool = True
    ):
        self.whm_host = whm_host.rstrip("/")
        self.username = username
        self.api_token = api_token
        self.use_ssl = use_ssl
        self.protocol = "https" if use_ssl else "http"

        # WHM uses port 2087 for SSL, 2086 for non-SSL
        self.port = 2087 if use_ssl else 2086
        self.base_url = f"{self.protocol}://{self.whm_host}:{self.port}"

        logger.info(f"Initializing Official WHM API for {whm_host}:{self.port}")

        # Test connectivity using correct WHM API format
        self.auth_working = self._test_whm_connectivity()

        if not self.auth_working:
            logger.warning("WHM API authentication failed, falling back to mock")
            self._initialize_mock()

    def _test_whm_connectivity(self) -> bool:
        """Test WHM connectivity using official API format with api.version=1"""
        try:
            # Use the correct WHM API endpoint format with api.version=1
            test_url = f"{self.base_url}/json-api/version"

            headers = self._get_whm_headers()
            params = {"api.version": "1"}

            response = requests.get(
                test_url, params=params, headers=headers, timeout=15, verify=False
            )

            logger.info(f"WHM API test response: {response.status_code}")
            logger.info(f"WHM API test URL: {response.url}")

            if response.status_code == 200:
                try:
                    result = response.json()
                    logger.info(f"WHM API response: {result}")
                    if "version" in result or "data" in result or "metadata" in result:
                        logger.info("WHM API authentication successful")
                        return True
                except Exception as e:
                    logger.warning(f"JSON parsing failed: {e}")

            logger.warning(
                f"WHM API test failed: {response.status_code} - {response.text[:500]}"
            )
            return False

        except Exception as e:
            logger.warning(f"WHM connectivity test failed: {e}")
            return False

    def _get_whm_headers(self) -> Dict[str, str]:
        """Get WHM API authentication headers according to official docs"""
        return {
            "Authorization": f"whm {self.username}:{self.api_token}",
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Nomadly-WHM-Client/1.0",
        }

    def _initialize_mock(self):
        """Initialize mock implementation as fallback"""
        try:
            from mock_cpanel_api import MockCPanelAPI

            self.mock_api = MockCPanelAPI(self.api_token, self.whm_host, self.username)
            self.is_mock = True
        except Exception as e:
            logger.error(f"Mock initialization failed: {e}")
            self.is_mock = True
            self.mock_api = None

    def _make_whm_request(
        self, api_function: str, params: Dict = None
    ) -> Optional[Dict]:
        """Make WHM API request using official format with api.version=1"""
        if getattr(self, "is_mock", False):
            return None

        try:
            # WHM API format: /json-api/function_name?api.version=1&param1=value1&param2=value2
            url = f"{self.base_url}/json-api/{api_function}"

            headers = self._get_whm_headers()

            # Add required api.version=1 parameter (CRITICAL FOR WHM API 1)
            request_params = params.copy() if params else {}
            request_params["api.version"] = "1"

            logger.info(
                f"Making WHM API request: {api_function} with params: {request_params}"
            )

            # Use GET with URL parameters (official WHM API style)
            response = requests.get(
                url, params=request_params, headers=headers, timeout=30, verify=False
            )

            logger.info(f"WHM API response: {response.status_code} for {response.url}")

            if response.status_code == 200:
                try:
                    result = response.json()
                    logger.info(f"WHM API success: {api_function}")
                    return result
                except:
                    logger.error(f"WHM API JSON parse error for {api_function}")
                    return None
            else:
                logger.error(
                    f"WHM API request failed: {response.status_code} - {response.text[:500]}"
                )
                return None

        except Exception as e:
            logger.error(f"WHM API request error: {e}")
            return None

    def create_account(
        self,
        domain: str,
        username: str,
        password: str,
        email: str,
        plan: str = "default",
    ) -> Tuple[bool, Optional[str], str]:
        """Create cPanel account using official WHM API with api.version=1"""

        if getattr(self, "is_mock", False):
            if self.mock_api:
                success, account_id = self.mock_api.create_account(
                    domain, username, password, plan
                )
                message = (
                    "Mock account created (WHM server unavailable)"
                    if success
                    else "Mock creation failed"
                )
                return success, account_id, message
            else:
                return False, None, "No WHM connection available"

        try:
            # Official WHM createacct API parameters with api.version=1
            params = {
                "username": username,
                "domain": domain,
                "password": password,
                "contactemail": email,
                "plan": plan,
                "pkgname": plan,
                "quota": 1000,  # MB
                "hasshell": 0,
                "maxftp": 10,
                "maxsql": 10,
                "maxpop": 10,
                "maxlst": 10,
                "maxsub": 10,
                "maxpark": 10,
                "maxaddon": 10,
                "bwlimit": 1000,  # MB
                "cgi": 1,
                "frontpage": 0,
            }

            result = self._make_whm_request("createacct", params)

            if result:
                metadata = result.get("metadata", {})
                if metadata.get("result") == 1:
                    logger.info(
                        f"WHM account created successfully: {username}@{domain}"
                    )
                    return True, username, "Account created successfully via WHM API"
                else:
                    error_msg = metadata.get("reason", "Unknown WHM error")
                    logger.error(f"WHM account creation failed: {error_msg}")
                    return False, None, error_msg
            else:
                return False, None, "WHM API request failed"

        except Exception as e:
            error_msg = f"WHM account creation error: {e}"
            logger.error(error_msg)
            return False, None, error_msg

    def list_accounts(self) -> List[Dict]:
        """List all cPanel accounts using official WHM API with api.version=1"""
        if getattr(self, "is_mock", False):
            return self.mock_api.list_accounts() if self.mock_api else []

        try:
            result = self._make_whm_request("listaccts")

            if result:
                metadata = result.get("metadata", {})
                if metadata.get("result") == 1:
                    return result.get("data", {}).get("acct", [])
                else:
                    logger.error(
                        f"WHM account listing failed: {metadata.get('reason')}"
                    )
                    return []
            else:
                return []

        except Exception as e:
            logger.error(f"WHM account listing error: {e}")
            return []

    def get_server_version(self) -> Optional[str]:
        """Get WHM server version using api.version=1"""
        try:
            result = self._make_whm_request("version")
            if result:
                return result.get(
                    "version", result.get("data", {}).get("version", "Unknown")
                )
            return None
        except Exception as e:
            logger.error(f"WHM version check error: {e}")
            return None

    def suspend_account(
        self, username: str, reason: str = "Administrative suspension"
    ) -> bool:
        """Suspend account using official WHM API with api.version=1"""
        if getattr(self, "is_mock", False):
            return (
                self.mock_api.suspend_account(username, reason)
                if self.mock_api
                else False
            )

        try:
            params = {"user": username, "reason": reason}

            result = self._make_whm_request("suspendacct", params)

            if result:
                metadata = result.get("metadata", {})
                if metadata.get("result") == 1:
                    logger.info(f"WHM account suspended: {username}")
                    return True
                else:
                    logger.error(
                        f"WHM account suspension failed: {metadata.get('reason')}"
                    )
                    return False
            else:
                return False

        except Exception as e:
            logger.error(f"WHM account suspension error: {e}")
            return False

    def unsuspend_account(self, username: str) -> bool:
        """Unsuspend account using official WHM API with api.version=1"""
        if getattr(self, "is_mock", False):
            return self.mock_api.unsuspend_account(username) if self.mock_api else False

        try:
            params = {"user": username}
            result = self._make_whm_request("unsuspendacct", params)

            if result:
                metadata = result.get("metadata", {})
                if metadata.get("result") == 1:
                    logger.info(f"WHM account unsuspended: {username}")
                    return True
                else:
                    logger.error(
                        f"WHM account unsuspension failed: {metadata.get('reason')}"
                    )
                    return False
            else:
                return False

        except Exception as e:
            logger.error(f"WHM account unsuspension error: {e}")
            return False

    def terminate_account(self, username: str, keep_dns: bool = False) -> bool:
        """Terminate account using official WHM API with api.version=1"""
        if getattr(self, "is_mock", False):
            return (
                self.mock_api.terminate_account(username, keep_dns)
                if self.mock_api
                else False
            )

        try:
            params = {"user": username, "keepdns": 1 if keep_dns else 0}

            result = self._make_whm_request("removeacct", params)

            if result:
                metadata = result.get("metadata", {})
                if metadata.get("result") == 1:
                    logger.info(f"WHM account terminated: {username}")
                    return True
                else:
                    logger.error(
                        f"WHM account termination failed: {metadata.get('reason')}"
                    )
                    return False
            else:
                return False

        except Exception as e:
            logger.error(f"WHM account termination error: {e}")
            return False

    def get_account_info(self, username: str) -> Optional[Dict]:
        """Get account information using official WHM API with api.version=1"""
        if getattr(self, "is_mock", False):
            return self.mock_api.get_account_info(username) if self.mock_api else None

        try:
            params = {"user": username}
            result = self._make_whm_request("accountsummary", params)

            if result:
                metadata = result.get("metadata", {})
                if metadata.get("result") == 1:
                    accounts = result.get("data", {}).get("acct", [])
                    return accounts[0] if accounts else None
                else:
                    logger.error(f"WHM account info failed: {metadata.get('reason')}")
                    return None
            else:
                return None

        except Exception as e:
            logger.error(f"WHM account info error: {e}")
            return None

    def get_connection_status(self) -> Dict:
        """Get detailed connection status"""
        return {
            "host": self.whm_host,
            "port": self.port,
            "username": self.username,
            "base_url": self.base_url,
            "auth_working": self.auth_working,
            "is_mock": getattr(self, "is_mock", False),
            "api_type": "Official WHM API with api.version=1",
            "protocol": self.protocol,
        }
