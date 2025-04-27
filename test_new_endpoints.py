import requests
import json

# Base URL for API
BASE_URL = 'http://localhost:5000/api'

def test_evaluate_endpoint():
    """Test the /evaluate endpoint"""
    url = f"{BASE_URL}/evaluate"
    
    # Example request data
    data = {
        "question": "What is the capital of France?",
        "responses": {
            "ChatGPT": "The capital of France is Paris. Paris is known for its iconic landmarks like the Eiffel Tower and the Louvre Museum.",
            "Gemini": "Paris is the capital city of France.",
            "Llama": "France's capital is Paris, which is located in the north-central part of the country."
        }
    }
    
    # Send POST request
    response = requests.post(url, json=data)
    
    # Check response
    if response.status_code == 200:
        result = response.json()
        print("Evaluation Result:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def test_evaluate_metrics_only():
    """Test the /evaluate/metrics endpoint (doesn't save to database)"""
    url = f"{BASE_URL}/evaluate/metrics"
    
    # Example request data
    data = {
        "question": "Explain how photosynthesis works.",
        "responses": {
            "ChatGPT": "Photosynthesis is the process by which plants convert sunlight, water, and carbon dioxide into oxygen and glucose. The process takes place in the chloroplasts of plant cells, specifically using the green pigment chlorophyll.",
            "Gemini": "Photosynthesis is how plants make food using sunlight, water and CO2.",
            "Llama": "Plants use sunlight to convert CO2 and H2O into sugar and oxygen through a process called photosynthesis."
        }
    }
    
    # Send POST request
    response = requests.post(url, json=data)
    
    # Check response
    if response.status_code == 200:
        result = response.json()
        print("\nMetrics Only Result:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def test_feedback_endpoint():
    """Test the /feedback endpoint"""
    url = f"{BASE_URL}/feedback"
    
    # Example request data
    data = {
        "feedback": {
            "ChatGPT": 4,
            "Gemini": 5,
            "Llama": 3
        },
        "scores": {
            "ChatGPT": {
                "coherence": 0.85,
                "token_overlap": 0.6,
                "length_ratio": 0.7,
                "overall_score": 0.75
            },
            "Gemini": {
                "coherence": 0.9,
                "token_overlap": 0.7,
                "length_ratio": 0.9,
                "overall_score": 0.85
            },
            "Llama": {
                "coherence": 0.7,
                "token_overlap": 0.5,
                "length_ratio": 0.6,
                "overall_score": 0.6
            }
        }
    }
    
    # Send POST request
    response = requests.post(url, json=data)
    
    # Check response
    if response.status_code == 200:
        result = response.json()
        print("\nFeedback Result:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

def test_ranking_endpoint():
    """Test the /ranking endpoint"""
    url = f"{BASE_URL}/ranking"
    
    # Send GET request
    response = requests.get(url)
    
    # Check response
    if response.status_code == 200:
        result = response.json()
        print("\nRanking Result:")
        print(json.dumps(result, indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    print("Testing the new endpoints...")
    
    # Run tests
    test_evaluate_endpoint()
    test_evaluate_metrics_only()
    test_feedback_endpoint()
    test_ranking_endpoint()
    
    print("\nTests completed.") 