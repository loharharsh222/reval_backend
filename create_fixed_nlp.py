#!/usr/bin/env python
"""
This script creates a completely new version of the NLP evaluator
with fixed indentation and all enhancements
"""

import os
import shutil

def create_fixed_nlp_evaluator():
    """Create a fixed version of the NLP evaluator with proper indentation"""
    
    # Path to the file
    nlp_evaluator_path = os.path.join('app', 'utils', 'nlp_evaluator.py')
    
    if not os.path.exists(nlp_evaluator_path):
        print(f"Error: Could not find {nlp_evaluator_path}")
        return False
    
    # Create a backup
    backup_path = nlp_evaluator_path + '.bak2'
    shutil.copy2(nlp_evaluator_path, backup_path)
    print(f"Created backup: {backup_path}")
    
    # The complete fixed file content
    fixed_content = """# filepath: c:\\Users\\Ahmad\\Desktop\\Desktop\\BE Project\\reval_backend\\app\\utils\\nlp_evaluator.py
import nltk
from nltk.translate.bleu_score import sentence_bleu
from nltk.tokenize import word_tokenize, sent_tokenize
import numpy as np
import string
import re
import random
from nltk.stem import PorterStemmer

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
    def preprocess_text(text, use_stemming=True):
        """Preprocess text by removing punctuation, converting to lowercase, and optionally stemming"""
        if not text:
            print("    DEBUG [Preprocess]: Empty text provided")
            return []
            
        # Make sure we're working with a copy to avoid reference issues
        text = str(text).lower()
        text = re.sub(r'[^\\w\\s]', '', text)
        
        tokens = word_tokenize(text)

        if use_stemming:
            stemmer = PorterStemmer()
            tokens = [stemmer.stem(token) for token in tokens]
            print(f"    DEBUG [Preprocess]: Applied stemming to tokens")
        
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
            
        # Check if this is a short greeting prompt
        is_short_greeting = len(reference_tokens) <= 2 and any(token in ['hi', 'hello', 'hey'] for token in reference_tokens)
        
        print(f"    DEBUG [Token Overlap]: Reference tokens ({len(reference_tokens)}): {sorted(list(reference_tokens))[:10]}{'...' if len(reference_tokens) > 10 else ''}")
        print(f"    DEBUG [Token Overlap]: Candidate tokens ({len(candidate_tokens)}): {sorted(list(candidate_tokens))[:10]}{'...' if len(candidate_tokens) > 10 else ''}")
        
        # Find common tokens and print them for debugging
        common_tokens = reference_tokens.intersection(candidate_tokens)
        print(f"    DEBUG [Token Overlap]: Common tokens ({len(common_tokens)}): {sorted(list(common_tokens))[:10]}{'...' if len(common_tokens) > 10 else ''}")
            
        overlap = len(common_tokens)
        
        # For short greeting prompts, evaluate differently
        if is_short_greeting:
            # Check for greeting responses
            greeting_tokens = set(['hi', 'hello', 'hey', 'greet', 'welcom'])
            has_greeting = any(token in greeting_tokens for token in candidate_tokens)
            
            if has_greeting:
                # Good score for greeting responses to greetings
                print(f"    DEBUG [Token Overlap]: Greeting detected in response to greeting prompt, boosting score")
                overlap_ratio = max(0.8, overlap / max(len(reference_tokens), 1))
                print(f"    DEBUG [Token Overlap]: Boosted overlap ratio: {overlap_ratio:.4f}")
                return overlap_ratio
        
        # Standard overlap calculation
        overlap_ratio = overlap / max(len(reference_tokens), 1)
        print(f"    DEBUG [Token Overlap]: Common tokens: {overlap}, ratio: {overlap_ratio:.4f}")
        return overlap_ratio

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
            
        # Special handling for short prompts
        is_short_prompt = reference_length <= 2
        
        # Penalize if candidate is too short or too long compared to reference
        ratio = candidate_length / max(reference_length, 1)
        print(f"    DEBUG [Length Ratio]: Raw ratio: {ratio:.4f}")
        
        if is_short_prompt:
            # For short prompts like "Hi", we expect responses to be much longer
            # Standard greeting responses are typically 5-20 tokens
            if 3 <= candidate_length <= 30:
                # Perfect range for greeting responses
                print(f"    DEBUG [Length Ratio]: Short prompt with appropriate response length")
                return 1.0
            elif candidate_length > 30:
                # Too verbose for a greeting
                final_ratio = 30 / candidate_length
                print(f"    DEBUG [Length Ratio]: Short prompt with verbose response: {final_ratio:.4f}")
                return final_ratio
            else:
                # Too short even for a greeting
                final_ratio = candidate_length / 5  # Ideal minimum would be 5 tokens
                print(f"    DEBUG [Length Ratio]: Short prompt with too brief response: {final_ratio:.4f}")
                return final_ratio
        else:
            # Normal prompt length handling
            if ratio > 1:
                final_ratio = 1.0 / ratio  # Invert ratio if candidate is longer
                print(f"    DEBUG [Length Ratio]: Candidate is longer, inverting ratio: {final_ratio:.4f}")
                return final_ratio
            return ratio

    @staticmethod
    def evaluate_coherence(text, question=None):
        """
        Evaluate coherence based on sentence structure, length, and relation to question
        
        Args:
            text: The response text to evaluate
            question: Optional question text to evaluate coherence in context
        """
        if not text:
            print("    DEBUG [Coherence]: Empty text, returning 0.0")
            return 0.0
            
        sentences = sent_tokenize(text)
        if not sentences:
            print("    DEBUG [Coherence]: No sentences found, returning 0.0")
            return 0.0
            
        # Special handling for short prompts (like "Hi", "Hello")
        is_short_prompt = question and len(question.strip().split()) <= 2
        if is_short_prompt:
            print(f"    DEBUG [Coherence]: Detected short prompt: '{question}'. Adjusting evaluation criteria.")
            # For short greeting prompts, brief responses are actually appropriate
            
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
            
        # Adjust sentence count evaluation based on prompt length
        is_short_prompt = question and len(question.strip().split()) <= 2
        
        if is_short_prompt:
            # For short prompts like "Hi", even a single sentence is appropriate
            sentence_count_score = 1.0 if len(sentences) <= 3 else min(1.0, 5.0 / len(sentences))
            print(f"    DEBUG [Coherence]: Short prompt sentence count score: {sentence_count_score:.4f}")
        else:
            # Normal prompt evaluation
            sentence_count_score = min(1.0, len(sentences) / 5.0) if len(sentences) < 5 else min(1.0, 10.0 / len(sentences))
            print(f"    DEBUG [Coherence]: Sentence count score: {sentence_count_score:.4f}")
        
        # Calculate content coherence based on question relevance
        content_coherence = 0.5  # Default value
        if question and len(question.strip()) > 0:
            # Get stemmed tokens for both question and response
            question_tokens = set(NLPEvaluator.preprocess_text(question, use_stemming=True))
            response_tokens = set(NLPEvaluator.preprocess_text(text, use_stemming=True))
            
            # Check if response addresses key terms from question
            if question_tokens and response_tokens:
                if is_short_prompt:
                    # For short prompts, we expect responses to include greeting tokens
                    greeting_tokens = set(['hi', 'hello', 'hey', 'greet', 'welcom'])
                    greeting_response = any(token in greeting_tokens for token in response_tokens)
                    
                    if greeting_response:
                        content_coherence = 0.9  # High score for greeting responses to greeting prompts
                        print(f"    DEBUG [Coherence]: Short prompt detected greeting response, setting content relevance to {content_coherence:.4f}")
                    else:
                        # Calculate standard relevance
                        intersection = len(question_tokens.intersection(response_tokens))
                        union = len(question_tokens.union(response_tokens))
                        content_coherence = max(0.6, intersection / max(union, 1))  # Minimum 0.6 for short prompts
                        print(f"    DEBUG [Coherence]: Short prompt content relevance (boosted): {content_coherence:.4f}")
                else:
                    # Standard content relevance for normal prompts
                    intersection = len(question_tokens.intersection(response_tokens))
                    union = len(question_tokens.union(response_tokens))
                    content_coherence = intersection / max(union, 1)
                    print(f"    DEBUG [Coherence]: Content relevance: {intersection}/{union} tokens = {content_coherence:.4f}")
        
        # Combine metrics - include content coherence when question is provided
        if question and len(question.strip()) > 0:
            if is_short_prompt:
                # For short prompts, prioritize content relevance and deprioritize structural metrics
                coherence_score = (0.2 * (1 - short_sentence_ratio) + 
                                  0.2 * length_variation + 
                                  0.2 * sentence_count_score +
                                  0.4 * content_coherence)  # More weight on content for short prompts
                
                print(f"    DEBUG [Coherence]: Short prompt calculation: 0.2 * (1 - {short_sentence_ratio:.4f}) + 0.2 * {length_variation:.4f} + 0.2 * {sentence_count_score:.4f} + 0.4 * {content_coherence:.4f} = {coherence_score:.4f}")
                
                # Boost score for short prompts to ensure appropriate scoring
                coherence_score = min(1.0, coherence_score * 1.2)  # 20% boost, capped at 1.0
                print(f"    DEBUG [Coherence]: Short prompt boosted score: {coherence_score:.4f}")
            else:
                # Standard calculation for normal prompts
                coherence_score = (0.3 * (1 - short_sentence_ratio) + 
                                  0.3 * length_variation + 
                                  0.2 * sentence_count_score +
                                  0.2 * content_coherence)
                
                print(f"    DEBUG [Coherence]: Calculation with question context: 0.3 * (1 - {short_sentence_ratio:.4f}) + 0.3 * {length_variation:.4f} + 0.2 * {sentence_count_score:.4f} + 0.2 * {content_coherence:.4f} = {coherence_score:.4f}")
        else:
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
        
        # Detect short prompt scenarios
        is_short_prompt = len(question.strip().split()) <= 2
        if is_short_prompt:
            print(f"  [Eval ID: {eval_id}] Short prompt detected: '{question}'. Using specialized evaluation.")
        
        metrics = {}
            
        # Calculate and debug individual metrics
        coherence = NLPEvaluator.evaluate_coherence(response, question)
        print(f"  Raw Coherence Score: {coherence:.4f}")
        metrics['coherence'] = round(coherence, 2)
        
        token_overlap = NLPEvaluator.calculate_token_overlap(question, response)
        print(f"  Raw Token Overlap: {token_overlap:.4f}")
        metrics['token_overlap'] = round(token_overlap, 2)
        
        length_ratio = NLPEvaluator.calculate_length_ratio(question, response)
        print(f"  Raw Length Ratio: {length_ratio:.4f}")
        metrics['length_ratio'] = round(length_ratio, 2)
            
        # Calculate overall score (weighted average)
        # Adjust weights for short prompts
        is_short_prompt = len(question.strip().split()) <= 2
        
        if is_short_prompt:
            # For short prompts, prioritize coherence and token overlap
            overall_score = (
                0.4 * metrics['coherence'] + 
                0.4 * metrics['token_overlap'] + 
                0.2 * metrics['length_ratio']
            )
            print(f"  Calculating Short Prompt Score: (0.4 * {metrics['coherence']}) + (0.4 * {metrics['token_overlap']}) + (0.2 * {metrics['length_ratio']}) = {overall_score:.4f}")
            
            # Apply boost for appropriate short prompt responses
            # Sensible greeting responses should get scores of 0.7+
            if overall_score < 0.5 and metrics['coherence'] > 0.6:
                boosted_score = min(1.0, overall_score * 1.5)  # 50% boost, capped at 1.0
                print(f"  Boosting short prompt score from {overall_score:.4f} to {boosted_score:.4f}")
                overall_score = boosted_score
        else:
            # Standard scoring for normal prompts
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
        
        return metrics
"""
    
    # Write the fixed content to the file
    with open(nlp_evaluator_path, 'w', encoding='utf-8') as file:
        file.write(fixed_content)
    
    print(f"✅ Created fixed version of {nlp_evaluator_path}")
    return True
    
if __name__ == "__main__":
    if create_fixed_nlp_evaluator():
        print("Fixed NLP evaluator created successfully.")
    else:
        print("Failed to create fixed NLP evaluator.")
