"""
Enhanced cPanel Integration using cpanel-api SDK
Provides both SDK-based and custom API implementations with intelligent fallback
"""

import logging
import os
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)


class EnhancedCpanelAPI:
    """Enhanced cPanel API with SDK support and intelligent fallback"""

    def __init__(
        self, whm_host: str, username: str, password: str, use_ssl: bool = True
    ):
        self.whm_host = whm_host.rstrip("/")
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.protocol = "https" if use_ssl else "http"

        # Initialize connection methods
        self.sdk_client = None
        self.custom_client = None
        self.is_mock = False
        self.connection_method = None

        logger.info(f"Initializing Enhanced cPanel API for {whm_host}")

        # Try SDK first, then custom implementation, then mock
        self._initialize_connection()

    def _initialize_connection(self):
        """Initialize connection using best available method"""

        # Method 1: Try cpanel-api SDK
        if self._try_sdk_connection():
            self.connection_method = "SDK"
            logger.info("Using cpanel-api SDK for cPanel integration")
            return

        # Method 2: Try custom implementation
        if self._try_custom_connection():
            self.connection_method = "Custom"
            logger.info("Using custom API implementation for cPanel integration")
            return

        # Method 3: Fall back to mock
        self._initialize_mock()
        self.connection_method = "Mock"
        logger.warning("Using mock implementation for cPanel integration")

    def _try_sdk_connection(self) -> bool:
        """Try to connect using cpanel-api SDK"""
        try:
            from cpanel_api import CPanelApi

            # Test with different authentication methods
            auth_methods = [
                ("utoken", self.password),  # API token
                ("password", self.password),  # Password
                ("hash", self.password),  # Hash
            ]

            for auth_type, auth_value in auth_methods:
                try:
                    self.sdk_client = CPanelApi(
                        hostname=self.whm_host,
                        username=self.username,
                        auth_value=auth_value,
                        auth_type=auth_type,
                        ssl=self.use_ssl,
                    )

                    # Test connection with a simple API call
                    result = self.sdk_client.uapi.SSH.get_port()
                    if result:
                        logger.info(
                            f"SDK connection successful with {auth_type} authentication"
                        )
                        return True

                except Exception as e:
                    logger.debug(f"SDK {auth_type} auth failed: {e}")
                    continue

        except ImportError:
            logger.info("cpanel-api SDK not available, trying custom implementation")
        except Exception as e:
            logger.debug(f"SDK connection failed: {e}")

        return False

    def _try_custom_connection(self) -> bool:
        """Try to connect using custom implementation"""
        try:
            from .cpanel import CpanelAPI

            self.custom_client = CpanelAPI(
                whm_host=self.whm_host,
                username=self.username,
                password=self.password,
                use_ssl=self.use_ssl,
            )

            # Return true if authentication worked (not mock)
            return self.custom_client.auth_working and not self.custom_client.is_mock

        except Exception as e:
            logger.debug(f"Custom connection failed: {e}")
            return False

    def _initialize_mock(self):
        """Initialize mock implementation"""
        try:
            from mock_cpanel_api import MockCPanelAPI

            self.mock_client = MockCPanelAPI(
                self.password, self.whm_host, self.username
            )
            self.is_mock = True
        except Exception as e:
            logger.error(f"Mock initialization failed: {e}")

    def create_account(
        self,
        domain: str,
        username: str,
        password: str,
        email: str,
        plan: str = "default",
    ) -> Tuple[bool, Optional[str], str]:
        """Create a new cPanel account using best available method"""

        if self.connection_method == "SDK" and self.sdk_client:
            return self._create_account_sdk(domain, username, password, email, plan)
        elif self.connection_method == "Custom" and self.custom_client:
            return self.custom_client.create_account(
                domain, username, password, email, plan
            )
        elif self.is_mock:
            success, account_id = self.mock_client.create_account(
                domain, username, password, plan
            )
            message = (
                "Mock account created successfully (real server unavailable)"
                if success
                else "Mock account creation failed"
            )
            return success, account_id, message
        else:
            return False, None, "No cPanel connection available"

    def _create_account_sdk(
        self, domain: str, username: str, password: str, email: str, plan: str
    ) -> Tuple[bool, Optional[str], str]:
        """Create account using SDK"""
        try:
            # Use WHM API for account creation
            result = self.sdk_client.whm_api(
                "createacct",
                {
                    "domain": domain,
                    "username": username,
                    "password": password,
                    "contactemail": email,
                    "plan": plan,
                },
            )

            if result and result.get("metadata", {}).get("result") == 1:
                logger.info(f"SDK account created successfully: {username}@{domain}")
                return True, username, "Account created successfully via SDK"
            else:
                error_msg = result.get("metadata", {}).get(
                    "reason", "Account creation failed"
                )
                logger.error(f"SDK account creation failed: {error_msg}")
                return False, None, error_msg

        except Exception as e:
            error_msg = f"SDK account creation error: {e}"
            logger.error(error_msg)
            return False, None, error_msg

    def suspend_account(
        self, username: str, reason: str = "Administrative suspension"
    ) -> bool:
        """Suspend account using best available method"""

        if self.connection_method == "SDK" and self.sdk_client:
            return self._suspend_account_sdk(username, reason)
        elif self.connection_method == "Custom" and self.custom_client:
            return self.custom_client.suspend_account(username, reason)
        elif self.is_mock:
            return self.mock_client.suspend_account(username, reason)
        else:
            return False

    def _suspend_account_sdk(self, username: str, reason: str) -> bool:
        """Suspend account using SDK"""
        try:
            result = self.sdk_client.whm_api(
                "suspendacct", {"user": username, "reason": reason}
            )

            if result and result.get("metadata", {}).get("result") == 1:
                logger.info(f"SDK account suspended: {username}")
                return True
            else:
                logger.error(
                    f"SDK account suspension failed: {result.get('metadata', {}).get('reason')}"
                )
                return False

        except Exception as e:
            logger.error(f"SDK account suspension error: {e}")
            return False

    def unsuspend_account(self, username: str) -> bool:
        """Unsuspend account using best available method"""

        if self.connection_method == "SDK" and self.sdk_client:
            return self._unsuspend_account_sdk(username)
        elif self.connection_method == "Custom" and self.custom_client:
            return self.custom_client.unsuspend_account(username)
        elif self.is_mock:
            return self.mock_client.unsuspend_account(username)
        else:
            return False

    def _unsuspend_account_sdk(self, username: str) -> bool:
        """Unsuspend account using SDK"""
        try:
            result = self.sdk_client.whm_api("unsuspendacct", {"user": username})

            if result and result.get("metadata", {}).get("result") == 1:
                logger.info(f"SDK account unsuspended: {username}")
                return True
            else:
                logger.error(
                    f"SDK account unsuspension failed: {result.get('metadata', {}).get('reason')}"
                )
                return False

        except Exception as e:
            logger.error(f"SDK account unsuspension error: {e}")
            return False

    def terminate_account(self, username: str, keep_dns: bool = False) -> bool:
        """Terminate account using best available method"""

        if self.connection_method == "SDK" and self.sdk_client:
            return self._terminate_account_sdk(username, keep_dns)
        elif self.connection_method == "Custom" and self.custom_client:
            return self.custom_client.terminate_account(username, keep_dns)
        elif self.is_mock:
            return self.mock_client.terminate_account(username, keep_dns)
        else:
            return False

    def _terminate_account_sdk(self, username: str, keep_dns: bool) -> bool:
        """Terminate account using SDK"""
        try:
            result = self.sdk_client.whm_api(
                "removeacct", {"user": username, "keepdns": 1 if keep_dns else 0}
            )

            if result and result.get("metadata", {}).get("result") == 1:
                logger.info(f"SDK account terminated: {username}")
                return True
            else:
                logger.error(
                    f"SDK account termination failed: {result.get('metadata', {}).get('reason')}"
                )
                return False

        except Exception as e:
            logger.error(f"SDK account termination error: {e}")
            return False

    def get_account_info(self, username: str) -> Optional[Dict]:
        """Get account information using best available method"""

        if self.connection_method == "SDK" and self.sdk_client:
            return self._get_account_info_sdk(username)
        elif self.connection_method == "Custom" and self.custom_client:
            return self.custom_client.get_account_info(username)
        elif self.is_mock:
            return self.mock_client.get_account_info(username)
        else:
            return None

    def _get_account_info_sdk(self, username: str) -> Optional[Dict]:
        """Get account info using SDK"""
        try:
            result = self.sdk_client.whm_api("accountsummary", {"user": username})

            if result and result.get("metadata", {}).get("result") == 1:
                return result.get("data", {}).get("acct", [{}])[0]
            else:
                logger.error(
                    f"SDK account info failed: {result.get('metadata', {}).get('reason')}"
                )
                return None

        except Exception as e:
            logger.error(f"SDK account info error: {e}")
            return None

    def list_accounts(self) -> List[Dict]:
        """List accounts using best available method"""

        if self.connection_method == "SDK" and self.sdk_client:
            return self._list_accounts_sdk()
        elif self.connection_method == "Custom" and self.custom_client:
            return self.custom_client.list_accounts()
        elif self.is_mock:
            return self.mock_client.list_accounts()
        else:
            return []

    def _list_accounts_sdk(self) -> List[Dict]:
        """List accounts using SDK"""
        try:
            result = self.sdk_client.whm_api("listaccts")

            if result and result.get("metadata", {}).get("result") == 1:
                return result.get("data", {}).get("acct", [])
            else:
                logger.error(
                    f"SDK account listing failed: {result.get('metadata', {}).get('reason')}"
                )
                return []

        except Exception as e:
            logger.error(f"SDK account listing error: {e}")
            return []

    def get_connection_status(self) -> Dict[str, Any]:
        """Get detailed connection status information"""
        return {
            "method": self.connection_method,
            "host": self.whm_host,
            "username": self.username,
            "is_mock": self.is_mock,
            "sdk_available": self.sdk_client is not None,
            "custom_available": (
                self.custom_client is not None and not self.custom_client.is_mock
                if self.custom_client
                else False
            ),
            "working": not self.is_mock,
        }
