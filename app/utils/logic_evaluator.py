import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from scipy.spatial.distance import cosine
import numpy as np
from sentence_transformers import SentenceTransformer

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class LogicEvaluator:
    model = None
    
    @staticmethod
    def get_model():
        """Lazy-load the sentence transformer model"""
        if LogicEvaluator.model is None:
            LogicEvaluator.model = SentenceTransformer('all-MiniLM-L6-v2')
        return LogicEvaluator.model
    
    @staticmethod
    def preprocess_text(text):
        """Tokenize and remove stopwords from text"""
        if not text:
            return []
        
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        return [word for word in tokens if word.isalnum() and word not in stop_words]
    
    @staticmethod
    def semantic_similarity(text1, text2):
        """
        Calculate semantic similarity between two texts
        Returns a score between 0 and 1, where 1 is perfect similarity
        """
        try:
            model = LogicEvaluator.get_model()
            embedding1 = model.encode([text1])[0]
            embedding2 = model.encode([text2])[0]
            
            similarity = 1 - cosine(embedding1, embedding2)
            return max(0, min(1, similarity))  # Clamp between 0 and 1
            
        except Exception as e:
            print(f"Error in semantic_similarity: {e}")
            return 0.0
    
    @staticmethod
    def check_logical_consistency(response):
        """
        Check for logical consistency in the response
        This is a simplified check - in real applications, this would be more complex
        Returns a score between 0 and 1
        """
        try:
            # Define contradictory phrase pairs (simplified)
            contradictions = [
                ("increase", "decrease"),
                ("more", "less"),
                ("larger", "smaller"),
                ("higher", "lower"),
                ("true", "false"),
                ("correct", "incorrect"),
                ("yes", "no"),
                ("positive", "negative"),
                ("always", "never")
            ]
            
            # Tokenize response
            tokens = LogicEvaluator.preprocess_text(response)
            if not tokens:
                return 0.5  # Neutral score if no analyzable content
            
            # Check for contradictions
            found_contradictions = 0
            for pair in contradictions:
                if pair[0] in tokens and pair[1] in tokens:
                    found_contradictions += 1
            
            # Calculate consistency score
            consistency_score = 1.0 - (found_contradictions * 0.2)  # Deduct 0.2 for each contradiction
            return max(0, consistency_score)  # Ensure it's not negative
            
        except Exception as e:
            print(f"Error in check_logical_consistency: {e}")
            return 0.5  # Neutral score on error 