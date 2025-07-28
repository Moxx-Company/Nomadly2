#!/usr/bin/env python3
"""
UI Complexity Reducer
System to reduce the 728 callback handlers and simplify user interface
"""

import re
import ast
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class CallbackAnalysis:
    """Analysis of callback handler complexity"""
    total_callbacks: int
    duplicates: int
    unused_callbacks: int
    complex_patterns: int
    suggested_merges: List[Tuple[str, List[str]]]
    simplification_opportunities: List[str]

@dataclass
class SimplificationRule:
    """Rule for simplifying callback patterns"""
    pattern: str
    replacement: str
    description: str
    complexity_reduction: int

class UIComplexityReducer:
    """System to reduce UI complexity and callback handler count"""
    
    def __init__(self):
        self.simplification_rules = self._initialize_simplification_rules()
        self.callback_patterns = {}
        self.callback_usage = defaultdict(int)
        
    def _initialize_simplification_rules(self) -> List[SimplificationRule]:
        """Initialize callback simplification rules"""
        return [
            SimplificationRule(
                pattern=r'(pay_crypto|pay_balance|pay_wallet)_.*',
                replacement='pay_{type}_{domain}',
                description='Consolidate payment callbacks into unified pattern',
                complexity_reduction=50
            ),
            
            SimplificationRule(
                pattern=r'dns_(create|update|delete)_[a-z]+_.*',
                replacement='dns_action_{record_type}_{domain}',
                description='Merge DNS operation callbacks by action type',
                complexity_reduction=40
            ),
            
            SimplificationRule(
                pattern=r'register_(domain|crypto|balance)_.*',
                replacement='register_{mode}_{domain}',
                description='Unify domain registration callbacks',
                complexity_reduction=30
            ),
            
            SimplificationRule(
                pattern=r'ns_(switch|update|set)_.*',
                replacement='nameserver_{action}_{domain}',
                description='Consolidate nameserver management callbacks',
                complexity_reduction=25
            ),
            
            SimplificationRule(
                pattern=r'admin_(user|domain|payment|system)_.*',
                replacement='admin_{section}_{action}',
                description='Streamline admin panel callbacks',
                complexity_reduction=35
            )
        ]
    
    def analyze_callback_complexity(self, callback_handlers: Dict[str, int]) -> CallbackAnalysis:
        """Analyze callback handler complexity"""
        total_callbacks = len(callback_handlers)
        
        # Find duplicate patterns
        pattern_groups = defaultdict(list)
        for callback in callback_handlers.keys():
            # Extract base pattern (everything before the last underscore)
            if '_' in callback:
                base_pattern = '_'.join(callback.split('_')[:-1])
                pattern_groups[base_pattern].append(callback)
        
        duplicates = sum(len(group) - 1 for group in pattern_groups.values() if len(group) > 1)
        
        # Find potentially unused callbacks (those with very low usage)
        unused_callbacks = sum(1 for usage in callback_handlers.values() if usage == 0)
        
        # Find complex patterns (very long callback names or deeply nested)
        complex_patterns = sum(1 for callback in callback_handlers.keys() 
                             if len(callback) > 30 or callback.count('_') > 4)
        
        # Suggest callback merges
        suggested_merges = []
        for pattern, callbacks in pattern_groups.items():
            if len(callbacks) > 3:  # Groups with more than 3 similar callbacks
                suggested_merges.append((pattern, callbacks))
        
        # Generate simplification opportunities
        simplification_opportunities = self._identify_simplification_opportunities(callback_handlers)
        
        return CallbackAnalysis(
            total_callbacks=total_callbacks,
            duplicates=duplicates,
            unused_callbacks=unused_callbacks,
            complex_patterns=complex_patterns,
            suggested_merges=suggested_merges,
            simplification_opportunities=simplification_opportunities
        )
    
    def _identify_simplification_opportunities(self, callback_handlers: Dict[str, int]) -> List[str]:
        """Identify specific opportunities for simplification"""
        opportunities = []
        callbacks = list(callback_handlers.keys())
        
        # Check for each simplification rule
        for rule in self.simplification_rules:
            matching_callbacks = [cb for cb in callbacks if re.match(rule.pattern, cb)]
            if len(matching_callbacks) >= 3:  # Worth consolidating if 3+ matches
                opportunities.append(
                    f"Consolidate {len(matching_callbacks)} '{rule.pattern}' callbacks into '{rule.replacement}' pattern "
                    f"(Reduces complexity by ~{rule.complexity_reduction} callbacks)"
                )
        
        # Check for domain-specific callback bloat
        domain_callbacks = [cb for cb in callbacks if any(tld in cb for tld in ['.com', '.org', '.net', '.info'])]
        if len(domain_callbacks) > 20:
            opportunities.append(
                f"Replace domain-specific callbacks ({len(domain_callbacks)} found) with dynamic domain parameter parsing"
            )
        
        # Check for action repetition
        action_patterns = defaultdict(list)
        for callback in callbacks:
            if '_' in callback:
                action = callback.split('_')[0]
                action_patterns[action].append(callback)
        
        for action, action_callbacks in action_patterns.items():
            if len(action_callbacks) > 10:
                opportunities.append(
                    f"Consolidate {len(action_callbacks)} '{action}_*' callbacks into dynamic action handler"
                )
        
        return opportunities
    
    def generate_unified_callback_handler(self, callback_group: List[str]) -> str:
        """Generate unified callback handler for a group of similar callbacks"""
        if not callback_group:
            return ""
        
        # Find common prefix
        common_prefix = callback_group[0]
        for callback in callback_group[1:]:
            while not callback.startswith(common_prefix):
                common_prefix = common_prefix[:-1]
        
        # Generate unified handler code
        handler_code = f'''async def handle_{common_prefix}(self, query, callback_data):
    """Unified handler for {common_prefix}* callbacks"""
    await query.answer("⚡ Processing...")
    
    # Parse callback data
    parts = callback_data.split('_')
    
    # Route to specific handler based on callback pattern
'''
        
        # Add routing logic for each callback in the group
        for callback in callback_group:
            unique_part = callback[len(common_prefix):].lstrip('_')
            if unique_part:
                handler_code += f'''    if callback_data == "{callback}":
        await self._handle_{callback.replace('-', '_')}(query, parts)
    '''
        
        handler_code += '''    else:
        logger.warning(f"Unknown callback pattern: {callback_data}")
        await query.edit_message_text(
            "❌ Unknown action. Please use the menu buttons.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]])
        )
'''
        
        return handler_code
    
    def simplify_callback_patterns(self, callbacks: List[str]) -> Dict[str, List[str]]:
        """Group callbacks by simplified patterns"""
        simplified_groups = defaultdict(list)
        
        for callback in callbacks:
            simplified_pattern = self._simplify_callback_pattern(callback)
            simplified_groups[simplified_pattern].append(callback)
        
        return dict(simplified_groups)
    
    def _simplify_callback_pattern(self, callback: str) -> str:
        """Simplify a callback to its essential pattern"""
        # Remove domain-specific parts
        callback = re.sub(r'\.(com|org|net|info|co|io|me|cc)', '', callback)
        
        # Remove UUID-like patterns
        callback = re.sub(r'[a-f0-9]{8}[-_][a-f0-9]{4}[-_][a-f0-9]{4}[-_][a-f0-9]{4}[-_][a-f0-9]{12}', 'ID', callback)
        
        # Remove numeric suffixes
        callback = re.sub(r'_\d+$', '_N', callback)
        
        # Simplify action patterns
        simplifications = {
            r'(create|add|new)_': 'create_',
            r'(update|edit|modify)_': 'update_',
            r'(delete|remove|del)_': 'delete_',
            r'(show|display|view)_': 'show_',
            r'(confirm|verify|validate)_': 'confirm_'
        }
        
        for pattern, replacement in simplifications.items():
            callback = re.sub(pattern, replacement, callback)
        
        return callback
    
    def create_callback_consolidation_plan(self, callbacks: List[str]) -> Dict[str, Any]:
        """Create comprehensive plan for callback consolidation"""
        analysis = self.analyze_callback_complexity({cb: 1 for cb in callbacks})
        simplified_groups = self.simplify_callback_patterns(callbacks)
        
        consolidation_plan = {
            'current_count': len(callbacks),
            'target_count': 0,
            'consolidations': [],
            'estimated_reduction': 0
        }
        
        # Plan consolidations for each group
        for pattern, group_callbacks in simplified_groups.items():
            if len(group_callbacks) > 1:
                consolidation = {
                    'pattern': pattern,
                    'callbacks': group_callbacks,
                    'unified_handler': f"handle_{pattern.replace('-', '_').replace('.', '_')}",
                    'reduction': len(group_callbacks) - 1
                }
                consolidation_plan['consolidations'].append(consolidation)
                consolidation_plan['estimated_reduction'] += consolidation['reduction']
        
        consolidation_plan['target_count'] = (
            consolidation_plan['current_count'] - consolidation_plan['estimated_reduction']
        )
        
        # Add specific recommendations
        consolidation_plan['recommendations'] = [
            "Implement dynamic callback parsing instead of hardcoded handlers",
            "Use callback data parameters for domain names and IDs", 
            "Create generic handlers for CRUD operations",
            "Implement callback routing middleware",
            "Add callback pattern validation and sanitization"
        ]
        
        return consolidation_plan
    
    def generate_dynamic_callback_system(self) -> str:
        """Generate code for dynamic callback system"""
        return '''
class DynamicCallbackHandler:
    """Dynamic callback handler to reduce UI complexity"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.action_handlers = {
            'pay': self._handle_payment,
            'dns': self._handle_dns,
            'register': self._handle_registration,
            'nameserver': self._handle_nameserver,
            'admin': self._handle_admin
        }
    
    async def route_callback(self, query, callback_data: str):
        """Route callback to appropriate handler based on pattern"""
        parts = callback_data.split('_')
        
        if not parts:
            return await self._handle_unknown_callback(query, callback_data)
        
        action = parts[0]
        
        if action in self.action_handlers:
            await self.action_handlers[action](query, parts[1:])
        else:
            await self._handle_unknown_callback(query, callback_data)
    
    async def _handle_payment(self, query, params):
        """Handle all payment-related callbacks"""
        if not params:
            return await self._invalid_params(query)
        
        payment_type = params[0]  # crypto, balance, wallet
        domain = params[1] if len(params) > 1 else None
        
        if payment_type == 'crypto':
            await self.bot.handle_crypto_payment(query, domain)
        elif payment_type == 'balance':
            await self.bot.handle_balance_payment(query, domain)
        elif payment_type == 'wallet':
            await self.bot.handle_wallet_payment(query, domain)
    
    async def _handle_dns(self, query, params):
        """Handle all DNS-related callbacks"""
        if len(params) < 2:
            return await self._invalid_params(query)
        
        action = params[0]      # create, update, delete
        record_type = params[1] # a, cname, mx, txt
        domain = params[2] if len(params) > 2 else None
        
        await self.bot.handle_dns_action(query, action, record_type, domain)
    
    async def _handle_registration(self, query, params):
        """Handle all domain registration callbacks"""
        if not params:
            return await self._invalid_params(query)
        
        reg_type = params[0]  # domain, crypto, balance
        domain = params[1] if len(params) > 1 else None
        nameserver_mode = params[2] if len(params) > 2 else 'cloudflare'
        
        await self.bot.handle_domain_registration(query, reg_type, domain, nameserver_mode)
    
    async def _handle_nameserver(self, query, params):
        """Handle all nameserver-related callbacks"""
        if len(params) < 2:
            return await self._invalid_params(query)
        
        action = params[0]  # switch, update, set
        mode = params[1]    # cloudflare, custom, registrar
        domain = params[2] if len(params) > 2 else None
        
        await self.bot.handle_nameserver_action(query, action, mode, domain)
    
    async def _handle_admin(self, query, params):
        """Handle all admin-related callbacks"""
        if not params:
            return await self._invalid_params(query)
        
        section = params[0]  # user, domain, payment, system
        action = params[1] if len(params) > 1 else 'view'
        
        await self.bot.handle_admin_action(query, section, action)
    
    async def _invalid_params(self, query):
        """Handle invalid callback parameters"""
        await query.edit_message_text(
            "❌ Invalid request parameters.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]])
        )
    
    async def _handle_unknown_callback(self, query, callback_data):
        """Handle unknown callback patterns"""
        logger.warning(f"Unknown callback: {callback_data}")
        await query.edit_message_text(
            "❌ Unknown action. Please use the menu buttons.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")
            ]])
        )
'''

async def test_ui_complexity_reduction():
    """Test UI complexity reduction system"""
    print("🧪 TESTING UI COMPLEXITY REDUCTION")
    print("=" * 50)
    
    reducer = UIComplexityReducer()
    
    # Simulate callback handlers found in testing
    test_callbacks = [
        'pay_crypto_example.com', 'pay_crypto_test.org', 'pay_crypto_domain.net',
        'pay_balance_example.com', 'pay_balance_test.org',
        'dns_create_a_example.com', 'dns_create_cname_test.org', 'dns_create_mx_domain.net',
        'dns_update_a_example.com', 'dns_update_cname_test.org',
        'register_domain_example.com', 'register_crypto_test.org',
        'ns_switch_cloudflare_example.com', 'ns_update_custom_test.org',
        'admin_user_list', 'admin_user_details', 'admin_domain_list'
    ]
    
    # Simulate additional callbacks to reach 728 total
    for i in range(700):
        test_callbacks.append(f'callback_{i % 20}_{i}')
    
    callback_usage = {cb: 1 for cb in test_callbacks}
    
    # Analyze complexity
    analysis = reducer.analyze_callback_complexity(callback_usage)
    print(f"📊 Callback Analysis:")
    print(f"Total callbacks: {analysis.total_callbacks}")
    print(f"Duplicates: {analysis.duplicates}")
    print(f"Complex patterns: {analysis.complex_patterns}")
    print(f"Suggested merges: {len(analysis.suggested_merges)}")
    
    # Show simplification opportunities
    print(f"\n💡 Simplification Opportunities:")
    for opportunity in analysis.simplification_opportunities:
        print(f"  • {opportunity}")
    
    # Create consolidation plan
    plan = reducer.create_callback_consolidation_plan(test_callbacks[:20])  # Sample subset
    print(f"\n📋 Consolidation Plan:")
    print(f"Current count: {plan['current_count']}")
    print(f"Target count: {plan['target_count']}")
    print(f"Estimated reduction: {plan['estimated_reduction']}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_ui_complexity_reduction())