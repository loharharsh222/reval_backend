import requests
import json

BASE_URL = 'http://127.0.0.1:5000/api'

def test_leaderboard():
    print("\nTesting Leaderboard endpoint...")
    response = requests.get(f'{BASE_URL}/leaderboard')
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

def test_evaluate():
    print("\nTesting Evaluate endpoint...")
    data = {
        "question": "What is 2+2?",
        "responses": {response.evaluate
            "ChatGPT": "4",
            "Gemini": "4",
            "Llama": "4"
        }
    }
    response = requests.post(f'{BASE_URL}/evaluate', json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.json().get('evaluation_id') if response.status_code == 200 else None

def test_feedback(evaluation_id):
    print("\nTesting Feedback endpoint...")
    data = {
        "evaluation_id": evaluation_id,
        "model_name": "ChatGPT",
        "vote_type": "upvote"
    }
    response = requests.post(f'{BASE_URL}/feedback', json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")

def test_single_query():
    url = "http://localhost:5000/api/rag/query"
    headers = {"Content-Type": "application/json"}
    data = {"query": "What is the capital of France?"}
    
    response = requests.post(url, headers=headers, json=data)
    print("Response Status Code:", response.status_code)
    print("Response Body:")
    print(json.dumps(response.json(), indent=2))

def test_batch_queries():
    url = "http://localhost:5000/api/rag/batch"
    headers = {"Content-Type": "application/json"}
    data = {
        "queries": [
            "What is the capital of France?",
            "What is the largest planet in our solar system?",
            "Who wrote Pride and Prejudice?"
        ]
    }
    
    response = requests.post(url, headers=headers, json=data)
    print("Response Status Code:", response.status_code)
    print("Response Body:")
    print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("Starting API tests...")
    test_leaderboard()
    evaluation_id = test_evaluate()
    if evaluation_id:
        test_feedback(evaluation_id)
    
    print("\nTesting single query...")
    test_single_query()
    
    print("\nTesting batch queries...")
    test_batch_queries() 