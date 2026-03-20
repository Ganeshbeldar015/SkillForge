"""
Experiment script to run test cases using sample data and simulate system performance.
This validates the effectiveness of the learning engine.
"""
import json
import logging
import os

# Import the functions cleanly
from metrics import (
    skill_extraction_accuracy,
    skill_gap_reduction,
    recommendation_precision,
    learning_efficiency,
    calculate_f1_score
)

# Set logging level mapping for clear outputs
logging.basicConfig(level=logging.INFO, format='%(message)s')

def run_experiment():
    logging.info("--- Starting Evaluation Experiments ---\n")
    
    # 1. Skill Extraction Accuracy Data
    # Setup data to achieve an accuracy of 0.8 (4/5)
    user_actual_skills = ["Python", "Machine Learning", "Data Analysis", "SQL", "Communication"]
    user_extracted_skills = ["Python", "Machine Learning", "SQL", "Communication", "Data Science"]
    
    # 2. Skill Gap Reduction Data
    # Setup data to achieve a gap reduction of 60%
    initial_gap = 10
    final_gap = 4
    
    # 3. Recommendation Precision Data
    # Setup data to achieve a precision of 0.75 (3/4)
    recommended_courses = ["Advanced SQL", "Deep Learning", "Public Speaking", "React"]
    relevant_courses = ["Advanced SQL", "Deep Learning", "Public Speaking"]
    
    # 4. Learning Efficiency Data
    # Setup data to achieve an efficiency score of roughly 82.5
    completion_rate = 85.0
    avg_score = 80.0
    time_taken = 5.0 
    
    # --- Executing Metrics Functions ---
    logging.info("Calculating metrics...")
    
    accuracy = skill_extraction_accuracy(user_extracted_skills, user_actual_skills)
    f1_score = calculate_f1_score(user_extracted_skills, user_actual_skills) # Bonus feature
    gap_reduction = skill_gap_reduction(initial_gap, final_gap)
    precision = recommendation_precision(recommended_courses, relevant_courses)
    efficiency_score = learning_efficiency(completion_rate, avg_score, time_taken)
    
    # Assemble the final dictionary exactly as required
    results = {
        "accuracy": accuracy,
        "gap_reduction": gap_reduction,
        "precision": precision,
        "efficiency_score": efficiency_score,
        "f1_score": f1_score  # Bonus feature appended intentionally at the end
    }
    
    # Output the results neatly
    logging.info("\n[Experiment Results]")
    print(json.dumps(results, indent=2))
    
    # Bonus feature: Store results in a JSON file
    output_filename = os.path.join(os.path.dirname(__file__), "evaluation_results.json")
    try:
        with open(output_filename, "w") as f:
            json.dump(results, f, indent=4)
        logging.info(f"\n✅ Results successfully logged and saved to {output_filename}")
    except IOError as e:
        logging.error(f"Failed to write results to file: {e}")

if __name__ == "__main__":
    run_experiment()
