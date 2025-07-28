#!/usr/bin/env python3
"""
Optimize Slow Button Responses
Apply comprehensive fixes to eliminate button responsiveness issues
"""

import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_slow_operations():
    """Find operations that could cause slow button responses"""
    
    print("🔍 FINDING SLOW OPERATIONS IN CALLBACK HANDLERS")
    print("=" * 50)
    
    try:
        with open('nomadly2_bot.py', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ nomadly2_bot.py not found")
        return []
    
    slow_patterns = [
        {
            'name': 'Domain Service Calls',
            'pattern': r'await.*domain_service\..*\(',
            'risk': 'HIGH - API timeouts can cause 8+ second delays'
        },
        {
            'name': 'OpenProvider API',
            'pattern': r'await.*openprovider.*\(',
            'risk': 'HIGH - Domain registration API can timeout'
        },
        {
            'name': 'Cloudflare API', 
            'pattern': r'await.*cloudflare\..*\(',
            'risk': 'MEDIUM - DNS operations usually fast but can timeout'
        },
        {
            'name': 'Database Queries',
            'pattern': r'db_manager\.get_.*\(|db\.get_.*\(',
            'risk': 'LOW - Usually fast but can slow down with large datasets'
        },
        {
            'name': 'Synchronous File Operations',
            'pattern': r'open\(.*\)|with open\(',
            'risk': 'LOW - File I/O can block'
        }
    ]
    
    findings = []
    
    for pattern_info in slow_patterns:
        matches = re.findall(pattern_info['pattern'], content)
        if matches:
            findings.append({
                'type': pattern_info['name'],
                'count': len(matches),
                'risk': pattern_info['risk'],
                'examples': matches[:3]  # First 3 examples
            })
    
    print("📊 SLOW OPERATIONS FOUND:")
    for finding in findings:
        print(f"\n🔍 {finding['type']}:")
        print(f"   📊 Count: {finding['count']} occurrences")
        print(f"   ⚠️ Risk: {finding['risk']}")
        print(f"   🔧 Examples: {finding['examples'][:2]}")
    
    return findings

def analyze_callback_flow_patterns():
    """Analyze callback handler flow patterns for optimization"""
    
    print(f"\n🔄 CALLBACK FLOW ANALYSIS:")
    print("=" * 30)
    
    try:
        with open('nomadly2_bot.py', 'r') as f:
            content = f.read()
    except FileNotFoundError:
        return []
    
    # Find callback handlers with potential issues
    problematic_patterns = []
    
    # Pattern 1: Handlers without immediate acknowledgment
    callback_handlers = re.findall(r'elif.*data.*==.*["\']([^"\']+)["\'].*?:', content)
    no_ack_handlers = []
    
    for handler in callback_handlers:
        # Find the handler block
        handler_pattern = f'elif.*data.*==.*["\']' + re.escape(handler) + r'["\'].*?:(.*?)(?=elif.*data.*==|else:|$)'
        handler_match = re.search(handler_pattern, content, re.DOTALL)
        
        if handler_match:
            handler_content = handler_match.group(1)
            # Check if has immediate acknowledgment
            if 'query.answer(' not in handler_content.split('\n')[0:3]:  # First 3 lines
                no_ack_handlers.append(handler)
    
    if no_ack_handlers:
        problematic_patterns.append({
            'issue': 'Missing Immediate Acknowledgment',
            'count': len(no_ack_handlers),
            'handlers': no_ack_handlers[:5],
            'impact': 'Users think button is unresponsive'
        })
    
    # Pattern 2: API calls before acknowledgment
    api_before_ack = []
    api_patterns = ['domain_service', 'openprovider', 'cloudflare']
    
    for handler in callback_handlers:
        handler_pattern = f'elif.*data.*==.*["\']' + re.escape(handler) + r'["\'].*?:(.*?)(?=elif.*data.*==|else:|$)'
        handler_match = re.search(handler_pattern, content, re.DOTALL)
        
        if handler_match:
            handler_content = handler_match.group(1)
            lines = handler_content.split('\n')
            
            # Find query.answer position
            ack_line = -1
            for i, line in enumerate(lines):
                if 'query.answer(' in line:
                    ack_line = i
                    break
            
            # Check for API calls before acknowledgment
            for i, line in enumerate(lines):
                if i < ack_line or ack_line == -1:
                    for api_pattern in api_patterns:
                        if api_pattern in line and 'await' in line:
                            api_before_ack.append(f"{handler} - {api_pattern}")
                            break
    
    if api_before_ack:
        problematic_patterns.append({
            'issue': 'API Calls Before Acknowledgment',
            'count': len(api_before_ack),
            'handlers': api_before_ack[:5],
            'impact': 'API delays block user feedback'
        })
    
    print("⚠️ PROBLEMATIC PATTERNS:")
    for pattern in problematic_patterns:
        print(f"\n📌 {pattern['issue']}:")
        print(f"   📊 Count: {pattern['count']}")
        print(f"   💥 Impact: {pattern['impact']}")
        print(f"   🔧 Examples: {pattern['handlers'][:3]}")
    
    return problematic_patterns

def generate_optimization_plan():
    """Generate comprehensive optimization plan"""
    
    print(f"\n🚀 OPTIMIZATION PLAN:")
    print("=" * 25)
    
    optimizations = [
        {
            'priority': 'CRITICAL',
            'title': 'Add Missing Acknowledgments',
            'description': 'Add query.answer() as first line in all callback handlers',
            'implementation': 'Insert await query.answer("⚡ Processing...") at start of each handler',
            'impact': 'Eliminates user perception of unresponsive buttons'
        },
        {
            'priority': 'HIGH',
            'title': 'Move API Calls to Background',
            'description': 'Restructure handlers to acknowledge first, then process',
            'implementation': 'Use asyncio.create_task() for background processing',
            'impact': 'API timeouts never block user interface'
        },
        {
            'priority': 'HIGH',
            'title': 'Implement Loading States',
            'description': 'Show processing messages during background operations',
            'implementation': 'Edit messages to show "⏳ Loading..." then update with results',
            'impact': 'Users understand system is working'
        },
        {
            'priority': 'MEDIUM',
            'title': 'Add Fallback Responses', 
            'description': 'Ensure buttons work even if APIs fail',
            'implementation': 'Try-catch blocks with user-friendly error messages',
            'impact': 'Graceful handling of API failures'
        },
        {
            'priority': 'LOW',
            'title': 'Cache Frequent Operations',
            'description': 'Cache domain pricing and DNS record lists',
            'implementation': 'In-memory cache with TTL for API responses',
            'impact': 'Faster response for repeated operations'
        }
    ]
    
    for opt in optimizations:
        priority_emoji = "🔴" if opt['priority'] == 'CRITICAL' else "🟡" if opt['priority'] == 'HIGH' else "🟢"
        print(f"{priority_emoji} {opt['priority']} - {opt['title']}:")
        print(f"   📋 What: {opt['description']}")
        print(f"   🔧 How: {opt['implementation']}")
        print(f"   📈 Impact: {opt['impact']}")
        print()
    
    return optimizations

def main():
    print("Starting comprehensive button optimization analysis...\n")
    
    # Find slow operations
    slow_ops = find_slow_operations()
    
    # Analyze callback flow patterns
    problematic_patterns = analyze_callback_flow_patterns()
    
    # Generate optimization plan
    optimizations = generate_optimization_plan()
    
    print("📊 SUMMARY:")
    print("=" * 15)
    print(f"🐌 Slow Operations: {len(slow_ops)} types found")
    print(f"⚠️ Problematic Patterns: {len(problematic_patterns)} issues")
    print(f"🚀 Optimizations: {len(optimizations)} recommendations")
    
    critical_count = len([o for o in optimizations if o['priority'] == 'CRITICAL'])
    high_count = len([o for o in optimizations if o['priority'] == 'HIGH'])
    
    print(f"🔴 Critical Fixes: {critical_count}")
    print(f"🟡 High Priority: {high_count}")
    
    print(f"\n✅ ANALYSIS COMPLETE")
    print("Ready to implement button responsiveness optimizations")

if __name__ == '__main__':
    main()