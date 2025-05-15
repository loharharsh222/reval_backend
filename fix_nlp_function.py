#!/usr/bin/env python
"""
Updated NLP Evaluator with fixed indentation and syntax
"""

import os
import shutil
import re

def fix_nlp_evaluator_function():
    """Create a fixed version of the calculate_length_ratio function"""
    
    fixed_function = """    @staticmethod
    def calculate_length_ratio(reference, candidate):
        \"\"\"Calculate length ratio between reference and candidate text\"\"\"
        if not reference or not candidate:
            print("    DEBUG [Length Ratio]: Empty text provided, returning 0.0")
            return 0.0
            
        reference_length = len(NLPEvaluator.preprocess_text(reference))
        candidate_length = len(NLPEvaluator.preprocess_text(candidate))
        print(f"    DEBUG [Length Ratio]: Reference tokens: {reference_length}, Candidate tokens: {candidate_length}")
        
        if reference_length == 0:
            print("    DEBUG [Length Ratio]: Reference length is 0, returning 0.0")
            return 0.0
            
        # Special handling for short prompts
        is_short_prompt = reference_length <= 2
        
        # Penalize if candidate is too short or too long compared to reference
        ratio = candidate_length / max(reference_length, 1)
        print(f"    DEBUG [Length Ratio]: Raw ratio: {ratio:.4f}")
        
        if is_short_prompt:
            # For short prompts like "Hi", we expect responses to be much longer
            # Standard greeting responses are typically 5-20 tokens
            if 3 <= candidate_length <= 30:
                # Perfect range for greeting responses
                print(f"    DEBUG [Length Ratio]: Short prompt with appropriate response length")
                return 1.0
            elif candidate_length > 30:
                # Too verbose for a greeting
                final_ratio = 30 / candidate_length
                print(f"    DEBUG [Length Ratio]: Short prompt with verbose response: {final_ratio:.4f}")
                return final_ratio
            else:
                # Too short even for a greeting
                final_ratio = candidate_length / 5  # Ideal minimum would be 5 tokens
                print(f"    DEBUG [Length Ratio]: Short prompt with too brief response: {final_ratio:.4f}")
                return final_ratio
        else:
            # Normal prompt length handling
            if ratio > 1:
                final_ratio = 1.0 / ratio  # Invert ratio if candidate is longer
                print(f"    DEBUG [Length Ratio]: Candidate is longer, inverting ratio: {final_ratio:.4f}")
                return final_ratio
            return ratio
"""
    
    # Path to the file
    nlp_evaluator_path = os.path.join('app', 'utils', 'nlp_evaluator.py')
    
    if not os.path.exists(nlp_evaluator_path):
        print(f"Error: Could not find {nlp_evaluator_path}")
        return False
    
    # Create a backup
    backup_path = nlp_evaluator_path + '.bak'
    shutil.copy2(nlp_evaluator_path, backup_path)
    print(f"Created backup: {backup_path}")
    
    # Read current file
    with open(nlp_evaluator_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regular expression to find the calculate_length_ratio method
    pattern = r'@staticmethod\s*def calculate_length_ratio\(.*?def'
    
    # Use re.DOTALL to match across line breaks
    if re.search(pattern, content, re.DOTALL):
        # Replace the method with our fixed version
        new_content = re.sub(
            pattern, 
            fixed_function + "\n    @staticmethod\n    def", 
            content, 
            1,  # Replace only first occurrence
            re.DOTALL
        )
        
        # Write the fixed content back
        with open(nlp_evaluator_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"Fixed {nlp_evaluator_path}")
        return True
    else:
        print("Error: Could not find the calculate_length_ratio method")
        return False

if __name__ == "__main__":
    if fix_nlp_evaluator_function():
        print("NLP evaluator fixed successfully!")
    else:
        print("Failed to fix NLP evaluator.")
