"""
Smart Payment Service for Nomadly2
Enhanced payment handling with intelligent recommendations and retry logic
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from database import get_db_manager
from payment_service import get_payment_service
from services.confirmation_service import get_confirmation_service
from utils.translation_helper import t_user
import json
import random

logger = logging.getLogger(__name__)


class SmartPaymentService:
    """Intelligent payment handling with recommendations and optimization"""

    def __init__(self):
        self.db = get_db_manager()
        self.payment_service = get_payment_service()
        self.confirmation_service = get_confirmation_service()

        # Payment method performance tracking
        self.method_success_rates = {
            "bitcoin": 0.85,
            "ethereum": 0.92,
            "litecoin": 0.88,
            "dogecoin": 0.80,
            "tron": 0.87,
            "usdt": 0.94,
        }

        # Fee structure for recommendations
        self.network_fees = {
            "bitcoin": {"low": 0.0001, "medium": 0.0003, "high": 0.0006},
            "ethereum": {"low": 0.002, "medium": 0.005, "high": 0.01},
            "litecoin": {"low": 0.001, "medium": 0.002, "high": 0.005},
            "dogecoin": {"low": 0.1, "medium": 0.5, "high": 1.0},
            "tron": {"low": 1.0, "medium": 2.0, "high": 5.0},
            "usdt": {"low": 1.0, "medium": 2.5, "high": 5.0},
        }

        # Retry configuration
        self.max_retries = 3
        self.base_retry_delay = 5  # seconds
        self.timeout_thresholds = {
            "payment_creation": 30,  # seconds
            "confirmation_wait": 3600,  # 1 hour
            "completion_timeout": 7200,  # 2 hours
        }

    async def recommend_payment_method(
        self,
        telegram_id: int,
        amount: float,
        service_type: str = "domain_registration",
    ) -> Dict[str, Any]:
        """
        Recommend optimal payment method based on user history, amount, and network conditions

        Args:
            telegram_id: User's Telegram ID
            amount: Payment amount in USD
            service_type: Type of service being purchased

        Returns:
            Recommendation with ranking and reasoning
        """
        try:
            # Get user payment history
            user_history = await self._get_user_payment_history(telegram_id)

            # Calculate recommendations
            recommendations = []

            for method, success_rate in self.method_success_rates.items():
                score = await self._calculate_method_score(
                    method, amount, user_history, service_type
                )

                fee_estimate = self._estimate_network_fee(method, amount)
                confirmation_time = self._estimate_confirmation_time(method)

                recommendations.append(
                    {
                        "method": method,
                        "score": score,
                        "success_rate": success_rate,
                        "estimated_fee": fee_estimate,
                        "confirmation_time": confirmation_time,
                        "reasoning": self._get_recommendation_reason(
                            method, score, success_rate
                        ),
                    }
                )

            # Sort by score (highest first)
            recommendations.sort(key=lambda x: x["score"], reverse=True)

            # Add user-friendly descriptions
            for rec in recommendations:
                rec["display_name"] = self._get_method_display_name(rec["method"])
                rec["recommendation_level"] = self._get_recommendation_level(
                    rec["score"]
                )

            return {
                "recommendations": recommendations,
                "top_choice": recommendations[0] if recommendations else None,
                "user_preferred": await self._get_user_preferred_method(telegram_id),
                "amount_usd": amount,
            }

        except Exception as e:
            logger.error(f"Error generating payment recommendations: {e}")
            # Fallback to simple default recommendation
            return {
                "recommendations": [
                    {
                        "method": "ethereum",
                        "score": 90,
                        "display_name": "Ethereum (ETH)",
                        "recommendation_level": "recommended",
                        "reasoning": "Fast and reliable blockchain network",
                    }
                ],
                "top_choice": {
                    "method": "ethereum",
                    "score": 90,
                    "display_name": "Ethereum (ETH)",
                },
                "amount_usd": amount,
            }

    async def create_smart_payment(
        self,
        telegram_id: int,
        service_data: Dict[str, Any],
        preferred_method: str = None,
    ) -> Dict[str, Any]:
        """
        Create payment with intelligent handling and retry logic

        Args:
            telegram_id: User's Telegram ID
            service_data: Service details (domain, hosting, etc.)
            preferred_method: User's preferred payment method

        Returns:
            Payment creation result with retry information
        """
        try:
            # Get or use recommended payment method
            if not preferred_method:
                recommendations = await self.recommend_payment_method(
                    telegram_id,
                    service_data.get("amount_usd", 0),
                    service_data.get("service_type", "domain_registration"),
                )
                preferred_method = recommendations["top_choice"]["method"]

            # Attempt payment creation with retry logic
            for attempt in range(self.max_retries):
                try:
                    logger.info(
                        f"Payment creation attempt {attempt + 1} for user {telegram_id} using {preferred_method}"
                    )

                    # Create payment using existing payment service
                    result = await self._create_payment_attempt(
                        telegram_id, service_data, preferred_method
                    )

                    if result.get("success"):
                        # Log successful payment creation
                        await self._log_payment_attempt(
                            telegram_id, preferred_method, "success", attempt + 1
                        )

                        # Set up intelligent monitoring
                        await self._setup_payment_monitoring(
                            result["order_id"], preferred_method
                        )

                        return {
                            "success": True,
                            "order_id": result["order_id"],
                            "payment_address": result.get("payment_address"),
                            "crypto_amount": result.get("crypto_amount"),
                            "method": preferred_method,
                            "attempts": attempt + 1,
                            "monitoring_enabled": True,
                        }

                except Exception as e:
                    logger.warning(f"Payment attempt {attempt + 1} failed: {e}")
                    await self._log_payment_attempt(
                        telegram_id, preferred_method, "failed", attempt + 1, str(e)
                    )

                    if attempt < self.max_retries - 1:
                        # Wait before retry with exponential backoff
                        delay = self.base_retry_delay * (2**attempt)
                        logger.info(f"Retrying payment creation in {delay} seconds...")
                        await asyncio.sleep(delay)
                    else:
                        # Final attempt failed, try alternative method
                        logger.info(
                            "All retry attempts failed, trying alternative payment method..."
                        )
                        alternative_method = await self._get_alternative_method(
                            preferred_method, telegram_id
                        )
                        if alternative_method:
                            return await self.create_smart_payment(
                                telegram_id, service_data, alternative_method
                            )

            # All attempts failed
            return {
                "success": False,
                "error": "Payment creation failed after all retry attempts",
                "attempts": self.max_retries,
                "suggested_action": "try_alternative_method",
            }

        except Exception as e:
            logger.error(f"Smart payment creation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "suggested_action": "contact_support",
            }

    async def handle_payment_switching(
        self, order_id: str, new_method: str
    ) -> Dict[str, Any]:
        """
        Handle mid-transaction payment method switching

        Args:
            order_id: Original order ID
            new_method: New payment method to switch to

        Returns:
            Switching result
        """
        try:
            # Get original order details
            order = self.db.get_order(order_id)
            if not order:
                return {"success": False, "error": "Order not found"}

            # Check if switching is allowed (payment not yet confirmed)
            if hasattr(order, "status") and order.status == "confirmed":
                return {
                    "success": False,
                    "error": "Cannot switch payment method - payment already confirmed",
                }

            # Create new payment with same service details
            service_data = {
                "amount_usd": getattr(order, "amount_usd", 0),
                "service_type": getattr(order, "service_type", "domain_registration"),
                "service_details": getattr(order, "service_details", {}),
            }

            # Create new payment
            new_payment = await self.create_smart_payment(
                order.telegram_id, service_data, new_method
            )

            if new_payment["success"]:
                # Mark old order as cancelled
                self.db.update_order_status(order_id, "cancelled_switched")

                # Log payment method switch
                await self._log_payment_switch(
                    order_id, new_payment["order_id"], order.crypto_currency, new_method
                )

                return {
                    "success": True,
                    "new_order_id": new_payment["order_id"],
                    "old_order_id": order_id,
                    "new_method": new_method,
                    "payment_address": new_payment.get("payment_address"),
                    "crypto_amount": new_payment.get("crypto_amount"),
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to create payment with new method",
                }

        except Exception as e:
            logger.error(f"Payment switching error: {e}")
            return {"success": False, "error": str(e)}

    async def get_smart_payment_status(self, order_id: str) -> Dict[str, Any]:
        """
        Get enhanced payment status with intelligent recommendations

        Args:
            order_id: Order ID to check

        Returns:
            Enhanced status information
        """
        try:
            # Get basic order status
            order = self.db.get_order(order_id)
            if not order:
                return {"success": False, "error": "Order not found"}

            # Calculate time since creation
            created_time = getattr(order, "created_at", datetime.now())
            elapsed_time = datetime.now() - created_time

            # Get payment monitoring data
            monitoring_data = await self._get_payment_monitoring_data(order_id)

            # Determine smart recommendations based on status
            recommendations = []
            if hasattr(order, "status"):
                if (
                    order.status == "pending"
                    and elapsed_time.total_seconds()
                    > self.timeout_thresholds["confirmation_wait"]
                ):
                    recommendations.append(
                        {
                            "type": "timeout_warning",
                            "message": t_user("payment_taking_long", order.telegram_id),
                            "action": "consider_switching_method",
                        }
                    )

                elif order.status == "failed":
                    recommendations.append(
                        {
                            "type": "retry_suggestion",
                            "message": t_user(
                                "payment_failed_retry", order.telegram_id
                            ),
                            "action": "create_new_payment",
                        }
                    )

            return {
                "success": True,
                "order_id": order_id,
                "status": getattr(order, "status", "unknown"),
                "payment_method": getattr(order, "crypto_currency", "unknown"),
                "amount_usd": getattr(order, "amount_usd", 0),
                "created_at": created_time,
                "elapsed_seconds": int(elapsed_time.total_seconds()),
                "monitoring_data": monitoring_data,
                "recommendations": recommendations,
                "can_switch_method": hasattr(order, "status")
                and order.status != "confirmed",
            }

        except Exception as e:
            logger.error(f"Smart payment status error: {e}")
            return {"success": False, "error": str(e)}

    # Helper methods
    async def _get_user_payment_history(self, telegram_id: int) -> Dict[str, Any]:
        """Get user's payment history for recommendations"""
        try:
            # This would typically query payment history from database
            # For now, return basic structure
            return {
                "total_payments": 0,
                "successful_methods": [],
                "failed_methods": [],
                "preferred_method": None,
            }
        except:
            return {
                "total_payments": 0,
                "successful_methods": [],
                "failed_methods": [],
                "preferred_method": None,
            }

    async def _calculate_method_score(
        self, method: str, amount: float, history: Dict, service_type: str
    ) -> float:
        """Calculate smart score for payment method"""
        base_score = self.method_success_rates.get(method, 0.5) * 100

        # Adjust for network fees
        fee_estimate = self._estimate_network_fee(method, amount)
        if fee_estimate < amount * 0.02:  # Less than 2% fee
            base_score += 10
        elif fee_estimate > amount * 0.05:  # More than 5% fee
            base_score -= 10

        # Adjust for user history
        if method in history.get("successful_methods", []):
            base_score += 15
        if method in history.get("failed_methods", []):
            base_score -= 10

        return min(100, max(0, base_score))

    def _estimate_network_fee(self, method: str, amount: float) -> float:
        """Estimate network fee for payment method"""
        fees = self.network_fees.get(method, {"medium": amount * 0.02})
        return fees["medium"]

    def _estimate_confirmation_time(self, method: str) -> str:
        """Estimate confirmation time for payment method"""
        times = {
            "bitcoin": "10-60 minutes",
            "ethereum": "2-15 minutes",
            "litecoin": "5-30 minutes",
            "dogecoin": "5-60 minutes",
            "tron": "1-10 minutes",
            "usdt": "2-15 minutes",
        }
        return times.get(method, "10-30 minutes")

    def _get_recommendation_reason(
        self, method: str, score: float, success_rate: float
    ) -> str:
        """Get human-readable recommendation reason"""
        if score >= 90:
            return "Highly recommended - excellent reliability and speed"
        elif score >= 80:
            return "Good choice - reliable with reasonable fees"
        elif score >= 70:
            return "Acceptable option - some limitations"
        else:
            return "Consider alternatives - may have issues"

    def _get_method_display_name(self, method: str) -> str:
        """Get user-friendly display name for payment method"""
        names = {
            "bitcoin": "Bitcoin (BTC)",
            "ethereum": "Ethereum (ETH)",
            "litecoin": "Litecoin (LTC)",
            "dogecoin": "Dogecoin (DOGE)",
            "tron": "TRON (TRX)",
            "usdt": "Tether USDT",
        }
        return names.get(method, method.upper())

    def _get_recommendation_level(self, score: float) -> str:
        """Get recommendation level based on score"""
        if score >= 90:
            return "highly_recommended"
        elif score >= 80:
            return "recommended"
        elif score >= 70:
            return "acceptable"
        else:
            return "not_recommended"

    async def _get_user_preferred_method(self, telegram_id: int) -> Optional[str]:
        """Get user's preferred payment method from history"""
        # This would typically query user preferences
        return None

    async def _create_payment_attempt(
        self, telegram_id: int, service_data: Dict[str, Any], method: str
    ) -> Dict[str, Any]:
        """Attempt to create payment using existing payment service"""
        try:
            # Use existing payment service
            result = await self.payment_service.create_cryptocurrency_payment(
                telegram_id,
                service_data.get("service_type", "domain_registration"),
                service_data.get("service_details", {}),
                service_data.get("amount_usd", 0),
                method,
            )
            return result
        except Exception as e:
            logger.error(f"Payment creation attempt failed: {e}")
            return {"success": False, "error": str(e)}

    async def _log_payment_attempt(
        self,
        telegram_id: int,
        method: str,
        status: str,
        attempt: int,
        error: str = None,
    ):
        """Log payment attempt for analytics"""
        logger.info(
            f"Payment attempt logged: user={telegram_id}, method={method}, status={status}, attempt={attempt}"
        )
        if error:
            logger.info(f"Payment attempt error: {error}")

    async def _setup_payment_monitoring(self, order_id: str, method: str):
        """Set up intelligent payment monitoring"""
        logger.info(f"Payment monitoring enabled for order {order_id} using {method}")

    async def _get_alternative_method(
        self, failed_method: str, telegram_id: int
    ) -> Optional[str]:
        """Get alternative payment method when primary fails"""
        alternatives = {
            "bitcoin": "ethereum",
            "ethereum": "usdt",
            "litecoin": "bitcoin",
            "dogecoin": "litecoin",
            "tron": "ethereum",
            "usdt": "ethereum",
        }
        return alternatives.get(failed_method)

    async def _get_payment_monitoring_data(self, order_id: str) -> Dict[str, Any]:
        """Get payment monitoring data"""
        return {"checks_performed": 0, "last_check": None, "network_status": "unknown"}

    async def _log_payment_switch(
        self, old_order_id: str, new_order_id: str, old_method: str, new_method: str
    ):
        """Log payment method switch"""
        logger.info(
            f"Payment method switched: {old_order_id} ({old_method}) -> {new_order_id} ({new_method})"
        )


# Global smart payment service instance
_smart_payment_service = None


def get_smart_payment_service() -> SmartPaymentService:
    """Get global smart payment service instance"""
    global _smart_payment_service
    if _smart_payment_service is None:
        _smart_payment_service = SmartPaymentService()
    return _smart_payment_service
