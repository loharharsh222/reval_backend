"""
Test script for short prompt handling
Enhanced to test both direct evaluation and API endpoints
"""
import requests
import time
import json
from app.utils.nlp_evaluator import NLPEvaluator

# API endpoint configuration
API_BASE_URL = "http://localhost:5000"
METRICS_ENDPOINT = f"{API_BASE_URL}/evaluate/metrics"
EVALUATION_ENDPOINT = f"{API_BASE_URL}/evaluate"

def test_short_prompts_direct():
    """Test direct evaluation of short prompt responses using NLPEvaluator"""
    
    print("\n=== TESTING SHORT PROMPT EVALUATION (DIRECT) ===\n")
    
    short_prompts = [
        "Hi",
        "Hello",
        "Hey there"
    ]
    
    responses = [
        "Hi there! How can I assist you today?",
        "Hello! I'm an AI assistant. What can I help you with?",
        "Hey! Nice to meet you. What would you like to know?",
        "The capital of France is Paris.",  # Irrelevant response
        "Hello."  # Too short response
    ]
    
    print("Testing short prompts with appropriate and inappropriate responses:\n")
    
    for prompt in short_prompts:
        print(f"\n--- Testing prompt: '{prompt}' ---")
        
        for response in responses:
            print(f"\nResponse: '{response}'")
            metrics = NLPEvaluator.evaluate_text(prompt, response)
            print(f"Overall score: {metrics['overall_score']:.4f}")
            print(f"Coherence: {metrics.get('coherence', 0):.4f}")
            print(f"Token overlap: {metrics.get('token_overlap', 0):.4f}")
            
            # Highlight if this is a good match for a short prompt
            if metrics['overall_score'] > 0.7:
                print("✅ GOOD MATCH for short prompt")
            elif metrics['overall_score'] < 0.4:
                print("❌ POOR MATCH for short prompt")

def test_short_prompts_api():
    """Test API endpoints with short prompts"""
    
    print("\n=== TESTING SHORT PROMPT EVALUATION (API) ===\n")
    
    # Test with different greeting prompts
    test_cases = [
        {
            "name": "Simple Hi",
            "prompt": "Hi",
            "responses": {
                "Formal": "Hello there! How may I assist you today?",
                "Casual": "Hey! What's up?",
                "Elaborate": "Greetings! I hope you're having a wonderful day. How can I help?",
                "NonGreeting": "The weather is nice today.",
                "JSON": '{"text": "Hello! How can I assist you?"}'
            }
        },
        {
            "name": "Simple Hello",
            "prompt": "Hello",
            "responses": {
                "Standard": "Hello! How can I help you today?",
                "Short": "Hi.",
                "Irrelevant": "Paris is the capital of France.",
                "JSON": '{"text": "Hello there!"}'
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n--- Testing {test_case['name']} ---")
        
        test_data = {
            "question": test_case["prompt"],
            "responses": test_case["responses"]
        }
        
        try:
            print("\nTesting /evaluate/metrics endpoint:")
            response = requests.post(METRICS_ENDPOINT, json=test_data)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Metrics evaluation successful")
                
                # Print scores in descending order
                scores = [(model, metrics.get('overall_score', 0)) 
                         for model, metrics in result.get('metrics', {}).items()]
                scores.sort(key=lambda x: x[1], reverse=True)
                
                print("\nRanked responses:")
                for i, (model, score) in enumerate(scores):
                    print(f"{i+1}. {model}: {score:.4f}")
                    
                # Check score variation
                if len(scores) > 1:
                    min_score = min(s[1] for s in scores)
                    max_score = max(s[1] for s in scores)
                    score_range = max_score - min_score
                    print(f"\nScore range: {score_range:.4f}")
                    
                    if score_range < 0.1:
                        print("⚠️ WARNING: Low score variation - models received very similar scores")
                    else:
                        print("✅ Good score variation")
            else:
                print(f"❌ API Error: {response.status_code}")
                print(response.text)
                
            # Add a small delay before next call
            time.sleep(1)
            
        except Exception as e:
            print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_short_prompts_direct()
    test_short_prompts_api()
