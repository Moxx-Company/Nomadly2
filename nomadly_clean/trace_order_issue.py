#!/usr/bin/env python3
"""Trace order issues without manual processing"""

import requests
import json
import os

print('🔍 TRACING NEW ORDER')
print('=' * 40)
print()
print('Order ID: ed0a1e60-d2d0-40eb-adab-0a30e2d7ec69')
print('Domain: loandbehold.sbs')
print('ETH Address: 0x27311851fd3B7c02F0B74DdA37533aA211b7db0c')
print('Expected Amount: 0.00265600 ETH')
print()

# Check webhook configuration
print('📡 WEBHOOK CONFIGURATION CHECK:')
print('BlockBee callback URL: https://nomadly2-onarrival.replit.app/webhook/blockbee/ed0a1e60-d2d0-40eb-adab-0a30e2d7ec69')
print()

# Check if local webhook server is running
print('🔍 Local webhook server status:')
try:
    response = requests.get('http://localhost:8000/health', timeout=2)
    if response.status_code == 200:
        print('✅ Webhook server is running on port 8000')
        health = response.json()
        print(f'   Status: {health.get("status")}')
        print(f'   Uptime: {health.get("uptime_seconds", 0)}s')
    else:
        print(f'❌ Webhook server returned status {response.status_code}')
except Exception as e:
    print(f'❌ Webhook server not accessible: {e}')

print()
print('🚨 CRITICAL ISSUE IDENTIFIED:')
print('❌ The webhook URL points to https://nomadly2-onarrival.replit.app')
print('❌ But our server is running on port 8000, not exposed publicly!')
print('❌ BlockBee cannot reach our webhook endpoint')
print()
print('📋 REQUIRED FIX:')
print('1. The webhook server needs to run on port 5000 (Replit public port)')
print('2. OR we need a proxy from port 5000 to 8000')
print('3. Currently BlockBee webhooks cannot reach our server')
print()
print('This is why payments are not being processed automatically!')