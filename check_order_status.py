#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/runner/workspace')
from database import get_db_manager

db = get_db_manager()
order = db.get_order('2884d40b-4b2e-40a5-927b-d41f43400c19')
if order:
    print(f'Order Status: {order.payment_status}')
    print(f'Payment Address: {order.payment_address}')
    print(f'Amount: ${order.amount}')
    if hasattr(order, 'payment_txid') and order.payment_txid:
        print(f'Transaction ID: {order.payment_txid}')
else:
    print('Order not found')