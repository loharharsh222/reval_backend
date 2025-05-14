"""
Fix script to repair the NLP evaluator file syntax
"""
import os

def fix_nlp_evaluator():
    """Fix syntax issues in the NLP evaluator file"""
    
    # Load the fixed content
    fixed_content = '''# filepath: c:\\Users\\Ahmad\\Desktop\\Desktop\\BE Project\\reval_backend\\app\\utils\\nlp_evaluator.py
import nltk
from nltk.translate.bleu_score import sentence_bleu
from nltk.tokenize import word_tokenize, sent_tokenize
import numpy as np
import string
import re
import random

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
            print("    DEBUG [Preprocess]: Empty text provided")
            return []
            
        # Make sure we're working with a copy to avoid reference issues
        text = str(text).lower()
        text = re.sub(r'[^\w\s]', '', text)
        
        tokens = word_tokenize(text)
        print(f"    DEBUG [Preprocess]: Generated {len(tokens)} tokens from text")
        return tokens
    
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
        # Ensure we're working with copies
        reference_processed = NLPEvaluator.preprocess_text(reference)
        candidate_processed = NLPEvaluator.preprocess_text(candidate)
        
        print(f"    DEBUG [Token Overlap]: ID reference_processed: {id(reference_processed)}")
        print(f"    DEBUG [Token Overlap]: ID candidate_processed: {id(candidate_processed)}")
        
        reference_tokens = set(reference_processed)
        candidate_tokens = set(candidate_processed)
        
        if not reference_tokens or not candidate_tokens:
            print("    DEBUG [Token Overlap]: Empty tokens set, returning 0.0")
            return 0.0
        
        print(f"    DEBUG [Token Overlap]: Reference tokens ({len(reference_tokens)}): {sorted(list(reference_tokens))[:10]}{'...' if len(reference_tokens) > 10 else ''}")
        print(f"    DEBUG [Token Overlap]: Candidate tokens ({len(candidate_tokens)}): {sorted(list(candidate_tokens))[:10]}{'...' if len(candidate_tokens) > 10 else ''}")
        
        # Find common tokens and print them for debugging
        common_tokens = reference_tokens.intersection(candidate_tokens)
        print(f"    DEBUG [Token Overlap]: Common tokens ({len(common_tokens)}): {sorted(list(common_tokens))[:10]}{'...' if len(common_tokens) > 10 else ''}")
            
        overlap = len(common_tokens)
        print(f"    DEBUG [Token Overlap]: Common tokens: {overlap}, ratio: {overlap / max(len(reference_tokens), 1):.4f}")
        return overlap / max(len(reference_tokens), 1)
    
    @staticmethod
    def calculate_length_ratio(reference, candidate):
        """Calculate length ratio between reference and candidate text"""
        if not reference or not candidate:
            print("    DEBUG [Length Ratio]: Empty text provided, returning 0.0")
            return 0.0
            
        reference_length = len(NLPEvaluator.preprocess_text(reference))
        candidate_length = len(NLPEvaluator.preprocess_text(candidate))
        print(f"    DEBUG [Length Ratio]: Reference tokens: {reference_length}, Candidate tokens: {candidate_length}")
        
        if reference_length == 0:
            print("    DEBUG [Length Ratio]: Reference length is 0, returning 0.0")
            return 0.0
        
        # Penalize if candidate is too short or too long compared to reference
        ratio = candidate_length / max(reference_length, 1)
        print(f"    DEBUG [Length Ratio]: Raw ratio: {ratio:.4f}")
        
        if ratio > 1:
            final_ratio = 1.0 / ratio  # Invert ratio if candidate is longer
            print(f"    DEBUG [Length Ratio]: Candidate is longer, inverting ratio: {final_ratio:.4f}")
            return final_ratio
        return ratio
    
    @staticmethod
    def evaluate_coherence(text):
        """Evaluate coherence based on sentence structure and length"""
        if not text:
            print("    DEBUG [Coherence]: Empty text, returning 0.0")
            return 0.0
            
        sentences = sent_tokenize(text)
        if not sentences:
            print("    DEBUG [Coherence]: No sentences found, returning 0.0")
            return 0.0
            
        print(f"    DEBUG [Coherence]: Number of sentences: {len(sentences)}")
        print(f"    DEBUG [Coherence]: First sentence: '{sentences[0][:50]}{'...' if len(sentences[0]) > 50 else ''}'")
            
        word_counts = [len(word_tokenize(sentence)) for sentence in sentences]
        print(f"    DEBUG [Coherence]: Words per sentence: {word_counts}")
        
        # Check for very short sentences (less than 3 words)
        short_sentences = sum(1 for count in word_counts if count < 3)
        short_sentence_ratio = short_sentences / max(len(sentences), 1)
        print(f"    DEBUG [Coherence]: Short sentences: {short_sentences}/{len(sentences)} (ratio: {short_sentence_ratio:.4f})")
        
        # Calculate standard deviation of sentence lengths for consistency
        if len(word_counts) > 1:
            length_std = np.std(word_counts)
            length_variation = min(1.0, 5.0 / max(length_std, 1))
            print(f"    DEBUG [Coherence]: Sentence length std dev: {length_std:.4f}, variation score: {length_variation:.4f}")
        else:
            length_variation = 0.5
            print(f"    DEBUG [Coherence]: Single sentence, using default variation score: {length_variation:.4f}")
        
        # Penalize text with too many or too few sentences
        sentence_count_score = min(1.0, len(sentences) / 5.0) if len(sentences) < 5 else min(1.0, 10.0 / len(sentences))
        print(f"    DEBUG [Coherence]: Sentence count score: {sentence_count_score:.4f}")
        
        # Combine metrics
        coherence_score = (0.4 * (1 - short_sentence_ratio) + 
                          0.4 * length_variation + 
                          0.2 * sentence_count_score)
        
        print(f"    DEBUG [Coherence]: Calculation: 0.4 * (1 - {short_sentence_ratio:.4f}) + 0.4 * {length_variation:.4f} + 0.2 * {sentence_count_score:.4f} = {coherence_score:.4f}")
        
        final_score = min(1.0, max(0.0, coherence_score))
        if final_score != coherence_score:
            print(f"    DEBUG [Coherence]: Score clamped to range [0,1]: {final_score:.4f}")
        
        return final_score
    
    @staticmethod
    def evaluate_text(question, response):
        """Evaluate the quality of a response using NLP metrics"""
        print("\\n--- NLP Evaluator Detailed Metrics ---")
        print(f"  Question: '{question[:50]}{'...' if len(question) > 50 else ''}' ({len(question)} chars)")
        print(f"  Response: '{response[:50]}{'...' if len(response) > 50 else ''}' ({len(response)} chars)")
        
        # Add unique identifier for each evaluation call to trace through debug logs
        eval_id = random.randint(1000, 9999)
        print(f"  [Eval ID: {eval_id}] Starting evaluation")
        
        metrics = {}
        
        # Calculate and debug individual metrics
        coherence = NLPEvaluator.evaluate_coherence(response)
        print(f"  Raw Coherence Score: {coherence:.4f}")
        metrics['coherence'] = round(coherence, 2)
        
        token_overlap = NLPEvaluator.calculate_token_overlap(question, response)
        print(f"  Raw Token Overlap: {token_overlap:.4f}")
        metrics['token_overlap'] = round(token_overlap, 2)
        
        length_ratio = NLPEvaluator.calculate_length_ratio(question, response)
        print(f"  Raw Length Ratio: {length_ratio:.4f}")
        metrics['length_ratio'] = round(length_ratio, 2)
        
        # Calculate overall score (weighted average)
        overall_score = (
            0.4 * metrics['coherence'] + 
            0.4 * metrics['token_overlap'] + 
            0.2 * metrics['length_ratio']
        )
        print(f"  Calculating Overall Score: (0.4 * {metrics['coherence']}) + (0.4 * {metrics['token_overlap']}) + (0.2 * {metrics['length_ratio']}) = {overall_score:.4f}")
        
        metrics['overall_score'] = round(overall_score, 2)
        print(f"  Final Overall Score: {metrics['overall_score']}")
        print(f"  [Eval ID: {eval_id}] Evaluation complete")
        print("--- End of NLP Evaluation ---\\n")
        
        return metrics'''
    
    # Get the file path
    file_path = os.path.join("app", "utils", "nlp_evaluator.py")
    
    # Write the fixed content to the file
    with open(file_path, 'w') as file:
        file.write(fixed_content)
    
    print(f"Fixed NLP evaluator file: {file_path}")

if __name__ == "__main__":
    fix_nlp_evaluator()
