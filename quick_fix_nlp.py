#!/usr/bin/env python
"""
Simple script to fix the NLP evaluator
"""

def fix_nlp_evaluator():
    """Fix the NLP evaluator by writing a corrected version"""
    
    # Simplified corrected version
    file_content = """# NLP Evaluator - Fixed version
import nltk
from nltk.translate.bleu_score import sentence_bleu
from nltk.tokenize import word_tokenize, sent_tokenize
import numpy as np
import string
import re
import random
from nltk.stem import PorterStemmer

# Download NLTK data
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
    def preprocess_text(text, use_stemming=True):
        """Process text by removing punctuation, lowercasing, and stemming"""
        if not text:
            print("DEBUG [Preprocess]: Empty text")
            return []
            
        text = str(text).lower()
        text = re.sub(r'[^\\w\\s]', '', text)
        tokens = word_tokenize(text)
        
        if use_stemming:
            stemmer = PorterStemmer()
            tokens = [stemmer.stem(token) for token in tokens]
            
        return tokens
        
    @staticmethod
    def calculate_token_overlap(reference, candidate):
        """Calculate token overlap between reference and candidate"""
        ref_tokens = set(NLPEvaluator.preprocess_text(reference))
        cand_tokens = set(NLPEvaluator.preprocess_text(candidate))
        
        if not ref_tokens or not cand_tokens:
            return 0.0
            
        # Check for greeting patterns
        is_greeting = len(ref_tokens) <= 2 and any(t in ['hi', 'hello', 'hey'] for t in ref_tokens)
        
        common = ref_tokens.intersection(cand_tokens)
        
        # Special handling for greetings
        if is_greeting:
            greeting_tokens = {'hi', 'hello', 'hey', 'greet'}
            has_greeting = any(t in greeting_tokens for t in cand_tokens)
            if has_greeting:
                return max(0.8, len(common) / len(ref_tokens))
                
        # Standard calculation
        return len(common) / max(len(ref_tokens), 1)
    
    @staticmethod
    def calculate_length_ratio(reference, candidate):
        """Calculate appropriate length ratio"""
        ref_tokens = NLPEvaluator.preprocess_text(reference)
        cand_tokens = NLPEvaluator.preprocess_text(candidate)
        
        ref_len = len(ref_tokens)
        cand_len = len(cand_tokens)
        
        if ref_len == 0:
            return 0.0
            
        # Short prompt handling
        is_short = ref_len <= 2
        ratio = cand_len / ref_len
        
        if is_short:
            # Greeting-type responses
            if 3 <= cand_len <= 30:
                return 1.0
            elif cand_len > 30:
                return 30 / cand_len  # Penalize verbose
            else:
                return cand_len / 5  # Penalize too short
        else:
            # Normal handling
            if ratio > 1:
                return 1.0 / ratio  # Invert if too long
            return ratio
            
    @staticmethod
    def evaluate_coherence(text, question=None):
        """Evaluate text coherence"""
        if not text:
            return 0.0
            
        sentences = sent_tokenize(text)
        if not sentences:
            return 0.0
            
        # Short prompt detection
        is_short_prompt = question and len(question.split()) <= 2
        
        # Calculate metrics
        word_counts = [len(word_tokenize(s)) for s in sentences]
        short_ratio = sum(1 for c in word_counts if c < 3) / max(len(sentences), 1)
        
        # Length variation
        if len(word_counts) > 1:
            length_std = np.std(word_counts)
            length_var = min(1.0, 5.0 / max(length_std, 1))
        else:
            length_var = 0.5
            
        # Sentence count score
        if is_short_prompt:
            sent_score = 1.0 if len(sentences) <= 3 else min(1.0, 5.0 / len(sentences))
        else:
            sent_score = min(1.0, len(sentences) / 5.0) if len(sentences) < 5 else min(1.0, 10.0 / len(sentences))
        
        # Content relevance
        content_score = 0.5
        if question:
            q_tokens = set(NLPEvaluator.preprocess_text(question))
            r_tokens = set(NLPEvaluator.preprocess_text(text))
            
            if q_tokens and r_tokens:
                if is_short_prompt:
                    # Check for greeting responses
                    greeting_tokens = {'hi', 'hello', 'hey', 'greet', 'welcom'}
                    if any(t in greeting_tokens for t in r_tokens):
                        content_score = 0.9
                    else:
                        common = len(q_tokens.intersection(r_tokens))
                        union = len(q_tokens.union(r_tokens))
                        content_score = max(0.6, common / max(union, 1))
                else:
                    common = len(q_tokens.intersection(r_tokens))
                    union = len(q_tokens.union(r_tokens))
                    content_score = common / max(union, 1)
        
        # Calculate final coherence
        if question:
            if is_short_prompt:
                score = (0.2 * (1 - short_ratio) +
                         0.2 * length_var +
                         0.2 * sent_score +
                         0.4 * content_score)
                score = min(1.0, score * 1.2)  # 20% boost
            else:
                score = (0.3 * (1 - short_ratio) +
                         0.3 * length_var +
                         0.2 * sent_score +
                         0.2 * content_score)
        else:
            score = (0.4 * (1 - short_ratio) +
                     0.4 * length_var +
                     0.2 * sent_score)
        
        return min(1.0, max(0.0, score))
        
    @staticmethod
    def evaluate_text(question, response):
        """Main evaluation function"""
        if not question or not response:
            return {'overall_score': 0, 'coherence': 0, 'token_overlap': 0, 'length_ratio': 0}
            
        # Generate ID for tracing
        eval_id = random.randint(1000, 9999)
        print(f"[Eval {eval_id}] Evaluating response for: '{question[:30]}...' ({len(question)} chars)")
        
        # Calculate individual metrics
        coherence = NLPEvaluator.evaluate_coherence(response, question)
        token_overlap = NLPEvaluator.calculate_token_overlap(question, response)
        length_ratio = NLPEvaluator.calculate_length_ratio(question, response)
        
        # Format for output
        metrics = {
            'coherence': round(coherence, 2),
            'token_overlap': round(token_overlap, 2),
            'length_ratio': round(length_ratio, 2)
        }
        
        # Determine if this is a short prompt
        is_short_prompt = len(question.strip().split()) <= 2
        
        # Calculate overall score with appropriate weights
        if is_short_prompt:
            # For short prompts like greetings
            score = (0.4 * metrics['coherence'] +
                     0.4 * metrics['token_overlap'] +
                     0.2 * metrics['length_ratio'])
                     
            # Boost appropriate greeting responses
            if score < 0.5 and metrics['coherence'] > 0.6:
                score = min(1.0, score * 1.5)
        else:
            # Standard weighting
            score = (0.4 * metrics['coherence'] +
                     0.4 * metrics['token_overlap'] +
                     0.2 * metrics['length_ratio'])
        
        metrics['overall_score'] = round(score, 2)
        print(f"[Eval {eval_id}] Score: {metrics['overall_score']}")
        
        return metrics
"""
    
    # Write to file
    with open('app/utils/nlp_evaluator.py', 'w', encoding='utf-8') as f:
        f.write(file_content)
        
    print("✅ Fixed nlp_evaluator.py")

if __name__ == "__main__":
    fix_nlp_evaluator()
    print("Completed.")
