import sympy
import re
from sympy.parsing.sympy_parser import parse_expr
from sympy.core.sympify import SympifyError

class MathEvaluator:
    @staticmethod
    def extract_math_expression(text):
        """Extract potential mathematical expressions from text"""
        # Remove any text inside parentheses that might confuse the parser
        text = re.sub(r'\([^)]*\)', '', text)
        
        # Look for potential mathematical expressions
        expressions = re.findall(r'[-+*/^().\d\s]+', text)
        
        # Return the longest expression (assuming it's the main calculation)
        if expressions:
            return max(expressions, key=len).strip()
        return None
    
    @staticmethod
    def normalize_expression(expression):
        """Normalize mathematical expressions for comparison"""
        if not expression:
            return None
            
        # Remove whitespace
        expression = re.sub(r'\s+', '', expression)
        
        # Replace × with * and ÷ with /
        expression = expression.replace('×', '*').replace('÷', '/')
        
        # Replace ^ with ** for exponentiation
        expression = expression.replace('^', '**')
        
        return expression
    
    @staticmethod
    def evaluate_math_expression(expression):
        """Evaluate a mathematical expression and return the result"""
        try:
            normalized = MathEvaluator.normalize_expression(expression)
            if not normalized:
                return None
                
            result = parse_expr(normalized)
            return float(result.evalf())
        except (SympifyError, ValueError, TypeError) as e:
            print(f"Error evaluating expression '{expression}': {e}")
            return None
    
    @staticmethod
    def check_math_validity(response, question):
        """
        Check the mathematical validity of a response
        Returns a score between 0 and 1
        """
        try:
            # Extract expressions from question and response
            question_expr = MathEvaluator.extract_math_expression(question)
            response_expr = MathEvaluator.extract_math_expression(response)
            
            # If we couldn't extract expressions, give a 0 score
            if not question_expr or not response_expr:
                return 0
            
            # Evaluate both expressions
            expected_result = MathEvaluator.evaluate_math_expression(question_expr)
            actual_result = MathEvaluator.evaluate_math_expression(response_expr)
            
            # If either couldn't be evaluated, give a 0 score
            if expected_result is None or actual_result is None:
                # Check if the response directly contains the correct result
                if str(expected_result) in response:
                    return 1.0
                return 0
            
            # Check how close the results are
            if abs(expected_result - actual_result) < 1e-6:  # Allow for floating point errors
                return 1.0
            
            # If the number is close, give partial credit
            relative_diff = abs(expected_result - actual_result) / max(abs(expected_result), 1e-10)
            if relative_diff < 0.1:
                return 0.8  # Within 10% of correct answer
            elif relative_diff < 0.2:
                return 0.5  # Within 20% of correct answer
            
            return 0.0  # Incorrect answer
            
        except Exception as e:
            print(f"Error in check_math_validity: {e}")
            return 0.0 