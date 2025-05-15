#!/usr/bin/env python
"""
Fix script to repair any syntax issues in the NLP evaluator file
"""
import os
import re

def fix_nlp_evaluator_syntax():
    """Fix syntax errors in the NLP evaluator file"""
    
    nlp_evaluator_path = os.path.join('app', 'utils', 'nlp_evaluator.py')
    
    if not os.path.exists(nlp_evaluator_path):
        print(f"Error: Could not find {nlp_evaluator_path}")
        return False
        
    print(f"Fixing syntax issues in {nlp_evaluator_path}...")
    
    with open(nlp_evaluator_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Fix #1: Fix decorator placement errors (return value@staticmethod)
    pattern = r'return ([^@\n]+)@staticmethod'
    replacement = r'return \1\n\n    @staticmethod'
    content = re.sub(pattern, replacement, content)
    
    # Fix #2: Fix missing newlines before decorators
    pattern = r'(\S)\s+@staticmethod'
    replacement = r'\1\n\n    @staticmethod'
    content = re.sub(pattern, replacement, content)
    
    # Fix #3: Fix indentation issues with decorators
    pattern = r'\n(\s*)@staticmethod'
    replacement = r'\n\1@staticmethod'
    content = re.sub(pattern, replacement, content)
    
    # Write fixed content back to file
    with open(nlp_evaluator_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"✅ Fixed syntax issues in {nlp_evaluator_path}")
    return True
    
if __name__ == "__main__":
    if fix_nlp_evaluator_syntax():
        print("Syntax fixes completed successfully.")
    else:
        print("Failed to apply syntax fixes.")
