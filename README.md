# LLM Response Evaluator API

A Flask API for evaluating responses from different Large Language Models (LLMs) based on mathematical and logical reasoning accuracy.

## Features

- Evaluates responses from ChatGPT, Gemini, and Llama
- Accepts real-time user input and pre-provided LLM responses
- Preprocesses and normalizes mathematical/logical responses
- Evaluates responses using multiple metrics, including RAGAS
- Stores results in a PostgreSQL database
- Maintains a leaderboard ranking LLMs based on performance
- Allows user feedback (upvote/downvote)
- Visualizes model performance over time
- Supports voice input via speech recognition

## Installation

1. Clone this repository:
```
git clone <repository-url>
cd llm-response-evaluator
```

2. Create a virtual environment:
```
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```
pip install -r requirements.txt
```

4. Create a PostgreSQL database:
```
createdb llm_eval
```

5. Configure environment variables:
   - Create a `.env` file in the root directory or modify the existing one
   - Set `DATABASE_URL` to your PostgreSQL connection string

## Usage

1. Start the Flask server:
```
python app.py
```

2. The API will be available at `http://localhost:5000`

## API Endpoints

### Evaluation

- `POST /api/evaluate`: Evaluate LLM responses
  - Input:
    ```json
    {
      "question": "What is 5 + 3 * 2?",
      "responses": {
        "ChatGPT": "11",
        "Gemini": "10",
        "Llama": "16"
      }
    }
    ```

- `POST /api/evaluate/audio`: Evaluate LLM responses using audio input
  - Multipart form data with:
    - `audio`: Audio file containing the spoken question
    - `responses`: JSON string of model responses

- `GET /api/evaluation/{id}`: Get a specific evaluation by ID

### Feedback

- `POST /api/feedback`: Add user feedback (upvote/downvote)
  - Input:
    ```json
    {
      "evaluation_id": 1,
      "model_name": "ChatGPT",
      "vote_type": "upvote"  // or "downvote"
    }
    ```

- `GET /api/feedback/stats`: Get feedback statistics
  - Optional query parameters:
    - `evaluation_id`: Filter by evaluation ID
    - `model_name`: Filter by model name

### Leaderboard

- `GET /api/leaderboard`: Get the current leaderboard
  - Optional query parameters:
    - `limit`: Maximum number of entries to return (default: 10)

- `GET /api/leaderboard/model/{model_name}`: Get detailed metrics for a specific model

- `GET /api/leaderboard/trend`: Get visualization of model performance trends
  - Optional query parameters:
    - `models`: Comma-separated list of model names
    - `metric`: The metric to visualize (default: final_score)

- `GET /api/leaderboard/radar`: Get radar chart comparison of models
  - Optional query parameters:
    - `models`: Comma-separated list of model names

## Example Response

```json
{
  "question": "What is 5 + 3 * 2?",
  "evaluation": {
    "ChatGPT": {
      "coherence": 0.95,
      "relevance": 0.9,
      "math_validity": 1.0,
      "logical_consistency": 0.95,
      "final_score": 0.95
    },
    "Gemini": {
      "coherence": 0.9,
      "relevance": 0.85,
      "math_validity": 0.5,
      "logical_consistency": 0.7,
      "final_score": 0.74
    }
  },
  "leaderboard": [
    {"model": "ChatGPT", "avg_score": 0.95},
    {"model": "Gemini", "avg_score": 0.74},
    {"model": "Llama", "avg_score": 0.6}
  ]
}
```

## Technologies Used

- Flask (API framework)
- SQLAlchemy (ORM for database)
- PostgreSQL (database)
- RAGAS (LLM response evaluation)
- SymPy (mathematical parsing)
- NLTK (text processing)
- Sentence Transformers (semantic similarity)
- SpeechRecognition (voice input)
- Matplotlib (visualization) 