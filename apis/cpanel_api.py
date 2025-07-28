"""
cPanel/WHM API Integration
Handles cPanel hosting account creation and management
"""

import os
import requests
import json
import logging
from typing import Dict, Any, Optional
import secrets
import string

logger = logging.getLogger(__name__)


class CpanelAPI:
    def __init__(self):
        self.whm_host = os.getenv("WHM_HOST", "https://your-server.com:2087")
        self.whm_username = os.getenv("WHM_USERNAME")
        self.whm_api_token = os.getenv("WHM_API_TOKEN")

        if not self.whm_username or not self.whm_api_token:
            logger.warning("cPanel/WHM credentials not configured")

        self.headers = {
            "Authorization": f"whm {self.whm_username}:{self.whm_api_token}",
            "Content-Type": "application/json",
        }

        # Hosting plans configuration
        self.HOSTING_PLANS = {
            "basic": {
                "name": "Basic Hosting",
                "price": 9.99,
                "disk_quota": 1000,  # MB
                "bandwidth_quota": 10000,  # MB
                "email_accounts": 10,
                "databases": 5,
                "subdomains": 10,
                "package_name": "basic_plan",
            },
            "professional": {
                "name": "Professional Hosting",
                "price": 19.99,
                "disk_quota": 5000,  # MB
                "bandwidth_quota": 50000,  # MB
                "email_accounts": 50,
                "databases": 20,
                "subdomains": 50,
                "package_name": "pro_plan",
            },
            "business": {
                "name": "Business Hosting",
                "price": 39.99,
                "disk_quota": 10000,  # MB
                "bandwidth_quota": 100000,  # MB
                "email_accounts": 100,
                "databases": 50,
                "subdomains": 100,
                "package_name": "business_plan",
            },
        }

    def generate_credentials(self, domain_name: str) -> Dict[str, str]:
        """Generate secure cPanel credentials"""
        # Create username from domain (first 8 chars + random)
        base_username = domain_name.replace(".", "").replace("-", "")[:6]
        random_suffix = "".join(secrets.choice(string.digits) for _ in range(2))
        username = f"{base_username}{random_suffix}"

        # Generate secure password
        password = "".join(
            secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*")
            for _ in range(12)
        )

        return {"username": username, "password": password}

    def create_account(
        self, domain_name: str, plan_type: str, email: str = None
    ) -> Dict[str, Any]:
        """Create a new cPanel account"""
        try:
            if plan_type not in self.HOSTING_PLANS:
                return {"success": False, "error": "Invalid hosting plan"}

            plan = self.HOSTING_PLANS[plan_type]
            credentials = self.generate_credentials(domain_name)

            # Prepare account creation data
            account_data = {
                "username": credentials["username"],
                "password": credentials["password"],
                "domain": domain_name,
                "plan": plan["package_name"],
                "contactemail": email or "noreply@example.com",
                "quota": plan["disk_quota"],
                "bwlimit": plan["bandwidth_quota"] // 1024,  # Convert to GB
                "maxftp": 10,
                "maxsql": plan["databases"],
                "maxsub": plan["subdomains"],
                "maxpark": 5,
                "maxaddon": 5,
                "hasshell": 0,
                "cgi": 1,
                "frontpage": 0,
                "cpmod": "paper_lantern",
            }

            # Mock account creation for development
            if not self.whm_username or not self.whm_api_token:
                logger.info(f"Mock cPanel account creation for {domain_name}")
                return {
                    "success": True,
                    "username": credentials["username"],
                    "password": credentials["password"],
                    "domain": domain_name,
                    "plan": plan_type,
                    "control_panel_url": f"https://{domain_name}:2083",
                    "server_ip": "192.0.2.100",
                    "account_id": f"mock_{credentials['username']}",
                    "message": "Account created successfully (mock)",
                }

            # Real WHM API call
            response = requests.post(
                f"{self.whm_host}/json-api/createacct",
                headers=self.headers,
                json=account_data,
                verify=False,  # For self-signed certificates
                timeout=API_TIMEOUT,
            )

            if response.status_code == 200:
                data = response.json()

                if data.get("metadata", {}).get("result") == 1:
                    logger.info(
                        f"cPanel account created successfully: {credentials['username']}"
                    )
                    return {
                        "success": True,
                        "username": credentials["username"],
                        "password": credentials["password"],
                        "domain": domain_name,
                        "plan": plan_type,
                        "control_panel_url": f"https://{domain_name}:2083",
                        "server_ip": data.get("data", {}).get("ip", "N/A"),
                        "account_id": credentials["username"],
                        "message": "Account created successfully",
                    }
                else:
                    error_msg = data.get("metadata", {}).get(
                        "reason", "Account creation failed"
                    )
                    logger.error(f"cPanel account creation failed: {error_msg}")
                    return {"success": False, "error": error_msg}
            else:
                error_msg = f"WHM API error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return {"success": False, "error": error_msg}

        except Exception as e:
            error_msg = f"cPanel account creation error: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}

    def suspend_account(self, username: str) -> Dict[str, Any]:
        """Suspend a cPanel account"""
        try:
            if not self.whm_username or not self.whm_api_token:
                logger.info(f"Mock account suspension for {username}")
                return {"success": True, "message": "Account suspended (mock)"}

            response = requests.post(
                f"{self.whm_host}/json-api/suspendacct",
                headers=self.headers,
                json={"user": username, "reason": "Billing suspension"},
                verify=False,
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("metadata", {}).get("result") == 1:
                    return {
                        "success": True,
                        "message": "Account suspended successfully",
                    }
                else:
                    return {
                        "success": False,
                        "error": data.get("metadata", {}).get("reason"),
                    }
            else:
                return {"success": False, "error": f"API error: {response.status_code}"}

        except Exception as e:
            logger.error(f"Account suspension error: {e}")
            return {"success": False, "error": str(e)}

    def unsuspend_account(self, username: str) -> Dict[str, Any]:
        """Unsuspend a cPanel account"""
        try:
            if not self.whm_username or not self.whm_api_token:
                logger.info(f"Mock account unsuspension for {username}")
                return {"success": True, "message": "Account unsuspended (mock)"}

            response = requests.post(
                f"{self.whm_host}/json-api/unsuspendacct",
                headers=self.headers,
                json={"user": username},
                verify=False,
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("metadata", {}).get("result") == 1:
                    return {
                        "success": True,
                        "message": "Account unsuspended successfully",
                    }
                else:
                    return {
                        "success": False,
                        "error": data.get("metadata", {}).get("reason"),
                    }
            else:
                return {"success": False, "error": f"API error: {response.status_code}"}

        except Exception as e:
            logger.error(f"Account unsuspension error: {e}")
            return {"success": False, "error": str(e)}

    def get_account_info(self, username: str) -> Dict[str, Any]:
        """Get cPanel account information"""
        try:
            if not self.whm_username or not self.whm_api_token:
                logger.info(f"Mock account info for {username}")
                return {
                    "success": True,
                    "username": username,
                    "domain": f"{username}.example.com",
                    "status": "active",
                    "disk_used": "150 MB",
                    "disk_limit": "1000 MB",
                    "bandwidth_used": "500 MB",
                    "bandwidth_limit": "10 GB",
                }

            response = requests.get(
                f"{self.whm_host}/json-api/accountsummary",
                headers=self.headers,
                params={"user": username},
                verify=False,
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("metadata", {}).get("result") == 1:
                    account_data = data.get("data", {}).get("acct", [{}])[0]
                    return {
                        "success": True,
                        "username": username,
                        "domain": account_data.get("domain"),
                        "status": account_data.get("suspended", "0") == "0"
                        and "active"
                        or "suspended",
                        "disk_used": account_data.get("diskused"),
                        "disk_limit": account_data.get("disklimit"),
                        "bandwidth_used": account_data.get("totalbytes"),
                        "email_accounts": account_data.get("email_accounts_count"),
                    }
                else:
                    return {
                        "success": False,
                        "error": data.get("metadata", {}).get("reason"),
                    }
            else:
                return {"success": False, "error": f"API error: {response.status_code}"}

        except Exception as e:
            logger.error(f"Get account info error: {e}")
            return {"success": False, "error": str(e)}

    def change_password(self, username: str, new_password: str) -> Dict[str, Any]:
        """Change cPanel account password"""
        try:
            if not self.whm_username or not self.whm_api_token:
                logger.info(f"Mock password change for {username}")
                return {"success": True, "message": "Password changed (mock)"}

            response = requests.post(
                f"{self.whm_host}/json-api/passwd",
                headers=self.headers,
                json={"user": username, "pass": new_password},
                verify=False,
                timeout=30,
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("metadata", {}).get("result") == 1:
                    return {"success": True, "message": "Password changed successfully"}
                else:
                    return {
                        "success": False,
                        "error": data.get("metadata", {}).get("reason"),
                    }
            else:
                return {"success": False, "error": f"API error: {response.status_code}"}

        except Exception as e:
            logger.error(f"Password change error: {e}")
            return {"success": False, "error": str(e)}
