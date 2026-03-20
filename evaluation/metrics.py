"""
Evaluation metrics for the AI-driven adaptive learning engine.
These metrics help validate the system's effectiveness for skill extraction,
gap analysis, and recommendation generation.
"""
from typing import List
import logging

# Configure basic logging for the module
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def skill_extraction_accuracy(predicted_skills: List[str], actual_skills: List[str]) -> float:
    """
    Measures how many of the actual skills were correctly extracted.
    Formula: Accuracy = (Correctly Extracted Skills / Total Actual Skills)
    """
    if not actual_skills:
        logging.warning("actual_skills is empty. Returning 0.0 to avoid division by zero.")
        return 0.0
    
    # Convert lists to sets for fast, case-insensitive comparison
    predicted_set = {skill.strip().lower() for skill in predicted_skills}
    actual_set = {skill.strip().lower() for skill in actual_skills}
    
    # Find correctly extracted skills (intersection)
    correctly_extracted = len(predicted_set.intersection(actual_set))
    accuracy = correctly_extracted / len(actual_set)
    
    return round(accuracy, 4)


def skill_gap_reduction(initial_gap_count: int, final_gap_count: int) -> float:
    """
    Measures the percentage reduction in the skill gap after a user takes the learning content.
    Formula: Reduction % = ((Initial Gap - Final Gap) / Initial Gap) * 100
    """
    if initial_gap_count <= 0:
        logging.warning("initial_gap_count is zero or negative. Returning 0.0.")
        return 0.0
    
    reduction = ((initial_gap_count - final_gap_count) / initial_gap_count) * 100.0
    return round(reduction, 2)


def recommendation_precision(recommended_skills: List[str], relevant_skills: List[str]) -> float:
    """
    Checks how many recommended skills or courses are actually relevant to the user.
    Formula: Precision = (Relevant Recommended Skills / Total Recommended Skills)
    """
    if not recommended_skills:
        logging.warning("recommended_skills is empty. Returning 0.0.")
        return 0.0
        
    recommended_set = {skill.strip().lower() for skill in recommended_skills}
    relevant_set = {skill.strip().lower() for skill in relevant_skills}
    
    relevant_recommended = len(recommended_set.intersection(relevant_set))
    precision = relevant_recommended / len(recommended_set)
    
    return round(precision, 4)


def learning_efficiency(completion_rate: float, avg_score: float, time_taken: float) -> float:
    """
    Combines completion rate, performance score, and time taken to calculate an efficiency score.
    Higher score means better efficiency. Max score is generally around 100.
    """
    # Base score using an even weight between completion rate and average score
    base_score = (completion_rate + avg_score) / 2.0
    
    # Simple logic: Introduce a slight penalty if the time taken is relatively high
    # Assuming standard time is 5.0 units. Time > 5 starts giving a penalty.
    time_penalty = max(0.0, (time_taken - 5.0) * 0.5)
    
    efficiency = base_score - time_penalty
    
    return round(max(0.0, min(100.0, efficiency)), 2)


# --- Bonus Features ---

def calculate_f1_score(predicted_skills: List[str], actual_skills: List[str]) -> float:
    """
    Calculates the F1-score for skill extraction, balancing precision and recall.
    Formula: F1 = 2 * (Precision * Recall) / (Precision + Recall)
    """
    if not predicted_skills or not actual_skills:
        return 0.0
        
    predicted_set = {skill.strip().lower() for skill in predicted_skills}
    actual_set = {skill.strip().lower() for skill in actual_skills}
    
    correct = len(predicted_set.intersection(actual_set))
    
    precision = correct / len(predicted_set) if predicted_set else 0.0
    recall = correct / len(actual_set) if actual_set else 0.0
    
    if precision + recall == 0:
        return 0.0
        
    f1 = 2 * (precision * recall) / (precision + recall)
    return round(f1, 4)
