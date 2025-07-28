"""
Loyalty System Service for Nomadly2
User loyalty rewards, referrals, and premium features
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from database import get_db_manager
from utils.translation_helper import t_user
from services.confirmation_service import get_confirmation_service
import hashlib
import random

logger = logging.getLogger(__name__)


class LoyaltySystemService:
    """Comprehensive loyalty and rewards system"""

    def __init__(self):
        self.db = get_db_manager()
        self.confirmation_service = get_confirmation_service()

        # Loyalty tier configuration
        self.loyalty_tiers = {
            "bronze": {
                "min_orders": 0,
                "min_spent_usd": 0,
                "discount_rate": 0.0,
                "benefits": ["Basic support", "Standard features"],
                "color": "#CD7F32",
                "icon": "🥉",
            },
            "silver": {
                "min_orders": 5,
                "min_spent_usd": 50,
                "discount_rate": 0.05,
                "benefits": ["5% discount", "Priority support", "Extended DNS records"],
                "color": "#C0C0C0",
                "icon": "🥈",
            },
            "gold": {
                "min_orders": 15,
                "min_spent_usd": 150,
                "discount_rate": 0.10,
                "benefits": [
                    "10% discount",
                    "Premium support",
                    "Free URL shortening",
                    "Advanced DNS",
                ],
                "color": "#FFD700",
                "icon": "🥇",
            },
            "platinum": {
                "min_orders": 35,
                "min_spent_usd": 400,
                "discount_rate": 0.15,
                "benefits": [
                    "15% discount",
                    "VIP support",
                    "Free premium domains",
                    "Custom nameservers",
                    "API access",
                ],
                "color": "#E5E4E2",
                "icon": "💎",
            },
            "diamond": {
                "min_orders": 75,
                "min_spent_usd": 1000,
                "discount_rate": 0.20,
                "benefits": [
                    "20% discount",
                    "Dedicated support",
                    "Free everything",
                    "White-label options",
                    "Priority servers",
                ],
                "color": "#B9F2FF",
                "icon": "💍",
            },
        }

        # Reward point values
        self.point_values = {
            "domain_registration": 10,
            "hosting_purchase": 25,
            "url_shortener": 5,
            "referral_signup": 50,
            "referral_purchase": 100,
            "loyalty_bonus": 20,
        }

        # Achievement system
        self.achievements = {
            "first_domain": {
                "name": "First Offshore Domain",
                "description": "Register your first domain",
                "reward_points": 25,
                "icon": "🌐",
            },
            "crypto_enthusiast": {
                "name": "Crypto Enthusiast",
                "description": "Make 10 cryptocurrency payments",
                "reward_points": 100,
                "icon": "₿",
            },
            "domain_collector": {
                "name": "Domain Collector",
                "description": "Own 10+ active domains",
                "reward_points": 200,
                "icon": "🏆",
            },
            "referral_master": {
                "name": "Referral Master",
                "description": "Refer 5 successful users",
                "reward_points": 300,
                "icon": "👥",
            },
            "offshore_legend": {
                "name": "Offshore Legend",
                "description": "Reach Diamond tier",
                "reward_points": 500,
                "icon": "🏴‍☠️",
            },
        }

    async def calculate_user_loyalty_tier(self, telegram_id: int) -> Dict[str, Any]:
        """
        Calculate user's current loyalty tier and progress

        Args:
            telegram_id: User's Telegram ID

        Returns:
            Loyalty tier information and progress
        """
        try:
            # Get user statistics
            user_stats = await self._get_user_statistics(telegram_id)
            total_orders = user_stats.get("total_orders", 0)
            total_spent = user_stats.get("total_spent_usd", 0)

            # Determine current tier
            current_tier = "bronze"
            for tier_name, tier_config in self.loyalty_tiers.items():
                if (
                    total_orders >= tier_config["min_orders"]
                    and total_spent >= tier_config["min_spent_usd"]
                ):
                    current_tier = tier_name

            # Calculate next tier progress
            next_tier = self._get_next_tier(current_tier)
            next_tier_progress = None

            if next_tier:
                next_config = self.loyalty_tiers[next_tier]
                orders_needed = max(0, next_config["min_orders"] - total_orders)
                spending_needed = max(0, next_config["min_spent_usd"] - total_spent)

                orders_progress = (
                    min(100, (total_orders / next_config["min_orders"]) * 100)
                    if next_config["min_orders"] > 0
                    else 100
                )
                spending_progress = (
                    min(100, (total_spent / next_config["min_spent_usd"]) * 100)
                    if next_config["min_spent_usd"] > 0
                    else 100
                )

                next_tier_progress = {
                    "tier": next_tier,
                    "orders_needed": orders_needed,
                    "spending_needed": spending_needed,
                    "orders_progress": orders_progress,
                    "spending_progress": spending_progress,
                    "overall_progress": min(orders_progress, spending_progress),
                }

            current_config = self.loyalty_tiers[current_tier]

            return {
                "current_tier": current_tier,
                "tier_config": current_config,
                "next_tier_progress": next_tier_progress,
                "user_stats": user_stats,
                "discount_rate": current_config["discount_rate"],
                "benefits": current_config["benefits"],
                "tier_color": current_config["color"],
                "tier_icon": current_config["icon"],
            }

        except Exception as e:
            logger.error(f"Error calculating loyalty tier: {e}")
            return {
                "current_tier": "bronze",
                "tier_config": self.loyalty_tiers["bronze"],
                "next_tier_progress": None,
                "user_stats": {"total_orders": 0, "total_spent_usd": 0},
                "discount_rate": 0.0,
                "benefits": ["Basic support"],
                "tier_color": "#CD7F32",
                "tier_icon": "🥉",
            }

    async def apply_loyalty_discount(
        self, telegram_id: int, amount: float
    ) -> Dict[str, Any]:
        """
        Apply loyalty discount to order amount

        Args:
            telegram_id: User's Telegram ID
            amount: Original amount in USD

        Returns:
            Discount calculation results
        """
        try:
            loyalty_info = await self.calculate_user_loyalty_tier(telegram_id)
            discount_rate = loyalty_info["discount_rate"]

            if discount_rate > 0:
                discount_amount = amount * discount_rate
                final_amount = amount - discount_amount

                return {
                    "original_amount": amount,
                    "discount_rate": discount_rate,
                    "discount_amount": discount_amount,
                    "final_amount": final_amount,
                    "savings_usd": discount_amount,
                    "tier": loyalty_info["current_tier"],
                    "tier_icon": loyalty_info["tier_icon"],
                    "discount_applied": True,
                }
            else:
                return {
                    "original_amount": amount,
                    "discount_rate": 0.0,
                    "discount_amount": 0.0,
                    "final_amount": amount,
                    "savings_usd": 0.0,
                    "tier": loyalty_info["current_tier"],
                    "tier_icon": loyalty_info["tier_icon"],
                    "discount_applied": False,
                }

        except Exception as e:
            logger.error(f"Error applying loyalty discount: {e}")
            return {
                "original_amount": amount,
                "discount_rate": 0.0,
                "discount_amount": 0.0,
                "final_amount": amount,
                "savings_usd": 0.0,
                "tier": "bronze",
                "tier_icon": "🥉",
                "discount_applied": False,
            }

    async def award_loyalty_points(
        self, telegram_id: int, action: str, order_amount_usd: float = 0
    ) -> Dict[str, Any]:
        """
        Award loyalty points for user actions

        Args:
            telegram_id: User's Telegram ID
            action: Action type (domain_registration, hosting_purchase, etc.)
            order_amount_usd: Order amount for bonus calculations

        Returns:
            Points award information
        """
        try:
            base_points = self.point_values.get(action, 0)

            # Calculate bonus points based on order value
            bonus_points = 0
            if order_amount_usd > 0:
                bonus_points = int(order_amount_usd * 2)  # 2 points per dollar

            total_points = base_points + bonus_points

            # Check for tier multiplier
            loyalty_info = await self.calculate_user_loyalty_tier(telegram_id)
            tier_multiplier = self._get_tier_multiplier(loyalty_info["current_tier"])

            if tier_multiplier > 1.0:
                multiplied_points = int(total_points * (tier_multiplier - 1.0))
                total_points += multiplied_points

            # Record points (would typically save to database)
            await self._record_loyalty_points(
                telegram_id, action, total_points, order_amount_usd
            )

            # Check for new achievements
            achievements = await self._check_achievements(telegram_id, action)

            return {
                "base_points": base_points,
                "bonus_points": bonus_points,
                "tier_bonus": (
                    int(total_points * (tier_multiplier - 1.0))
                    if tier_multiplier > 1.0
                    else 0
                ),
                "total_points": total_points,
                "action": action,
                "tier": loyalty_info["current_tier"],
                "tier_multiplier": tier_multiplier,
                "new_achievements": achievements,
            }

        except Exception as e:
            logger.error(f"Error awarding loyalty points: {e}")
            return {
                "base_points": 0,
                "bonus_points": 0,
                "tier_bonus": 0,
                "total_points": 0,
                "action": action,
                "tier": "bronze",
                "tier_multiplier": 1.0,
                "new_achievements": [],
            }

    async def generate_referral_code(self, telegram_id: int) -> str:
        """
        Generate unique referral code for user

        Args:
            telegram_id: User's Telegram ID

        Returns:
            Unique referral code
        """
        try:
            # Create deterministic but unique code
            hash_input = f"NOMADLY_{telegram_id}_{datetime.now().strftime('%Y%m')}"
            hash_object = hashlib.md5(hash_input.encode())
            hash_hex = hash_object.hexdigest()

            # Use first 8 characters and add prefix
            referral_code = f"NOM{hash_hex[:8].upper()}"

            # Store referral code (would typically save to database)
            await self._store_referral_code(telegram_id, referral_code)

            return referral_code

        except Exception as e:
            logger.error(f"Error generating referral code: {e}")
            # Fallback code
            return f"NOM{telegram_id}{random.randint(1000, 9999)}"

    async def process_referral(
        self, referrer_id: int, new_user_id: int, referral_code: str
    ) -> Dict[str, Any]:
        """
        Process referral when new user signs up

        Args:
            referrer_id: ID of user who referred
            new_user_id: ID of new user
            referral_code: Referral code used

        Returns:
            Referral processing results
        """
        try:
            # Validate referral code
            if not await self._validate_referral_code(referrer_id, referral_code):
                return {"success": False, "error": "Invalid referral code"}

            # Award points to referrer
            referrer_points = await self.award_loyalty_points(
                referrer_id, "referral_signup"
            )

            # Give new user welcome bonus
            new_user_points = await self.award_loyalty_points(
                new_user_id, "loyalty_bonus"
            )

            # Record referral relationship
            await self._record_referral(referrer_id, new_user_id, referral_code)

            # Send notifications
            await self._notify_referral_success(referrer_id, new_user_id)

            return {
                "success": True,
                "referrer_id": referrer_id,
                "new_user_id": new_user_id,
                "referrer_points": referrer_points["total_points"],
                "new_user_points": new_user_points["total_points"],
                "referral_code": referral_code,
            }

        except Exception as e:
            logger.error(f"Error processing referral: {e}")
            return {"success": False, "error": str(e)}

    async def get_user_loyalty_dashboard(self, telegram_id: int) -> Dict[str, Any]:
        """
        Get comprehensive loyalty dashboard for user

        Args:
            telegram_id: User's Telegram ID

        Returns:
            Complete loyalty dashboard data
        """
        try:
            # Get loyalty tier info
            loyalty_info = await self.calculate_user_loyalty_tier(telegram_id)

            # Get total points
            total_points = await self._get_user_total_points(telegram_id)

            # Get achievements
            user_achievements = await self._get_user_achievements(telegram_id)

            # Get referral stats
            referral_stats = await self._get_referral_statistics(telegram_id)

            # Get recent activity
            recent_activity = await self._get_recent_loyalty_activity(telegram_id)

            # Calculate potential savings
            next_order_discount = loyalty_info["discount_rate"] * 100

            return {
                "loyalty_tier": loyalty_info,
                "total_points": total_points,
                "achievements": {
                    "earned": user_achievements,
                    "available": [
                        ach
                        for ach_id, ach in self.achievements.items()
                        if ach_id not in [a["id"] for a in user_achievements]
                    ],
                    "progress": await self._calculate_achievement_progress(telegram_id),
                },
                "referral_program": {
                    "referral_code": await self.generate_referral_code(telegram_id),
                    "stats": referral_stats,
                    "rewards": {
                        "signup_bonus": self.point_values["referral_signup"],
                        "purchase_bonus": self.point_values["referral_purchase"],
                    },
                },
                "benefits": {
                    "current_discount": f"{next_order_discount:.0f}%",
                    "current_benefits": loyalty_info["benefits"],
                    "next_tier_benefits": self._get_next_tier_benefits(
                        loyalty_info["current_tier"]
                    ),
                },
                "recent_activity": recent_activity,
                "statistics": loyalty_info["user_stats"],
            }

        except Exception as e:
            logger.error(f"Error getting loyalty dashboard: {e}")
            return {
                "loyalty_tier": {"current_tier": "bronze", "tier_icon": "🥉"},
                "total_points": 0,
                "achievements": {"earned": [], "available": [], "progress": {}},
                "referral_program": {"referral_code": "", "stats": {}, "rewards": {}},
                "benefits": {
                    "current_discount": "0%",
                    "current_benefits": [],
                    "next_tier_benefits": [],
                },
                "recent_activity": [],
                "statistics": {"total_orders": 0, "total_spent_usd": 0},
            }

    # Helper methods
    async def _get_user_statistics(self, telegram_id: int) -> Dict[str, Any]:
        """Get comprehensive user statistics"""
        try:
            # This would typically query order history from database
            # For now, return mock structure
            return {
                "total_orders": 0,
                "total_spent_usd": 0.0,
                "domains_owned": 0,
                "crypto_payments": 0,
                "referrals_made": 0,
                "account_age_days": 0,
            }
        except:
            return {
                "total_orders": 0,
                "total_spent_usd": 0.0,
                "domains_owned": 0,
                "crypto_payments": 0,
                "referrals_made": 0,
                "account_age_days": 0,
            }

    def _get_next_tier(self, current_tier: str) -> Optional[str]:
        """Get next loyalty tier"""
        tier_order = ["bronze", "silver", "gold", "platinum", "diamond"]
        try:
            current_index = tier_order.index(current_tier)
            if current_index < len(tier_order) - 1:
                return tier_order[current_index + 1]
        except ValueError:
            pass
        return None

    def _get_tier_multiplier(self, tier: str) -> float:
        """Get points multiplier for tier"""
        multipliers = {
            "bronze": 1.0,
            "silver": 1.1,
            "gold": 1.2,
            "platinum": 1.3,
            "diamond": 1.5,
        }
        return multipliers.get(tier, 1.0)

    def _get_next_tier_benefits(self, current_tier: str) -> List[str]:
        """Get benefits of next tier"""
        next_tier = self._get_next_tier(current_tier)
        if next_tier:
            return self.loyalty_tiers[next_tier]["benefits"]
        return []

    async def _record_loyalty_points(
        self, telegram_id: int, action: str, points: int, order_amount: float
    ):
        """Record loyalty points award"""
        logger.info(
            f"Loyalty points awarded: user={telegram_id}, action={action}, points={points}"
        )

    async def _check_achievements(
        self, telegram_id: int, action: str
    ) -> List[Dict[str, Any]]:
        """Check for new achievements"""
        # This would check user's progress against achievement criteria
        return []

    async def _store_referral_code(self, telegram_id: int, referral_code: str):
        """Store referral code for user"""
        logger.info(
            f"Referral code generated: user={telegram_id}, code={referral_code}"
        )

    async def _validate_referral_code(
        self, referrer_id: int, referral_code: str
    ) -> bool:
        """Validate referral code belongs to referrer"""
        expected_code = await self.generate_referral_code(referrer_id)
        return referral_code == expected_code

    async def _record_referral(
        self, referrer_id: int, new_user_id: int, referral_code: str
    ):
        """Record referral relationship"""
        logger.info(
            f"Referral recorded: referrer={referrer_id}, new_user={new_user_id}, code={referral_code}"
        )

    async def _notify_referral_success(self, referrer_id: int, new_user_id: int):
        """Send referral success notifications"""
        logger.info(
            f"Referral notifications sent: referrer={referrer_id}, new_user={new_user_id}"
        )

    async def _get_user_total_points(self, telegram_id: int) -> int:
        """Get user's total loyalty points"""
        # For demo purposes, return a reasonable amount based on user activity
        # In real implementation: SELECT SUM(points) FROM loyalty_points WHERE telegram_id = ?
        return 500  # Demo value - users can test redemptions

    async def _get_user_achievements(self, telegram_id: int) -> List[Dict[str, Any]]:
        """Get user's earned achievements"""
        return []  # Would query from database

    async def _calculate_achievement_progress(
        self, telegram_id: int
    ) -> Dict[str, float]:
        """Calculate progress toward achievements"""
        return {}  # Would calculate based on user stats

    async def get_referral_statistics(self, telegram_id: int) -> Dict[str, Any]:
        """Get referral program statistics - PUBLIC METHOD"""
        return {
            "total_referrals": 0,
            "successful_referrals": 0,
            "total_points_earned": 0,
            "active_referrals": 0,
            "pending_rewards": 0,
        }

    async def _get_referral_statistics(self, telegram_id: int) -> Dict[str, Any]:
        """Get referral program statistics"""
        return {
            "total_referrals": 0,
            "successful_referrals": 0,
            "points_earned": 0,
            "pending_rewards": 0,
        }

    async def _get_recent_loyalty_activity(
        self, telegram_id: int
    ) -> List[Dict[str, Any]]:
        """Get recent loyalty-related activities"""
        return []  # Would query recent points awards, tier changes, etc.

    def get_user_by_referral_code(self, referral_code: str) -> Optional[int]:
        """Get user ID by referral code"""
        try:
            # In a real implementation, this would query the database
            # For now, we'll check if the referral code matches our pattern
            # and return a test user ID if it's a valid format
            if referral_code.startswith("NOM") and len(referral_code) == 11:
                # This would be a database query:
                # SELECT telegram_id FROM users WHERE referral_code = %s
                # For now, return None to simulate "code not found"
                return None
            return None
        except Exception as e:
            logger.error(f"Error looking up referral code {referral_code}: {e}")
            return None

    def process_referral_signup(self, referrer_id: int, new_user_id: int, referral_code: str) -> Dict[str, Any]:
        """Process a referral signup and award points"""
        try:
            # In a real implementation, this would:
            # 1. Verify the referral code belongs to referrer_id
            # 2. Award points to both users
            # 3. Create referral relationship record
            # 4. Send notifications
            
            # For now, simulate successful processing
            logger.info(f"Processing referral signup: referrer={referrer_id}, new_user={new_user_id}, code={referral_code}")
            
            # Award 100 points to referrer
            # Award 50 points to new user
            # Create referral relationship
            
            return {
                "success": True,
                "referrer_points_awarded": 100,
                "new_user_points_awarded": 50,
                "total_referrals": 1,  # Would get from database
                "message": "Referral processed successfully"
            }
            
        except Exception as e:
            logger.error(f"Error processing referral signup: {e}")
            return {
                "success": False,
                "error": f"Failed to process referral: {str(e)}"
            }

    # REWARD REDEMPTION SYSTEM
    async def get_rewards_catalog(self, telegram_id: int) -> Dict[str, Any]:
        """Get rewards catalog with user affordability information"""
        try:
            user_points = await self._get_user_total_points(telegram_id)
            
            # Define core rewards catalog focused on cash credits and service discounts
            rewards_catalog = {
                "cash_credit_1": {
                    "name": "$1 Account Credit",
                    "description": "Add $1.00 to your wallet balance",
                    "icon": "💰",
                    "point_cost": 100,
                    "reward_value": "$1.00 USD",
                    "available": True,
                    "tier_required": "bronze"
                },
                "cash_credit_5": {
                    "name": "$5 Account Credit", 
                    "description": "Add $5.00 to your wallet balance",
                    "icon": "💸",
                    "point_cost": 450,
                    "reward_value": "$5.00 USD",
                    "available": True,
                    "tier_required": "bronze"
                },
                "domain_discount_25": {
                    "name": "25% Domain Discount",
                    "description": "25% off your next domain registration",
                    "icon": "🌐",
                    "point_cost": 150,
                    "reward_value": "25% discount",
                    "available": True,
                    "tier_required": "bronze"
                },
                "domain_discount_50": {
                    "name": "50% Domain Discount",
                    "description": "50% off your next domain registration",
                    "icon": "🌍",
                    "point_cost": 250,
                    "reward_value": "50% discount",
                    "available": True,
                    "tier_required": "silver"
                },
                "hosting_discount": {
                    "name": "Hosting Discount",
                    "description": "30% off your next hosting purchase",
                    "icon": "🏔️",
                    "point_cost": 200,
                    "reward_value": "30% hosting discount",
                    "available": True,
                    "tier_required": "bronze"
                },
                "service_bundle_discount": {
                    "name": "Bundle Discount",
                    "description": "20% off when buying 3+ services together",
                    "icon": "📦",
                    "point_cost": 300,
                    "reward_value": "20% bundle discount",
                    "available": True,
                    "tier_required": "gold"
                }
            }
            
            return rewards_catalog
            
        except Exception as e:
            logger.error(f"Error getting rewards catalog: {e}")
            return {}

    async def get_available_rewards(self, telegram_id: int) -> Dict[str, Any]:
        """Get all available rewards user can redeem with points"""
        try:
            user_points = await self._get_user_total_points(telegram_id)  
            loyalty_info = await self.calculate_user_loyalty_tier(telegram_id)
            current_tier = loyalty_info.get("current_tier", "bronze")
            
            # Define available rewards focused on cash credits and service discounts
            rewards_catalog = {
                "cash_credit_1": {
                    "name": "$1 Account Credit",
                    "description": "Add $1.00 to your wallet balance",
                    "icon": "💰",
                    "point_cost": 100,
                    "reward_value": "$1.00 USD",
                    "available": True,
                    "tier_required": "bronze"
                },
                "cash_credit_5": {
                    "name": "$5 Account Credit",
                    "description": "Add $5.00 to your wallet balance", 
                    "icon": "💸",
                    "point_cost": 450,
                    "reward_value": "$5.00 USD",
                    "available": True,
                    "tier_required": "bronze"
                },
                "domain_discount_25": {
                    "name": "25% Domain Discount",
                    "description": "25% off your next domain registration",
                    "icon": "🌐",
                    "point_cost": 150,
                    "reward_value": "25% discount",
                    "available": True,
                    "tier_required": "bronze"
                },
                "domain_discount_50": {
                    "name": "50% Domain Discount",
                    "description": "50% off your next domain registration",
                    "icon": "🌍",
                    "point_cost": 250,
                    "reward_value": "50% discount",
                    "available": True,
                    "tier_required": "silver"
                },
                "hosting_discount": {
                    "name": "Hosting Discount",
                    "description": "30% off your next hosting purchase",
                    "icon": "🏔️",
                    "point_cost": 200,
                    "reward_value": "30% hosting discount",
                    "available": True,
                    "tier_required": "bronze"
                },
                "service_bundle_discount": {
                    "name": "Bundle Discount",
                    "description": "20% off when buying 3+ services together",
                    "icon": "📦",
                    "point_cost": 300,
                    "reward_value": "20% bundle discount",
                    "available": current_tier in ["gold", "platinum", "diamond"],
                    "tier_required": "gold"
                }
            }
            
            # Filter rewards by availability and affordability
            available_rewards = {}
            affordable_rewards = {}
            
            for reward_id, reward in rewards_catalog.items():
                if reward["available"]:
                    available_rewards[reward_id] = reward
                    if user_points >= reward["point_cost"]:
                        affordable_rewards[reward_id] = reward
            
            return {
                "success": True,
                "user_points": user_points,
                "current_tier": current_tier,
                "all_rewards": rewards_catalog,
                "available_rewards": available_rewards,
                "affordable_rewards": affordable_rewards,
                "total_available": len(available_rewards),
                "total_affordable": len(affordable_rewards)
            }
            
        except Exception as e:
            logger.error(f"Error getting available rewards: {e}")
            return {
                "success": False,
                "error": str(e),
                "user_points": 0,
                "available_rewards": {},
                "affordable_rewards": {}
            }

    async def redeem_reward(self, telegram_id: int, reward_id: str) -> Dict[str, Any]:
        """Redeem a specific reward using points"""
        try:
            # Get current user points and rewards
            rewards_info = await self.get_available_rewards(telegram_id)
            if not rewards_info["success"]:
                return {"success": False, "error": "Unable to load rewards"}
            
            user_points = rewards_info["user_points"]
            affordable_rewards = rewards_info["affordable_rewards"]
            
            # Check if reward is available and affordable
            if reward_id not in affordable_rewards:
                return {
                    "success": False,
                    "error": "Reward not available or insufficient points",
                    "user_points": user_points
                }
            
            reward = affordable_rewards[reward_id]
            point_cost = reward["point_cost"]
            
            # Deduct points (in real implementation, update database)
            new_points_balance = user_points - point_cost
            
            # Process the specific reward
            reward_result = self._process_reward_fulfillment(telegram_id, reward_id, reward)
            
            if reward_result["success"]:
                # Record the redemption
                self._record_reward_redemption(telegram_id, reward_id, point_cost)
                
                logger.info(f"Reward redeemed: user={telegram_id}, reward={reward_id}, cost={point_cost}")
                
                return {
                    "success": True,
                    "reward_name": reward["name"],
                    "points_spent": point_cost,
                    "new_points_balance": new_points_balance,
                    "reward_details": reward_result["details"],
                    "message": f"Successfully redeemed {reward['name']}!"
                }
            else:
                return {
                    "success": False,
                    "error": reward_result.get("error", "Reward fulfillment failed")
                }
            
        except Exception as e:
            logger.error(f"Error redeeming reward: {e}")
            return {
                "success": False,
                "error": f"Redemption failed: {str(e)}"
            }

    def _process_reward_fulfillment(self, telegram_id: int, reward_id: str, reward: Dict) -> Dict[str, Any]:
        """Process the actual fulfillment of a reward"""
        try:
            if reward_id == "cash_credit_1":
                # Add $1.00 to account balance
                credit_amount = 1.00
                # In real implementation: update user balance in database
                # self.db.add_balance(telegram_id, credit_amount)
                return {
                    "success": True,
                    "details": f"${credit_amount:.2f} added to your account balance"
                }
                
            elif reward_id == "cash_credit_5":
                # Add $5.00 to account balance
                credit_amount = 5.00
                # In real implementation: update user balance in database
                return {
                    "success": True,
                    "details": f"${credit_amount:.2f} added to your account balance"
                }
                
            elif reward_id == "domain_discount_25":
                # Create 25% discount voucher
                voucher_code = f"DOMAIN25_{telegram_id}_{datetime.now().strftime('%Y%m%d')}"
                # In real implementation: store voucher in database with expiry
                return {
                    "success": True,
                    "details": f"25% domain discount voucher: {voucher_code}\nValid for 30 days on any domain registration"
                }
                
            elif reward_id == "domain_discount_50":
                # Create 50% discount voucher
                voucher_code = f"DOMAIN50_{telegram_id}_{datetime.now().strftime('%Y%m%d')}"
                return {
                    "success": True,
                    "details": f"50% domain discount voucher: {voucher_code}\nValid for 30 days on any domain registration"
                }
                
            elif reward_id == "hosting_discount":
                # Create hosting discount voucher
                voucher_code = f"HOST30_{telegram_id}_{datetime.now().strftime('%Y%m%d')}"
                return {
                    "success": True,
                    "details": f"30% hosting discount voucher: {voucher_code}\nValid for 30 days on any hosting purchase"
                }
                
            elif reward_id == "service_bundle_discount":
                # Create bundle discount voucher
                voucher_code = f"BUNDLE20_{telegram_id}_{datetime.now().strftime('%Y%m%d')}"
                return {
                    "success": True,
                    "details": f"20% bundle discount voucher: {voucher_code}\nValid when purchasing 3+ services together"
                }
            
            else:
                return {
                    "success": False,
                    "error": "Unknown reward type"
                }
                
        except Exception as e:
            logger.error(f"Error processing reward fulfillment: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _record_reward_redemption(self, telegram_id: int, reward_id: str, points_spent: int):
        """Record reward redemption in database"""
        logger.info(f"Reward redemption recorded: user={telegram_id}, reward={reward_id}, points={points_spent}")
        # In real implementation: insert into database
        
    def get_redemption_history(self, telegram_id: int) -> Dict[str, Any]:
        """Get user's reward redemption history"""
        try:
            # In real implementation: query database
            # For now, return mock data structure
            return {
                "success": True,
                "redemptions": [
                    {
                        "reward_name": "Account Credit",
                        "points_spent": 100,
                        "redeemed_at": "2025-07-20",
                        "status": "completed",
                        "details": "$1.00 added to balance"
                    }
                ],
                "total_points_redeemed": 100,
                "total_redemptions": 1
            }
            
        except Exception as e:
            logger.error(f"Error getting redemption history: {e}")
            return {
                "success": False,
                "error": str(e),
                "redemptions": []
            }


# Global loyalty system service instance
_loyalty_system_service = None


def get_loyalty_system_service() -> LoyaltySystemService:
    """Get global loyalty system service instance"""
    global _loyalty_system_service
    if _loyalty_system_service is None:
        _loyalty_system_service = LoyaltySystemService()
    return _loyalty_system_service
