"""
Debug script to test the evaluation with different models
"""
from app.utils.nlp_evaluator import NLPEvaluator
from app.services.evaluation_service import EvaluationService

def test_direct_evaluation():
    """
    Test direct evaluation with different responses
    """
    print("\n=== DIRECT EVALUATION TEST ===\n")
    
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
    if len(set(scores)) < len(scores):
        print("❌ WARNING: Some scores are identical!")
    else:
        print("✅ All models have different scores")

if __name__ == "__main__":
    test_direct_evaluation()
