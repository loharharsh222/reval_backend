"""
Fix script to repair the evaluation service file syntax
"""
import os

def fix_evaluation_service():
    """Fix syntax issues in the evaluation service file"""
    
    # Load the fixed content
    fixed_content = '''# filepath: c:\\Users\\Ahmad\\Desktop\\Desktop\\BE Project\\reval_backend\\app\\services\\evaluation_service.py
from app.utils.nlp_evaluator import NLPEvaluator
from app.models.evaluation import Evaluation
from app.models.leaderboard import Leaderboard
from app import db
import re
import json
import pprint

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
        
        print("\\n" + "="*80)
        print(f"DEBUG: Evaluating responses for question: '{question}'")
        print("="*80)
        
        # Evaluate each model's response
        for model_name, response_text in responses.items():
            # Skip empty responses
            if not response_text:
                print(f"DEBUG: Skipping {model_name} - Empty response")
                continue
            
            print(f"\\nDEBUG: Evaluating {model_name} response:")
            print(f"Response: '{response_text[:100]}{'...' if len(response_text) > 100 else ''}'")
            print(f"Response type: {type(response_text)}, ID: {id(response_text)}")
                
            # Calculate metrics using the NLP evaluator
            metrics = NLPEvaluator.evaluate_text(question, response_text)
            
            # Print metrics for debugging
            print(f"Metrics for {model_name}:")
            pprint.pprint(metrics)
            
            # Store results
            evaluation_results[model_name] = metrics
        
        print("\\nDEBUG: Final evaluation results:")
        pprint.pprint(evaluation_results)
        
        # Check for identical metrics across models
        if len(evaluation_results) > 1:
            print("\\nDEBUG: Checking for identical metrics across models...")
            
            # Collect all coherence scores
            coherence_scores = [metrics['coherence'] for metrics in evaluation_results.values()]
            token_overlap_scores = [metrics['token_overlap'] for metrics in evaluation_results.values()]
            length_ratio_scores = [metrics['length_ratio'] for metrics in evaluation_results.values()]
            overall_scores = [metrics['overall_score'] for metrics in evaluation_results.values()]
            
            # Check if all scores are identical
            if len(set(coherence_scores)) == 1:
                print(f"WARNING: All coherence scores are identical: {coherence_scores[0]}")
            if len(set(token_overlap_scores)) == 1:
                print(f"WARNING: All token overlap scores are identical: {token_overlap_scores[0]}")
            if len(set(length_ratio_scores)) == 1:
                print(f"WARNING: All length ratio scores are identical: {length_ratio_scores[0]}")
            if len(set(overall_scores)) == 1:
                print(f"WARNING: All overall scores are identical: {overall_scores[0]}")
                
        print("="*80 + "\\n")
        
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
        print("\\n" + "="*80)
        print("DEBUG: Saving evaluation to database")
        print(f"Question: '{question}'")
        print("Models evaluated:", list(responses.keys()))
        
        # Create and save the evaluation record
        evaluation = Evaluation(
            question=question,
            responses=responses,
            scores=evaluation_results
        )
        
        db.session.add(evaluation)
        db.session.commit()
        print(f"DEBUG: Saved evaluation with ID: {evaluation.id}")
        
        # Update leaderboard for each model
        for model_name, scores in evaluation_results.items():
            # Get or create leaderboard entry
            leaderboard_entry = Leaderboard.query.filter_by(model_name=model_name).first()
            if not leaderboard_entry:
                leaderboard_entry = Leaderboard(model_name=model_name)
                db.session.add(leaderboard_entry)
            
            # Update the scores
            leaderboard_entry.update_scores(scores)
            print(f"DEBUG: Updated leaderboard for {model_name} - Current avg_score: {leaderboard_entry.avg_final_score:.4f}")
        
        db.session.commit()
        print("DEBUG: Database transaction committed")
        print("="*80 + "\\n")
        
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
        }'''
    
    # Get the file path
    file_path = os.path.join("app", "services", "evaluation_service.py")
    
    # Write the fixed content to the file
    with open(file_path, 'w') as file:
        file.write(fixed_content)
    
    print(f"Fixed evaluation service file: {file_path}")

if __name__ == "__main__":
    fix_evaluation_service()
