"""
User State model for Nomadly3 Clean Architecture
Imports from fresh_database.py to maintain single source of truth
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fresh_database import UserState

__all__ = ['UserState']