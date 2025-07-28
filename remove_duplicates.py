import re

# Read the file
with open('nomadly3_clean_bot.py', 'r') as f:
    content = f.read()

# Remove the first occurrence of show_my_domains (line 1164)
lines = content.split('\n')

# Find and remove first show_my_domains method (around line 1164)
start_idx = None
end_idx = None
indent_level = None

for i, line in enumerate(lines):
    if i >= 1163 and 'async def show_my_domains(self, query):' in line and '"""Show comprehensive domain portfolio' in lines[i+1]:
        start_idx = i
        indent_level = len(line) - len(line.lstrip())
        break

if start_idx is not None:
    # Find the end of this method
    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        if line.strip() and not line.startswith(' ' * (indent_level + 1)) and not line.startswith('\n'):
            if line.startswith(' ' * indent_level) and 'def ' in line:
                end_idx = i
                break
    
    if end_idx:
        # Remove the duplicate method
        del lines[start_idx:end_idx]
        print(f"Removed first show_my_domains method (lines {start_idx+1}-{end_idx})")

# Find and remove first show_custom_search method (around line 1042)  
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if i >= 1000 and i <= 1100 and 'async def show_custom_search(self, query):' in line:
        start_idx = i
        indent_level = len(line) - len(line.lstrip())
        break

if start_idx is not None:
    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        if line.strip() and not line.startswith(' ' * (indent_level + 1)):
            if line.startswith(' ' * indent_level) and 'def ' in line:
                end_idx = i
                break
    
    if end_idx:
        del lines[start_idx:end_idx]
        print(f"Removed first show_custom_search method (lines {start_idx+1}-{end_idx})")

# Find and remove first handle_wallet_crypto_funding method (around line 1633)
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if i >= 1500 and i <= 1700 and 'async def handle_wallet_crypto_funding(self, query, crypto_type):' in line:
        start_idx = i
        indent_level = len(line) - len(line.lstrip())
        break

if start_idx is not None:
    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        if line.strip() and not line.startswith(' ' * (indent_level + 1)):
            if line.startswith(' ' * indent_level) and 'def ' in line:
                end_idx = i
                break
    
    if end_idx:
        del lines[start_idx:end_idx]
        print(f"Removed first handle_wallet_crypto_funding method (lines {start_idx+1}-{end_idx})")

# Find and remove first credit_wallet_balance method (around line 2236)
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if i >= 2200 and i <= 2300 and 'async def credit_wallet_balance(self, user_id, amount):' in line:
        start_idx = i
        indent_level = len(line) - len(line.lstrip())
        break

if start_idx is not None:
    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        if line.strip() and not line.startswith(' ' * (indent_level + 1)):
            if line.startswith(' ' * indent_level) and 'def ' in line:
                end_idx = i
                break
    
    if end_idx:
        del lines[start_idx:end_idx]
        print(f"Removed first credit_wallet_balance method (lines {start_idx+1}-{end_idx})")

# Find and remove first simulate_domain_payment_amount method (around line 3170)
start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if i >= 3100 and i <= 3200 and 'def simulate_domain_payment_amount(self, expected_price: float) -> float:' in line:
        start_idx = i
        indent_level = len(line) - len(line.lstrip())
        break

if start_idx is not None:
    for i in range(start_idx + 1, len(lines)):
        line = lines[i]
        if line.strip() and not line.startswith(' ' * (indent_level + 1)):
            if line.startswith(' ' * indent_level) and 'def ' in line:
                end_idx = i
                break
    
    if end_idx:
        del lines[start_idx:end_idx]
        print(f"Removed first simulate_domain_payment_amount method (lines {start_idx+1}-{end_idx})")

# Write back the cleaned content
with open('nomadly3_clean_bot.py', 'w') as f:
    f.write('\n'.join(lines))

print("Duplicate method removal completed!")
