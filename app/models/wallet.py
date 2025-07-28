"""
Wallet models for Nomadly3 Clean Architecture
Imports from fresh_database.py to maintain single source of truth
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fresh_database import Transaction, Order

# Aliases for compatibility with repository layer
WalletTransaction = Transaction

__all__ = ['Transaction', 'Order', 'WalletTransaction']