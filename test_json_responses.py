#!/usr/bin/env python
# test_json_responses.py - Test JSON response handling in the evaluation API

import requests
import json
import time

# Configuration
API_BASE_URL = "http://localhost:5000"  # Update this if your server runs on a different URL
METRICS_ENDPOINT = f"{API_BASE_URL}/evaluate/metrics"
EVALUATION_ENDPOINT = f"{API_BASE_URL}/evaluate"

# Test data with different response formats
test_data = {
    "question": "What is 5 + 3 * 2?",
    "responses": {
        "PlainText": "The answer is 11 because multiplication has precedence over addition.",
        "JSONText": '{"text": "The answer is 11 because multiplication has precedence over addition."}',
        "PartialJSON": '{"text": "The answer is 11", "confidence": 0.95}',
        "InvalidJSON": '{text: The answer is 11}',  # Invalid JSON but should be handled gracefully
        "ShortResponse": "11"
    }
}

def test_metrics_endpoint():
    """Test the /evaluate/metrics endpoint with different response formats"""
    print("\n" + "="*80)
    print("TESTING METRICS ENDPOINT WITH JSON RESPONSES")
    print("="*80)
    
    try:
        response = requests.post(METRICS_ENDPOINT, json=test_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\nSUCCESS: Metrics evaluation completed")
            print("\nMETRICS RESULTS:")
            for model, metrics in result.get('metrics', {}).items():
                print(f"\n{model}:")
                for metric_name, value in metrics.items():
                    # Format floating point metrics nicely
                    if isinstance(value, float):
                        print(f"  {metric_name}: {value:.4f}")
                    else:
                        print(f"  {metric_name}: {value}")
                
            # Check for identical scores
            if len(result.get('metrics', {})) > 1:
                scores = [m.get('overall_score', 0) for m in result.get('metrics', {}).values()]
                if len(set([round(s, 4) for s in scores])) == 1:
                    print("\nWARNING: All models received identical scores!")
                else:
                    print("\nSUCCESS: Models received different scores.")
                    
        else:
            print(f"ERROR: Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Exception occurred: {str(e)}")

def test_evaluation_endpoint():
    """Test the /evaluate endpoint with different response formats"""
    print("\n" + "="*80)
    print("TESTING EVALUATION ENDPOINT WITH JSON RESPONSES")
    print("="*80)
    
    try:
        response = requests.post(EVALUATION_ENDPOINT, json=test_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\nSUCCESS: Evaluation completed and saved")
            print("\nEVALUATION RESULTS:")
            for model, data in result.get('evaluations', {}).items():
                print(f"\n{model}:")
                print(f"  Overall Score: {data.get('overall_score', 0):.4f}")
                
        else:
            print(f"ERROR: Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"Exception occurred: {str(e)}")

if __name__ == "__main__":
    print("Starting JSON response handling tests...")
    
    # Test both endpoints
    test_metrics_endpoint()
    time.sleep(1)  # Add a small delay between tests
    test_evaluation_endpoint()
    
    print("\nTests completed!")
