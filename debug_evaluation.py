"""
Debug script to test the evaluation with different models
Enhanced to test JSON response handling and specialized evaluation cases
"""
import json
import uuid
import requests
from app.utils.nlp_evaluator import NLPEvaluator
from app.services.evaluation_service import EvaluationService

# API endpoint configuration
API_BASE_URL = "http://localhost:5000"
METRICS_ENDPOINT = f"{API_BASE_URL}/evaluate/metrics"

def generate_eval_id():
    """Generate a short evaluation ID for tracking in logs"""
    return str(uuid.uuid4())[:8]

def test_direct_evaluation():
    """
    Test direct evaluation with different responses
    """
    eval_id = generate_eval_id()
    print(f"\n=== DIRECT EVALUATION TEST (ID: {eval_id}) ===\n")
    
    question = "What is the capital of France?"
    
    # Responses with varying degrees of correctness and structure
    responses = {
        "Model1": "The capital of France is Paris.",
        "Model2": "Paris is the capital city of France, located on the Seine River.",
        "Model3": "France's capital is Paris, a major European cultural center."
    }
    
    # Evaluate directly using NLPEvaluator
    print("Testing direct NLPEvaluator calls:")
    for model, response in responses.items():
        print(f"\n--- Testing {model} ---")
        metrics = NLPEvaluator.evaluate_text(question, response)
        print(f"{model} scores: {metrics}")
    
    # Evaluate using the service
    print("\n\nTesting EvaluationService:")
    eval_results = EvaluationService.evaluate_responses(question, responses)
    
    # Verify results are different
    print("\nVerifying results differ:")
    scores = [metrics['overall_score'] for metrics in eval_results.values()]
    if len(set([round(score, 4) for score in scores])) < len(scores):
        print("❌ WARNING: Some scores are identical!")
    else:
        print("✅ All models have different scores")

def test_json_responses():
    """
    Test evaluation with JSON-formatted responses
    """
    eval_id = generate_eval_id()
    print(f"\n=== JSON RESPONSE EVALUATION TEST (ID: {eval_id}) ===\n")
    
    question = "Explain how to make pasta."
    
    # Different formats of JSON responses
    responses = {
        "PlainText": "To make pasta, boil water, add salt, cook pasta until al dente, drain and serve.",
        "SimpleJSON": '{"text": "To make pasta, boil water, add salt, cook pasta until al dente, drain and serve."}',
        "NestedJSON": '{"response": {"content": {"text": "To make pasta, boil water, add salt, cook pasta until al dente, drain and serve."}}}',
        "JSONWithMetadata": '{"text": "To make pasta, boil water, add salt, cook pasta until al dente, drain and serve.", "confidence": 0.95, "model": "gpt-3.5"}'
    }
    
    # Test direct evaluation
    print("Testing direct evaluation with JSON responses:")
    
    # First, manually extract from JSON
    processed_responses = {}
    for model, response in responses.items():
        print(f"\nProcessing {model} response: {response[:50]}{'...' if len(response) > 50 else ''}")
        
        if isinstance(response, str) and response.startswith('{') and response.endswith('}'):
            try:
                parsed = json.loads(response)
                if 'text' in parsed:
                    extracted = parsed['text']
                    print(f"✅ Extracted text from JSON: {extracted[:50]}{'...' if len(extracted) > 50 else ''}")
                    processed_responses[model] = extracted
                elif 'response' in parsed and 'content' in parsed['response'] and 'text' in parsed['response']['content']:
                    extracted = parsed['response']['content']['text']
                    print(f"✅ Extracted text from nested JSON: {extracted[:50]}{'...' if len(extracted) > 50 else ''}")
                    processed_responses[model] = extracted
                else:
                    print("❌ No 'text' field found in JSON")
                    processed_responses[model] = response
            except json.JSONDecodeError:
                print("❌ Invalid JSON format")
                processed_responses[model] = response
        else:
            processed_responses[model] = response
    
    # Evaluate using the service with manually extracted text
    print("\nEvaluating with manually extracted text:")
    manual_results = EvaluationService.evaluate_responses(question, processed_responses)
    
    for model, metrics in manual_results.items():
        print(f"{model}: {metrics['overall_score']:.4f}")
    
    # Now test the service with raw responses (should handle JSON extraction)
    print("\nEvaluating with raw responses (service should handle JSON):")
    auto_results = EvaluationService.evaluate_responses(question, responses)
    
    for model, metrics in auto_results.items():
        print(f"{model}: {metrics['overall_score']:.4f}")
    
    # Verify the two approaches give the same results
    print("\nVerifying both approaches give same results:")
    for model in responses.keys():
        if model in manual_results and model in auto_results:
            manual_score = manual_results[model]['overall_score']
            auto_score = auto_results[model]['overall_score']
            if abs(manual_score - auto_score) < 0.0001:
                print(f"✅ {model}: Both methods give same score: {manual_score:.4f}")
            else:
                print(f"❌ {model}: Scores differ - Manual: {manual_score:.4f}, Auto: {auto_score:.4f}")
                
def test_api_endpoints():
    """Test API endpoints with various response formats"""
    eval_id = generate_eval_id()
    print(f"\n=== API ENDPOINT TEST (ID: {eval_id}) ===\n")
    
    test_data = {
        "question": "What is the best programming language?",
        "responses": {
            "PlainText": "Python is widely considered one of the best programming languages due to its readability and versatility.",
            "JSONFormatted": '{"text": "JavaScript is very popular for web development and has a large ecosystem."}',
            "ShortAnswer": "Python",
        }
    }
    
    try:
        print("Testing /evaluate/metrics endpoint...")
        response = requests.post(METRICS_ENDPOINT, json=test_data)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("✅ API request successful")
            print("\nMetrics for each response:")
            
            for model, metrics in result.get('metrics', {}).items():
                print(f"\n{model}:")
                for name, value in metrics.items():
                    if isinstance(value, float):
                        print(f"  {name}: {value:.4f}")
                    else:
                        print(f"  {name}: {value}")
        else:
            print(f"❌ API request failed: {response.text}")
    except Exception as e:
        print(f"❌ Exception: {str(e)}")

if __name__ == "__main__":
    test_direct_evaluation()
    test_json_responses()
    test_api_endpoints()
