import matplotlib.pyplot as plt
import pandas as pd
import io
import base64
from matplotlib.ticker import MaxNLocator

class Visualization:
    @staticmethod
    def generate_leaderboard_trend(model_names, evaluations, metric='final_score'):
        """
        Generate a graph showing the trend of model performance over time
        
        Args:
            model_names: List of model names to include
            evaluations: List of evaluation records
            metric: The metric to plot (default: final_score)
            
        Returns:
            Base64 encoded PNG image
        """
        try:
            # Extract data for plotting
            data = {}
            for model in model_names:
                data[model] = []
                
            # Extract timestamps and scores for each model
            for eval_record in evaluations:
                timestamp = eval_record.created_at
                for model in model_names:
                    if model in eval_record.scores:
                        model_scores = eval_record.scores[model]
                        if metric in model_scores:
                            data[model].append((timestamp, model_scores[metric]))
            
            # Create figure
            plt.figure(figsize=(10, 6))
            
            # Plot data for each model
            for model in model_names:
                if data[model]:
                    # Sort by timestamp
                    sorted_data = sorted(data[model], key=lambda x: x[0])
                    
                    # Separate timestamps and scores
                    timestamps = [item[0] for item in sorted_data]
                    scores = [item[1] for item in sorted_data]
                    
                    # Plot line
                    plt.plot(timestamps, scores, marker='o', label=model)
            
            # Add labels and title
            plt.xlabel('Time')
            plt.ylabel(f'{metric.replace("_", " ").title()} Score')
            plt.title(f'LLM Performance Trend - {metric.replace("_", " ").title()}')
            plt.legend()
            plt.grid(True, linestyle='--', alpha=0.7)
            
            # Set y-axis range between 0 and 1
            plt.ylim(0, 1)
            
            # Format x-axis
            plt.gca().xaxis.set_major_locator(MaxNLocator(nbins=5))
            plt.xticks(rotation=45)
            
            # Tight layout to prevent label cutoff
            plt.tight_layout()
            
            # Save the figure to a bytes buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            
            # Encode the bytes to base64
            image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
            
            return image_base64
            
        except Exception as e:
            print(f"Error generating visualization: {e}")
            return None
    
    @staticmethod
    def generate_radar_chart(model_scores):
        """
        Generate a radar chart comparing different models across metrics
        
        Args:
            model_scores: Dictionary of model scores by metric
                {
                    'model1': {'metric1': 0.9, 'metric2': 0.8, ...},
                    'model2': {'metric1': 0.7, 'metric2': 0.9, ...}
                }
                
        Returns:
            Base64 encoded PNG image
        """
        try:
            # Get list of metrics and models
            metrics = []
            for model, scores in model_scores.items():
                for metric in scores.keys():
                    if metric not in metrics and metric != 'final_score':
                        metrics.append(metric)
            
            models = list(model_scores.keys())
            
            # Number of variables
            N = len(metrics)
            
            # Create a figure
            fig = plt.figure(figsize=(8, 8))
            ax = fig.add_subplot(111, polar=True)
            
            # Angle of each axis
            angles = [n / float(N) * 2 * 3.14159 for n in range(N)]
            angles += angles[:1]  # Close the loop
            
            # Plot for each model
            for i, model in enumerate(models):
                values = [model_scores[model].get(metric, 0) for metric in metrics]
                values += values[:1]  # Close the loop
                
                ax.plot(angles, values, linewidth=2, label=model)
                ax.fill(angles, values, alpha=0.1)
            
            # Fix axis to go clockwise and start from top
            ax.set_theta_offset(3.14159 / 2)
            ax.set_theta_direction(-1)
            
            # Draw axis lines for each angle and label
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels([m.replace('_', ' ').title() for m in metrics])
            
            # Draw y-axis labels (0 to 1)
            ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
            ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'])
            ax.set_ylim(0, 1)
            
            # Add legend
            plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
            
            # Add title
            plt.title('Model Performance Comparison by Metric')
            
            # Save the radar chart to a bytes buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            
            # Encode the bytes to base64
            image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            plt.close()
            
            return image_base64
            
        except Exception as e:
            print(f"Error generating radar chart: {e}")
            return None 