from app.utils.nlp_evaluator import NLPEvaluator
from app.models.evaluation import Evaluation
from app.models.leaderboard import Leaderboard
from app import db
import re

class EvaluationService:
    @staticmethod
    def evaluate_responses(question, responses):
        """
        Evaluate responses from multiple LLMs for a given question
        
        Args:
            question: The user's question
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
                
            # Calculate metrics using the NLP evaluator
            metrics = NLPEvaluator.evaluate_text(question, response_text)
            
            # Store results
            evaluation_results[model_name] = metrics
        
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