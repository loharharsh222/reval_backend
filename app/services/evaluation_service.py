from app.utils.math_evaluator import MathEvaluator
from app.utils.logic_evaluator import LogicEvaluator
from app.models.evaluation import Evaluation
from app.models.leaderboard import Leaderboard
from app import db
import re

class EvaluationService:
    @staticmethod
    def evaluate_coherence(response):
        """
        Evaluate the coherence of a response
        Returns a score between 0 and 1
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
            
    @staticmethod
    def evaluate_responses(question, responses):
        """
        Evaluate responses from multiple LLMs for a given question
        
        Args:
            question: The user's question (math/logical reasoning)
            responses: Dictionary of model responses (model_name -> response_text)
            
        Returns:
            Dictionary of evaluation scores for each model
        """
        evaluation_results = {}
        
        # Evaluate each model's response
        for model_name, response_text in responses.items():
            # Skip empty responses
            if not response_text:
                continue
                
            # Calculate metrics
            coherence = EvaluationService.evaluate_coherence(response_text)
            relevance = EvaluationService.evaluate_relevance(question, response_text)
            math_validity = MathEvaluator.check_math_validity(response_text, question)
            logical_consistency = LogicEvaluator.check_logical_consistency(response_text)
            
            # Calculate final score (weighted average)
            final_score = (
                0.20 * coherence + 
                0.25 * relevance + 
                0.35 * math_validity + 
                0.20 * logical_consistency
            )
            
            # Store results
            evaluation_results[model_name] = {
                'coherence': round(coherence, 2),
                'relevance': round(relevance, 2),
                'math_validity': round(math_validity, 2),
                'logical_consistency': round(logical_consistency, 2),
                'final_score': round(final_score, 2)
            }
        
        return evaluation_results
    
    @staticmethod
    def save_evaluation(question, responses, evaluation_results):
        """
        Save evaluation results to database and update leaderboard
        
        Args:
            question: The user's question
            responses: Dictionary of model responses
            evaluation_results: Dictionary of evaluation scores for each model
            
        Returns:
            Created evaluation record
        """
        # Create and save the evaluation record
        evaluation = Evaluation(
            question=question,
            responses=responses,
            scores=evaluation_results
        )
        
        db.session.add(evaluation)
        db.session.commit()
        
        # Update leaderboard for each model
        for model_name, scores in evaluation_results.items():
            # Get or create leaderboard entry
            leaderboard_entry = Leaderboard.query.filter_by(model_name=model_name).first()
            if not leaderboard_entry:
                leaderboard_entry = Leaderboard(model_name=model_name)
                db.session.add(leaderboard_entry)
            
            # Update the scores
            leaderboard_entry.update_scores(scores)
        
        db.session.commit()
        
        return evaluation
    
    @staticmethod
    def get_leaderboard():
        """
        Get the current leaderboard rankings
        
        Returns:
            List of leaderboard entries sorted by average final score
        """
        leaderboard_entries = Leaderboard.query.order_by(Leaderboard.avg_final_score.desc()).all()
        return [entry.to_dict() for entry in leaderboard_entries]
    
    @staticmethod
    def evaluate_and_save(question, responses):
        """
        Evaluate LLM responses and save results to database
        
        Args:
            question: The user's question
            responses: Dictionary of model responses
            
        Returns:
            Dictionary with evaluation results and leaderboard
        """
        # Evaluate responses
        evaluation_results = EvaluationService.evaluate_responses(question, responses)
        
        # Save to database
        evaluation = EvaluationService.save_evaluation(question, responses, evaluation_results)
        
        # Get updated leaderboard
        leaderboard = EvaluationService.get_leaderboard()
        
        return {
            'question': question,
            'evaluation': evaluation_results,
            'leaderboard': leaderboard
        } 