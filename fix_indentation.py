#!/usr/bin/env python3
"""Fix indentation issues in nomadly3_clean_bot.py"""

import re

def fix_indentation():
    with open('nomadly3_clean_bot.py', 'r') as f:
        content = f.read()
    
    # Find the problematic section
    lines = content.split('\n')
    
    fixed_lines = []
    in_success_texts = False
    in_lang_dict = False
    
    for i, line in enumerate(lines):
        # Check if we're in the success_texts dictionary
        if 'success_texts = {' in line and 'Multilingual' in lines[i-1]:
            in_success_texts = True
            fixed_lines.append(line)
            continue
            
        if in_success_texts:
            # Fix indentation for language keys
            if line.strip() in ['"en": {', '"fr": {', '"hi": {', '"zh": {', '"es": {']:
                # Language key should have 24 spaces (6 levels * 4)
                fixed_lines.append(' ' * 24 + line.strip())
                in_lang_dict = True
                continue
            elif line.strip() == '},':
                if in_lang_dict:
                    # Closing brace for language dict
                    fixed_lines.append(' ' * 24 + line.strip())
                    in_lang_dict = False
                else:
                    # Closing brace for success_texts
                    fixed_lines.append(' ' * 20 + line.strip())
                    in_success_texts = False
                continue
            elif in_lang_dict and '"title":' in line or '"details":' in line or '"manage_domain":' in line or '"register_more":' in line or '"check_wallet":' in line or '"back_menu":' in line:
                # Keys inside language dict should have 28 spaces (7 levels * 4)
                fixed_lines.append(' ' * 28 + line.strip())
                continue
        
        # For all other lines, keep as is
        fixed_lines.append(line)
    
    # Write back
    with open('nomadly3_clean_bot.py', 'w') as f:
        f.write('\n'.join(fixed_lines))
    
    print("Fixed indentation issues")

if __name__ == "__main__":
    fix_indentation()