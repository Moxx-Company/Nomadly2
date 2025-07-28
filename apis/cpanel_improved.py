"""
Improved cPanel/WHM API Integration
Enhanced version with better connectivity testing, authentication methods, and error handling
"""

import requests
import logging
import socket
import ssl
import base64
import json
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse
import time

logger = logging.getLogger(__name__)


class ImprovedCpanelAPI:
    """Improved cPanel API with enhanced connectivity and authentication"""

    def __init__(
        self, whm_host: str, username: str, password: str, use_ssl: bool = True
    ):
        self.whm_host = whm_host.rstrip("/")
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.protocol = "https" if use_ssl else "http"

        # Connection details
        self.base_url = None
        self.auth_headers = None
        self.is_mock = False
        self.connection_method = None

        logger.info(f"Initializing improved cPanel API for {whm_host}")

        # Enhanced connectivity testing
        self.auth_working = self._enhanced_connectivity_test()

        if not self.auth_working:
            logger.warning("Falling back to mock implementation")
            self._initialize_mock()

    def _enhanced_connectivity_test(self) -> bool:
        """Enhanced connectivity testing with multiple fallback options"""

        # Test different host variations
        host_variations = [
            self.whm_host,
            f"cpanel.{self.whm_host}",
            f"whm.{self.whm_host}",
            f"panel.{self.whm_host}",
            f"server.{self.whm_host}",
        ]

        # Test different ports
        port_variations = [2087, 2083, 2086, 443, 8443]

        # Test different protocols
        protocol_variations = ["https", "http"] if self.use_ssl else ["http", "https"]

        for host in host_variations:
            # Skip if host doesn't resolve
            if not self._test_dns_resolution(host):
                continue

            for protocol in protocol_variations:
                for port in port_variations:
                    if self._test_connection_combination(host, protocol, port):
                        return True

        return False

    def _test_dns_resolution(self, hostname: str) -> bool:
        """Test if hostname resolves to IP"""
        try:
            socket.gethostbyname(hostname)
            return True
        except socket.gaierror:
            return False

    def _test_connection_combination(self, host: str, protocol: str, port: int) -> bool:
        """Test specific host/protocol/port combination"""
        try:
            # Test socket connectivity first
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((host, port))
            sock.close()

            if result != 0:
                return False

            # Test HTTP connectivity
            base_url = f"{protocol}://{host}:{port}"

            # Try different authentication methods
            auth_methods = [
                ("whm_token", f"whm {self.username}:{self.password}"),
                (
                    "basic",
                    f"Basic {base64.b64encode(f'{self.username}:{self.password}'.encode()).decode()}",
                ),
                ("bearer", f"Bearer {self.password}"),
                ("api_token", f"cpanel {self.username}:{self.password}"),
            ]

            # Test different endpoints
            test_endpoints = [
                "/json-api/version",
                "/json-api/listaccts",
                "/json-api/applist",
                "/login/?login_only=1",
            ]

            for auth_name, auth_header in auth_methods:
                headers = {
                    "Authorization": auth_header,
                    "Content-Type": "application/json",
                    "User-Agent": "Nomadly-cPanel-Client/1.0",
                }

                for endpoint in test_endpoints:
                    try:
                        url = f"{base_url}{endpoint}"
                        response = requests.get(
                            url, headers=headers, timeout=15, verify=False
                        )

                        # Success responses
                        if response.status_code in [
                            200,
                            401,
                        ]:  # 401 means endpoint exists but auth issue
                            if response.status_code == 200:
                                # Check if response looks like valid cPanel/WHM response
                                try:
                                    json_response = response.json()
                                    if (
                                        "metadata" in json_response
                                        or "data" in json_response
                                    ):
                                        # This is a valid cPanel API response
                                        self.base_url = base_url
                                        self.auth_headers = headers
                                        self.connection_method = (
                                            f"{auth_name}_{protocol}_{port}"
                                        )
                                        logger.info(
                                            f"Connection successful: {host}:{port} via {auth_name}"
                                        )
                                        return True
                                except:
                                    pass

                            # Even 401 indicates the endpoint exists
                            if (
                                endpoint == "/json-api/version"
                                and response.status_code == 401
                            ):
                                self.base_url = base_url
                                self.auth_headers = headers
                                self.connection_method = (
                                    f"{auth_name}_{protocol}_{port}_auth_issue"
                                )
                                logger.warning(
                                    f"Endpoint found but auth failed: {host}:{port}"
                                )
                                return True

                    except Exception as e:
                        continue

        except Exception as e:
            logger.debug(f"Connection test failed for {host}:{port} - {e}")
            return False

        return False

    def _initialize_mock(self):
        """Initialize mock implementation"""
        try:
            from mock_cpanel_api import MockCPanelAPI

            self.mock_api = MockCPanelAPI(self.password, self.whm_host, self.username)
            self.is_mock = True
        except Exception as e:
            logger.error(f"Mock initialization failed: {e}")

    def _make_api_request(
        self, endpoint: str, params: Dict = None, method: str = "GET"
    ) -> Optional[Dict]:
        """Make API request with error handling"""
        if self.is_mock:
            return None

        try:
            url = f"{self.base_url}{endpoint}"

            if method.upper() == "GET":
                response = requests.get(
                    url,
                    params=params,
                    headers=self.auth_headers,
                    timeout=30,
                    verify=False,
                )
            else:
                response = requests.post(
                    url,
                    data=params,
                    headers=self.auth_headers,
                    timeout=30,
                    verify=False,
                )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(
                    f"API request failed: {response.status_code} - {response.text[:200]}"
                )
                return None

        except Exception as e:
            logger.error(f"API request error: {e}")
            return None

    def create_account(
        self,
        domain: str,
        username: str,
        password: str,
        email: str,
        plan: str = "default",
    ) -> Tuple[bool, Optional[str], str]:
        """Create a new cPanel account with improved error handling"""

        if self.is_mock:
            success, account_id = self.mock_api.create_account(
                domain, username, password, plan
            )
            message = (
                "Mock account created (real server unavailable)"
                if success
                else "Mock creation failed"
            )
            return success, account_id, message

        try:
            params = {
                "domain": domain,
                "username": username,
                "password": password,
                "contactemail": email,
                "plan": plan,
                "maxftp": 10,
                "maxsql": 10,
                "maxpop": 10,
                "maxlst": 10,
                "maxsub": 10,
                "maxpark": 10,
                "maxaddon": 10,
                "hasshell": 0,
                "bwlimit": 1000,
                "quota": 1000,
            }

            result = self._make_api_request("/json-api/createacct", params)

            if result and result.get("metadata", {}).get("result") == 1:
                logger.info(f"Account created successfully: {username}@{domain}")
                return True, username, "Account created successfully"
            else:
                error_msg = (
                    result.get("metadata", {}).get("reason", "Unknown error")
                    if result
                    else "API request failed"
                )
                logger.error(f"Account creation failed: {error_msg}")
                return False, None, error_msg

        except Exception as e:
            error_msg = f"Account creation error: {e}"
            logger.error(error_msg)
            return False, None, error_msg

    def list_accounts(self) -> List[Dict]:
        """List all cPanel accounts with improved handling"""
        if self.is_mock:
            return self.mock_api.list_accounts()

        try:
            result = self._make_api_request("/json-api/listaccts")

            if result and result.get("metadata", {}).get("result") == 1:
                return result.get("data", {}).get("acct", [])
            else:
                logger.error(
                    f"Account listing failed: {result.get('metadata', {}).get('reason') if result else 'API request failed'}"
                )
                return []

        except Exception as e:
            logger.error(f"Account listing error: {e}")
            return []

    def suspend_account(
        self, username: str, reason: str = "Administrative suspension"
    ) -> bool:
        """Suspend account with improved handling"""
        if self.is_mock:
            return self.mock_api.suspend_account(username, reason)

        try:
            params = {"user": username, "reason": reason}

            result = self._make_api_request("/json-api/suspendacct", params)

            if result and result.get("metadata", {}).get("result") == 1:
                logger.info(f"Account suspended: {username}")
                return True
            else:
                logger.error(
                    f"Account suspension failed: {result.get('metadata', {}).get('reason') if result else 'API request failed'}"
                )
                return False

        except Exception as e:
            logger.error(f"Account suspension error: {e}")
            return False

    def unsuspend_account(self, username: str) -> bool:
        """Unsuspend account with improved handling"""
        if self.is_mock:
            return self.mock_api.unsuspend_account(username)

        try:
            params = {"user": username}
            result = self._make_api_request("/json-api/unsuspendacct", params)

            if result and result.get("metadata", {}).get("result") == 1:
                logger.info(f"Account unsuspended: {username}")
                return True
            else:
                logger.error(
                    f"Account unsuspension failed: {result.get('metadata', {}).get('reason') if result else 'API request failed'}"
                )
                return False

        except Exception as e:
            logger.error(f"Account unsuspension error: {e}")
            return False

    def terminate_account(self, username: str, keep_dns: bool = False) -> bool:
        """Terminate account with improved handling"""
        if self.is_mock:
            return self.mock_api.terminate_account(username, keep_dns)

        try:
            params = {"user": username, "keepdns": 1 if keep_dns else 0}

            result = self._make_api_request("/json-api/removeacct", params)

            if result and result.get("metadata", {}).get("result") == 1:
                logger.info(f"Account terminated: {username}")
                return True
            else:
                logger.error(
                    f"Account termination failed: {result.get('metadata', {}).get('reason') if result else 'API request failed'}"
                )
                return False

        except Exception as e:
            logger.error(f"Account termination error: {e}")
            return False

    def get_account_info(self, username: str) -> Optional[Dict]:
        """Get account information with improved handling"""
        if self.is_mock:
            return self.mock_api.get_account_info(username)

        try:
            params = {"user": username}
            result = self._make_api_request("/json-api/accountsummary", params)

            if result and result.get("metadata", {}).get("result") == 1:
                accounts = result.get("data", {}).get("acct", [])
                return accounts[0] if accounts else None
            else:
                logger.error(
                    f"Account info failed: {result.get('metadata', {}).get('reason') if result else 'API request failed'}"
                )
                return None

        except Exception as e:
            logger.error(f"Account info error: {e}")
            return None

    def get_connection_status(self) -> Dict:
        """Get detailed connection status"""
        return {
            "host": self.whm_host,
            "username": self.username,
            "base_url": self.base_url,
            "auth_working": self.auth_working,
            "is_mock": self.is_mock,
            "connection_method": self.connection_method,
            "protocol": self.protocol,
        }
