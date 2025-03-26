import numpy as np

class RagasEvaluator:
    @staticmethod
    def evaluate_coherence(response):
        """
        Evaluate the coherence of a response
        Returns a score between 0 and 1
        
        Note: This is a fallback implementation that doesn't require RAGAS
        """
        try:
            # Fallback to a simpler coherence estimate
            word_count = len(response.split())
            sentence_count = response.count('.') + response.count('!') + response.count('?')
            
            # If no sentences detected, check if response has at least some content
            if sentence_count == 0:
                if word_count > 0:
                    return 0.7  # Some content but no proper sentences
                else:
                    return 0.0  # Empty response
            
            # Average words per sentence - too short or too long sentences may indicate poor coherence
            avg_words_per_sentence = word_count / max(sentence_count, 1)
            
            # Very short or very long responses might be less coherent
            if word_count < 3:
                return 0.3
            elif word_count > 200:
                return 0.7
            
            # Ideal words per sentence for coherence (roughly 10-20)
            if 10 <= avg_words_per_sentence <= 20:
                return 0.9
            elif 5 <= avg_words_per_sentence < 10 or 20 < avg_words_per_sentence <= 30:
                return 0.8
            else:
                return 0.7
                
        except Exception as e:
            print(f"Error in evaluate_coherence: {e}")
            return 0.7  # Default value

    @staticmethod
    def evaluate_relevance(question, response):
        """
        Evaluate the relevance of a response to a question
        Returns a score between 0 and 1
        
        Note: This is a fallback implementation that doesn't require RAGAS
        """
        try:
            # Simple word overlap calculation
            question_words = set(question.lower().split())
            response_words = set(response.lower().split())
            overlap = len(question_words.intersection(response_words))
            
            # Calculate Jaccard similarity
            if len(question_words) == 0 or len(response_words) == 0:
                return 0.5
                
            jaccard = overlap / len(question_words.union(response_words))
            
            # Calculate word overlap ratio
            overlap_ratio = overlap / len(question_words) if len(question_words) > 0 else 0
            
            # Combine metrics
            if overlap > 0:
                # Weigh direct overlap more heavily for relevance
                relevance_score = 0.3 + (0.7 * max(jaccard, overlap_ratio))
                return min(relevance_score, 1.0)
            else:
                return 0.3  # Low relevance if no word overlap
                
        except Exception as e:
            print(f"Error in evaluate_relevance: {e}")
            return 0.5  # Default neutral value 