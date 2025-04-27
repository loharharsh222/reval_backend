from typing import List, Dict
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class RAGEvaluator:
    def __init__(self):
        # Initialize the sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def evaluate_answer_correctness(self, answer: str, reference: str) -> float:
        """Evaluate how correct the answer is compared to the reference answer."""
        answer_embedding = self.model.encode(answer)
        reference_embedding = self.model.encode(reference)
        return float(cosine_similarity([answer_embedding], [reference_embedding])[0][0])
    
    def evaluate_answer_relevancy(self, question: str, answer: str) -> float:
        """Evaluate how relevant the answer is to the question."""
        question_embedding = self.model.encode(question)
        answer_embedding = self.model.encode(answer)
        return float(cosine_similarity([question_embedding], [answer_embedding])[0][0])
    
    def evaluate_context_precision(self, question: str, contexts: List[str]) -> float:
        """Evaluate how precise the retrieved contexts are."""
        question_embedding = self.model.encode(question)
        context_embeddings = self.model.encode(contexts)
        similarities = cosine_similarity([question_embedding], context_embeddings)[0]
        return float(np.mean(similarities))
    
    def evaluate_context_recall(self, answer: str, contexts: List[str]) -> float:
        """Evaluate how well the contexts cover the answer."""
        answer_embedding = self.model.encode(answer)
        context_embeddings = self.model.encode(contexts)
        similarities = cosine_similarity([answer_embedding], context_embeddings)[0]
        return float(np.mean(similarities))
    
    def evaluate_faithfulness(self, answer: str, contexts: List[str]) -> float:
        """Evaluate how faithful the answer is to the contexts."""
        answer_embedding = self.model.encode(answer)
        context_embeddings = self.model.encode(' '.join(contexts))
        return float(cosine_similarity([answer_embedding], [context_embeddings])[0][0])
    
    def evaluate_context_relevancy(self, question: str, contexts: List[str]) -> float:
        """Evaluate how relevant the contexts are to the question."""
        return self.evaluate_context_precision(question, contexts)

    def evaluate_single_response(self, question: str, answer: str, reference: str, contexts: List[str]) -> Dict[str, float]:
        """
        Evaluate a single question-answer pair using the provided reference.
        
        Args:
            question: The question asked
            answer: The generated answer
            reference: The reference answer (from ChatGPT)
            contexts: List of contexts used to generate the answer
            
        Returns:
            Dict containing evaluation metrics
        """
        metrics = {
            'answer_correctness': self.evaluate_answer_correctness(answer, reference),
            'answer_relevancy': self.evaluate_answer_relevancy(question, answer),
            'context_precision': self.evaluate_context_precision(question, contexts),
            'context_recall': self.evaluate_context_recall(answer, contexts),
            'faithfulness': self.evaluate_faithfulness(answer, contexts),
            'context_relevancy': self.evaluate_context_relevancy(question, contexts)
        }
        
        return metrics

# Create a global evaluator instance
evaluator = RAGEvaluator()

# Example usage
if __name__ == "__main__":
    # Test evaluation with sample data
    sample_data = {
        "question": "What is the capital of France?",
        "answer": "The capital of France is Paris.",
        "reference": "The capital of France is Paris, a major European city and a global center for art, fashion, and culture.",
        "contexts": ["Paris is the capital and most populous city of France."]
    }
    
    print("\nSample Evaluation Results:")
    print("------------------------")
    metrics = evaluator.evaluate_single_response(
        sample_data["question"],
        sample_data["answer"],
        sample_data["reference"],
        sample_data["contexts"]
    )
    for metric, score in metrics.items():
        print(f"{metric}: {score:.4f}")
    print("------------------------\n") 