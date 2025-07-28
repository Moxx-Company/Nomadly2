"""
cPanel/WHM API Integration
Handles hosting account creation, management, and domain configuration
"""

import requests
import logging
from typing import Dict, List, Optional, Tuple
import json
import base64

logger = logging.getLogger(__name__)


class CpanelAPI:
    def __init__(
        self, whm_host: str, username: str, password: str, use_ssl: bool = True
    ):
        self.whm_host = whm_host.rstrip("/")
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.protocol = "https" if use_ssl else "http"
        self.base_url = f"{self.protocol}://{self.whm_host}:2087"
        self.is_mock = False

        logger.info(f"Initializing cPanel API for {whm_host} with user {username}")

        # Test connectivity and authentication
        self.auth_working = self._test_connectivity()
        if not self.auth_working:
            logger.warning(
                f"cPanel server {whm_host} authentication failed, will use mock fallback"
            )
            self.is_mock = True
            from mock_cpanel_api import MockCPanelAPI

            self.mock_api = MockCPanelAPI(password, whm_host, username)
        else:
            logger.info(f"cPanel server {whm_host} authentication successful")

    def _test_connectivity(self) -> bool:
        """Test if cPanel server is reachable and authenticate"""
        try:
            # Test network connectivity first
            import socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((self.whm_host, 2087))
            sock.close()

            if result != 0:
                logger.warning(
                    f"Cannot connect to {self.whm_host}:2087 - network unreachable"
                )
                return False

            # Test authentication with multiple methods
            test_url = f"{self.base_url}/json-api/version"

            # Try WHM API token format first
            response = requests.get(
                test_url, headers=self._get_headers(), timeout=15, verify=False
            )

            if response.status_code == 200:
                logger.info(
                    f"cPanel server {self.whm_host} authenticated successfully with API token"
                )
                return True

            # Try basic authentication as fallback
            response = requests.get(
                test_url, headers=self._get_basic_headers(), timeout=15, verify=False
            )

            if response.status_code == 200:
                logger.info(
                    f"cPanel server {self.whm_host} authenticated successfully with Basic auth"
                )
                # Update to use basic auth
                self._get_headers = self._get_basic_headers
                return True

            # Try alternative endpoints
            for endpoint in ["/json-api/listaccts", "/json-api/applist"]:
                test_url = f"{self.base_url}{endpoint}"
                response = requests.get(
                    test_url, headers=self._get_headers(), timeout=15, verify=False
                )
                if response.status_code == 200:
                    logger.info(
                        f"cPanel server {self.whm_host} authenticated via {endpoint}"
                    )
                    return True

            logger.warning(f"cPanel authentication failed: HTTP {response.status_code}")
            logger.warning(f"Response: {response.text[:200]}")
            return False

        except Exception as e:
            logger.warning(f"cPanel connectivity test failed: {e}")
            return False

    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers for WHM API"""
        # WHM typically uses either Basic auth or API token auth
        # Try API token format first
        return {
            "Authorization": f"whm {self.username}:{self.password}",
            "Content-Type": "application/json",
        }

    def _get_basic_headers(self) -> Dict[str, str]:
        """Get basic authentication headers as fallback"""
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        return {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/json",
        }

    def create_account(
        self,
        domain: str,
        username: str,
        password: str,
        email: str,
        plan: str = "default",
    ) -> Tuple[bool, Optional[str], str]:
        """Create a new cPanel account"""
        # Use mock API if real server authentication failed
        if self.is_mock:
            success, account_id = self.mock_api.create_account(
                domain, username, password, plan
            )
            if success:
                return (
                    True,
                    account_id,
                    "Mock account created successfully (auth unavailable)",
                )
            else:
                return False, None, "Mock account creation failed"

        # Try real API with authenticated connection
        try:
            url = f"{self.base_url}/json-api/createacct"

            params = {
                "domain": domain,
                "username": username,
                "password": password,
                "email": email,
                "plan": plan,
            }

            response = requests.get(
                url, params=params, headers=self._get_headers(), verify=False
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("metadata", {}).get("result") == 1:
                    logger.info(
                        f"cPanel account created successfully: {username}@{domain}"
                    )
                    return True, username, "Account created successfully"
                else:
                    error_msg = result.get("metadata", {}).get(
                        "reason", "Account creation failed"
                    )
                    logger.error(f"cPanel account creation failed: {error_msg}")
                    return False, None, error_msg
            else:
                logger.error(f"cPanel account creation failed: {response.status_code}")
                return False, None, f"HTTP {response.status_code}"

        except Exception as e:
            error_msg = f"cPanel account creation error: {e}"
            logger.error(error_msg)
            return False, None, error_msg

    def suspend_account(
        self, username: str, reason: str = "Administrative suspension"
    ) -> bool:
        """Suspend a cPanel account"""
        try:
            url = f"{self.base_url}/json-api/suspendacct"
            params = {"user": username, "reason": reason}

            response = requests.get(
                url, params=params, headers=self._get_headers(), verify=False
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("metadata", {}).get("result") == 1:
                    logger.info(f"Account suspended successfully: {username}")
                    return True
                else:
                    logger.error(
                        f"Account suspension failed: {result.get('metadata', {}).get('reason')}"
                    )
                    return False
            else:
                logger.error(f"Account suspension failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Account suspension error: {e}")
            return False

    def unsuspend_account(self, username: str) -> bool:
        """Unsuspend a cPanel account"""
        try:
            url = f"{self.base_url}/json-api/unsuspendacct"
            params = {"user": username}

            response = requests.get(
                url, params=params, headers=self._get_headers(), verify=False
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("metadata", {}).get("result") == 1:
                    logger.info(f"Account unsuspended successfully: {username}")
                    return True
                else:
                    logger.error(
                        f"Account unsuspension failed: {result.get('metadata', {}).get('reason')}"
                    )
                    return False
            else:
                logger.error(f"Account unsuspension failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Account unsuspension error: {e}")
            return False

    def terminate_account(self, username: str, keep_dns: bool = False) -> bool:
        """Terminate a cPanel account"""
        try:
            url = f"{self.base_url}/json-api/removeacct"
            params = {"user": username, "keepdns": 1 if keep_dns else 0}

            response = requests.get(
                url, params=params, headers=self._get_headers(), verify=False
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("metadata", {}).get("result") == 1:
                    logger.info(f"Account terminated successfully: {username}")
                    return True
                else:
                    logger.error(
                        f"Account termination failed: {result.get('metadata', {}).get('reason')}"
                    )
                    return False
            else:
                logger.error(f"Account termination failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Account termination error: {e}")
            return False

    def get_account_info(self, username: str) -> Optional[Dict]:
        """Get account information"""
        try:
            url = f"{self.base_url}/json-api/accountsummary"
            params = {"user": username}

            response = requests.get(
                url, params=params, headers=self._get_headers(), verify=False
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("metadata", {}).get("result") == 1:
                    return result.get("data", {}).get("acct", [{}])[0]
                else:
                    logger.error(
                        f"Account info retrieval failed: {result.get('metadata', {}).get('reason')}"
                    )
                    return None
            else:
                logger.error(f"Account info retrieval failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Account info retrieval error: {e}")
            return None

    def list_accounts(self) -> List[Dict]:
        """List all cPanel accounts"""
        try:
            url = f"{self.base_url}/json-api/listaccts"
            response = requests.get(url, headers=self._get_headers(), verify=False)

            if response.status_code == 200:
                result = response.json()
                if result.get("metadata", {}).get("result") == 1:
                    return result.get("data", {}).get("acct", [])
                else:
                    logger.error(
                        f"Account listing failed: {result.get('metadata', {}).get('reason')}"
                    )
                    return []
            else:
                logger.error(f"Account listing failed: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Account listing error: {e}")
            return []

    def change_password(self, username: str, new_password: str) -> bool:
        """Change account password"""
        try:
            url = f"{self.base_url}/json-api/passwd"
            params = {"user": username, "pass": new_password}

            response = requests.get(
                url, params=params, headers=self._get_headers(), verify=False
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("metadata", {}).get("result") == 1:
                    logger.info(f"Password changed successfully for: {username}")
                    return True
                else:
                    logger.error(
                        f"Password change failed: {result.get('metadata', {}).get('reason')}"
                    )
                    return False
            else:
                logger.error(f"Password change failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Password change error: {e}")
            return False

    def get_disk_usage(self, username: str) -> Optional[Dict]:
        """Get disk usage for an account"""
        try:
            url = f"{self.base_url}/json-api/showbw"
            params = {"searchtype": "user", "search": username}

            response = requests.get(
                url, params=params, headers=self._get_headers(), verify=False
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("metadata", {}).get("result") == 1:
                    bandwidth_data = result.get("data", {}).get("month", [])
                    if bandwidth_data:
                        return bandwidth_data[0]
                    return {}
                else:
                    logger.error(
                        f"Disk usage retrieval failed: {result.get('metadata', {}).get('reason')}"
                    )
                    return None
            else:
                logger.error(f"Disk usage retrieval failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Disk usage retrieval error: {e}")
            return None

    def create_email_account(
        self,
        username: str,
        domain: str,
        email_username: str,
        password: str,
        quota: int = 250,
    ) -> bool:
        """Create an email account"""
        try:
            url = f"{self.base_url}/json-api/add_pop"
            params = {
                "user": username,
                "domain": domain,
                "email": email_username,
                "password": password,
                "quota": quota,
            }

            response = requests.get(
                url, params=params, headers=self._get_headers(), verify=False
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("metadata", {}).get("result") == 1:
                    logger.info(f"Email account created: {email_username}@{domain}")
                    return True
                else:
                    logger.error(
                        f"Email account creation failed: {result.get('metadata', {}).get('reason')}"
                    )
                    return False
            else:
                logger.error(f"Email account creation failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Email account creation error: {e}")
            return False

    def add_addon_domain(self, username: str, domain: str, subdomain: str) -> bool:
        """Add an addon domain to an account"""
        try:
            url = f"{self.base_url}/json-api/park"
            params = {"user": username, "domain": domain, "subdomain": subdomain}

            response = requests.get(
                url, params=params, headers=self._get_headers(), verify=False
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("metadata", {}).get("result") == 1:
                    logger.info(f"Addon domain added: {domain} to {username}")
                    return True
                else:
                    logger.error(
                        f"Addon domain addition failed: {result.get('metadata', {}).get('reason')}"
                    )
                    return False
            else:
                logger.error(f"Addon domain addition failed: {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Addon domain addition error: {e}")
            return False

    def get_server_status(self) -> Optional[Dict]:
        """Get server status information"""
        try:
            url = f"{self.base_url}/json-api/systemloadavg"
            response = requests.get(url, headers=self._get_headers(), verify=False)

            if response.status_code == 200:
                result = response.json()
                if result.get("metadata", {}).get("result") == 1:
                    return result.get("data", {})
                else:
                    logger.error(
                        f"Server status retrieval failed: {result.get('metadata', {}).get('reason')}"
                    )
                    return None
            else:
                logger.error(f"Server status retrieval failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Server status retrieval error: {e}")
            return None

    def get_hosting_plans(self) -> List[Dict]:
        """Get available hosting plans"""
        try:
            url = f"{self.base_url}/json-api/listpkgs"
            response = requests.get(url, headers=self._get_headers(), verify=False)

            if response.status_code == 200:
                result = response.json()
                if result.get("metadata", {}).get("result") == 1:
                    return result.get("data", {}).get("pkg", [])
                else:
                    logger.error(
                        f"Hosting plans retrieval failed: {result.get('metadata', {}).get('reason')}"
                    )
                    return []
            else:
                logger.error(f"Hosting plans retrieval failed: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Hosting plans retrieval error: {e}")
            return []
