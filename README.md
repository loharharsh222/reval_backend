# LLM Response Evaluator API

A Flask API for evaluating responses from different Large Language Models (LLMs) using NLP metrics.

## Features

- Evaluates responses from ChatGPT, Gemini, and Llama
- Accepts real-time user input and pre-provided LLM responses
- Evaluates responses using NLP metrics (coherence, token overlap, length ratio)
- Stores results in a PostgreSQL database
- Maintains a leaderboard ranking LLMs based on performance
- Allows user feedback (ratings from 1-5)
- Calculates model rankings based on metrics and user feedback

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

- `POST /api/evaluate`: Evaluate LLM responses and save to database
  - Input:
    ```json
    {
      "question": "What is the capital of France?",
      "responses": {
        "ChatGPT": "The capital of France is Paris.",
        "Gemini": "Paris is the capital city of France.",
        "Llama": "France's capital is Paris."
      }
    }
    ```

- `POST /api/evaluate/metrics`: Evaluate LLM responses without saving to database
  - Input:
    ```json
    {
      "question": "What is the capital of France?",
      "responses": {
        "ChatGPT": "The capital of France is Paris.",
        "Gemini": "Paris is the capital city of France.",
        "Llama": "France's capital is Paris."
      }
    }
    ```

- `GET /api/evaluation/{id}`: Get a specific evaluation by ID

### Feedback

- `POST /api/feedback`: Add user feedback with ratings
  - Input:
    ```json
    {
      "feedback": {
        "ChatGPT": 4,
        "Gemini": 5,
        "Llama": 3
      },
      "scores": {
        "ChatGPT": { ... metrics ... },
        "Gemini": { ... metrics ... },
        "Llama": { ... metrics ... }
      }
    }
    ```

- `GET /api/ranking`: Get the current model ranking based on metrics and user feedback

### Leaderboard

- `GET /api/leaderboard`: Get the current leaderboard
  - Optional query parameters:
    - `limit`: Maximum number of entries to return (default: 10)

- `GET /api/leaderboard/model/{model_name}`: Get detailed metrics for a specific model

## Example Response

### Evaluation Response
```json
{
  "question": "What is the capital of France?",
  "evaluation": {
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
    }
  },
  "leaderboard": [
    {"model": "Gemini", "avg_score": 0.85},
    {"model": "ChatGPT", "avg_score": 0.75},
    {"model": "Llama", "avg_score": 0.65}
  ]
}
```

### Ranking Response
```json
[
  {
    "model": "Gemini",
    "combined_score": 0.88,
    "nlp_score": 0.85,
    "user_rating": 4.8,
    "feedback_count": 5,
    "evaluation_count": 10,
    "rank": 1
  },
  {
    "model": "ChatGPT",
    "combined_score": 0.76,
    "nlp_score": 0.75,
    "user_rating": 4.2,
    "feedback_count": 5,
    "evaluation_count": 10,
    "rank": 2
  },
  {
    "model": "Llama",
    "combined_score": 0.63,
    "nlp_score": 0.65,
    "user_rating": 3.5,
    "feedback_count": 5,
    "evaluation_count": 10,
    "rank": 3
  }
]
```

## Technologies Used

- Flask (API framework)
- SQLAlchemy (ORM for database)
- PostgreSQL (database)
- NLTK (text processing)
- Sentence Transformers (semantic similarity)
- NumPy (numerical calculations)
- Matplotlib (visualization) 