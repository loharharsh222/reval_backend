from typing import List, Dict, Tuple
from app.utils.evaluation import evaluator
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class RAGService:
    def __init__(self):
        # Initialize the sentence transformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        # Sample knowledge base - in a real application, this would be your actual knowledge base
        self.knowledge_base = [
            "Paris is the capital of France and is known as the City of Light.",
            "The Eiffel Tower is a wrought-iron lattice tower in Paris, France.",
            "The Louvre Museum is the world's largest art museum in Paris.",
            "Jupiter is the largest planet in our solar system.",
            "Jupiter is the fifth planet from the Sun.",
            "Jupiter has 79 known moons.",
            "Jane Austen was an English novelist.",
            "Pride and Prejudice was published in 1813.",
            "Jane Austen's works critique the British landed gentry."
        ]
        # Pre-compute embeddings for the knowledge base
        self.kb_embeddings = self.model.encode(self.knowledge_base)

    def retrieve_contexts(self, query: str, top_k: int = 3) -> List[str]:
        """
        Retrieve relevant contexts from the knowledge base.
        
        Args:
            query: The user's question
            top_k: Number of contexts to retrieve
            
        Returns:
            List of relevant contexts
        """
        # Encode the query
        query_embedding = self.model.encode(query)
        
        # Calculate similarities
        similarities = cosine_similarity(
            [query_embedding],
            self.kb_embeddings
        )[0]
        
        # Get top-k most similar contexts
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        return [self.knowledge_base[i] for i in top_indices]

    def generate_answer(self, query: str, contexts: List[str]) -> str:
        """
        Generate an answer based on the query and retrieved contexts.
        This is a simple implementation - in a real application, you might use an LLM.
        
        Args:
            query: The user's question
            contexts: Retrieved contexts
            
        Returns:
            Generated answer
        """
        # Simple answer generation by combining contexts
        return f"Based on the information: {' '.join(contexts)}"

    def process_query(self, query: str, reference: str) -> Tuple[str, List[str], Dict[str, float]]:
        """
        Process a user query and return the answer, contexts, and evaluation metrics.
        
        Args:
            query: The user's question
            reference: The reference answer from ChatGPT
            
        Returns:
            Tuple containing:
            - The generated answer
            - List of contexts used
            - Dictionary of evaluation metrics
        """
        # Retrieve relevant contexts
        contexts = self.retrieve_contexts(query)
        
        # Generate answer
        answer = self.generate_answer(query, contexts)
        
        # Evaluate the response
        evaluation_metrics = evaluator.evaluate_single_response(
            question=query,
            answer=answer,
            reference=reference,
            contexts=contexts
        )
        
        return answer, contexts, evaluation_metrics

    def batch_process(self, queries: List[str], references: List[str]) -> List[Tuple[str, List[str], Dict[str, float]]]:
        """
        Process multiple queries and return their answers, contexts, and evaluation metrics.
        
        Args:
            queries: List of user questions
            references: List of reference answers from ChatGPT
            
        Returns:
            List of tuples containing answers, contexts, and evaluation metrics
        """
        results = []
        for query, reference in zip(queries, references):
            answer, contexts, metrics = self.process_query(query, reference)
            results.append((answer, contexts, metrics))
        return results 