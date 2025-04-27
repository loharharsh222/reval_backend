import nltk
from nltk.translate.bleu_score import sentence_bleu
from nltk.tokenize import word_tokenize, sent_tokenize
import numpy as np
import string
import re

# Download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('stopwords')
except LookupError:
    nltk.download('stopwords')

class NLPEvaluator:
    @staticmethod
    def preprocess_text(text):
        """Preprocess text by removing punctuation and converting to lowercase"""
        if not text:
            return []
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return word_tokenize(text)
    
    @staticmethod
    def calculate_bleu_score(reference, candidate):
        """Calculate BLEU score between reference and candidate text"""
        if not reference or not candidate:
            return 0.0
        
        reference_tokens = NLPEvaluator.preprocess_text(reference)
        candidate_tokens = NLPEvaluator.preprocess_text(candidate)
        
        if not reference_tokens or not candidate_tokens:
            return 0.0
            
        # BLEU score calculation
        try:
            return sentence_bleu([reference_tokens], candidate_tokens)
        except Exception as e:
            print(f"Error calculating BLEU score: {e}")
            return 0.0
    
    @staticmethod
    def calculate_token_overlap(reference, candidate):
        """Calculate token overlap ratio between reference and candidate text"""
        reference_tokens = set(NLPEvaluator.preprocess_text(reference))
        candidate_tokens = set(NLPEvaluator.preprocess_text(candidate))
        
        if not reference_tokens or not candidate_tokens:
            return 0.0
            
        overlap = len(reference_tokens.intersection(candidate_tokens))
        return overlap / max(len(reference_tokens), 1)
    
    @staticmethod
    def calculate_length_ratio(reference, candidate):
        """Calculate length ratio between reference and candidate text"""
        if not reference or not candidate:
            return 0.0
            
        reference_length = len(NLPEvaluator.preprocess_text(reference))
        candidate_length = len(NLPEvaluator.preprocess_text(candidate))
        
        if reference_length == 0:
            return 0.0
        
        # Penalize if candidate is too short or too long compared to reference
        ratio = candidate_length / max(reference_length, 1)
        if ratio > 1:
            return 1.0 / ratio  # Invert ratio if candidate is longer
        return ratio
    
    @staticmethod
    def evaluate_coherence(text):
        """Evaluate coherence based on sentence structure and length"""
        if not text:
            return 0.0
            
        sentences = sent_tokenize(text)
        if not sentences:
            return 0.0
            
        word_counts = [len(word_tokenize(sentence)) for sentence in sentences]
        
        # Check for very short sentences (less than 3 words)
        short_sentences = sum(1 for count in word_counts if count < 3)
        short_sentence_ratio = short_sentences / max(len(sentences), 1)
        
        # Calculate standard deviation of sentence lengths for consistency
        if len(word_counts) > 1:
            length_std = np.std(word_counts)
            length_variation = min(1.0, 5.0 / max(length_std, 1))
        else:
            length_variation = 0.5
        
        # Penalize text with too many or too few sentences
        sentence_count_score = min(1.0, len(sentences) / 5.0) if len(sentences) < 5 else min(1.0, 10.0 / len(sentences))
        
        # Combine metrics
        coherence_score = (0.4 * (1 - short_sentence_ratio) + 
                          0.4 * length_variation + 
                          0.2 * sentence_count_score)
        
        return min(1.0, max(0.0, coherence_score))
    
    @staticmethod
    def evaluate_text(question, response):
        """Evaluate the quality of a response using NLP metrics"""
        metrics = {}
        
        # Calculate individual metrics
        metrics['coherence'] = round(NLPEvaluator.evaluate_coherence(response), 2)
        metrics['token_overlap'] = round(NLPEvaluator.calculate_token_overlap(question, response), 2)
        metrics['length_ratio'] = round(NLPEvaluator.calculate_length_ratio(question, response), 2)
        
        # Calculate overall score (weighted average)
        metrics['overall_score'] = round(
            0.4 * metrics['coherence'] + 
            0.4 * metrics['token_overlap'] + 
            0.2 * metrics['length_ratio'], 
            2
        )
        
        return metrics 