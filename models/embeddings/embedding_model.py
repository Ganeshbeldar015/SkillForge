"""
embedding_model.py
------------------
AI-powered semantic matching module using SentenceTransformers.
This module provides embedding-based similarity for skill matching,
understanding the *meaning* of skills rather than simple keywords
(e.g., matching "ml" to "machine learning").

Model utilized: 'all-MiniLM-L6-v2' (fast, lightweight, accurate)

Dependencies:
    pip install sentence-transformers

Functions:
    - load_model(): Returns a singleton instance of the model.
    - get_embedding(text): Returns the vector embedding for a given text.
    - compute_similarity(text1, text2): Returns the cosine similarity score.
    - match_skills(user_skills, role_skills): Matches user skills to required skills.
"""

import logging
from functools import lru_cache
from typing import List, Dict, Union

# Attempt to import necessary libraries with graceful fallback/warnings
try:
    import numpy as np
    from sentence_transformers import SentenceTransformer, util
    _ST_AVAILABLE = True
except ImportError:
    _ST_AVAILABLE = False
    logging.warning("sentence-transformers not installed. Please run: pip install sentence-transformers")


# ---------------------------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model Configuration & Singleton
# ---------------------------------------------------------------------------
MODEL_NAME = 'all-MiniLM-L6-v2'

# Global variable to hold the singleton model instance
_model_instance = None


def load_model() -> Union['SentenceTransformer', None]:
    """
    Load the SentenceTransformer model only once (Singleton pattern).
    Avoids reloading the model multiple times during execution.
    
    Returns:
        SentenceTransformer model instance.
    """
    global _model_instance
    if not _ST_AVAILABLE:
        logger.error("Cannot load model: sentence-transformers is not available.")
        return None
        
    if _model_instance is None:
        logger.info(f"Loading SentenceTransformer model '{MODEL_NAME}'...")
        _model_instance = SentenceTransformer(MODEL_NAME)
        logger.info("Model loaded successfully.")
        
    return _model_instance


# ---------------------------------------------------------------------------
# Embedding Generation
# ---------------------------------------------------------------------------
@lru_cache(maxsize=1024)
def get_embedding(text: str):
    """
    Convert input text (skill or sentence) into a vector embedding.
    Uses lru_cache to remember embeddings for previously seen texts,
    optimizing performance significantly when processing multiple resumes.
    
    Args:
        text (str): The skill text to embed.
        
    Returns:
        numpy.ndarray: The vector embedding for the text, or None if failed.
    """
    if not text or not str(text).strip():
        return None
        
    model = load_model()
    if model is None:
        return None
        
    # lowercasing and stripping to ensure consistent cache hits
    clean_text = str(text).strip().lower()
    
    # encode() returns a numpy array since we'll use PyTorch/Numpy utilities
    # normalize_embeddings=True makes cosine similarity just a dot product
    return model.encode(clean_text, convert_to_numpy=True, normalize_embeddings=True)


# ---------------------------------------------------------------------------
# Similarity Computation
# ---------------------------------------------------------------------------
def compute_similarity(text1: str, text2: str) -> float:
    """
    Calculate the cosine similarity between two texts.
    
    Args:
        text1 (str): First text.
        text2 (str): Second text.
        
    Returns:
        float: Cosine similarity score between 0.0 and 1.0.
    """
    if not text1 or not text2:
        return 0.0
        
    emb1 = get_embedding(text1)
    emb2 = get_embedding(text2)
    
    if emb1 is None or emb2 is None:
        return 0.0
        
    # Compute cosine similarity using sentence-transformers util
    cos_sim = util.cos_sim(emb1, emb2)
    
    # Convert tensor to float, extract the single value
    return float(cos_sim[0][0])


# ---------------------------------------------------------------------------
# Skill Matching Logic
# ---------------------------------------------------------------------------
def match_skills(user_skills: List[str], role_skills: List[str], threshold: float = 0.7) -> Dict:
    """
    Compare user skills against role skills semantically.
    If similarity score > threshold, it's considered a match.
    
    Args:
        user_skills (List[str]): Skills the user possesses.
        role_skills (List[str]): Skills required by the target role.
        threshold (float): Minimum cosine similarity to be considered a match.
        
    Returns:
        Dict: Contains matched skills and detailed similarity scores.
    """
    result = {
        "matched_skills": [],
        "match_details": [],
        "similarity_scores": {}
    }
    
    if not user_skills or not role_skills:
        logger.warning("Empty user skills or role skills provided.")
        return result
        
    if not _ST_AVAILABLE:
        logger.error("sentence-transformers unavailable. Cannot perform semantic matching.")
        return result
        
    # To optimize, we embed all skills once
    # Fallback to python list comprehension if get_embedding fails on edge cases
    clean_user = [s for s in user_skills if s and str(s).strip()]
    clean_role = [s for s in role_skills if s and str(s).strip()]
    
    if not clean_user or not clean_role:
        return result
        
    # Get embeddings for all user skills and role skills
    # Since get_embedding is cached, this is fast even inside loops
    user_embs = [get_embedding(s) for s in clean_user]
    role_embs = [get_embedding(s) for s in clean_role]
    
    # Filter out any None embeddings
    valid_user = [(s, e) for s, e in zip(clean_user, user_embs) if e is not None]
    valid_role = [(s, e) for s, e in zip(clean_role, role_embs) if e is not None]
    
    if not valid_user or not valid_role:
        return result
        
    # We can use util.cos_sim directly on matrices for 100x faster execution
    import numpy as np
    
    # Stack lists of 1D arrays into 2D matrices
    u_matrix = np.stack([e for _, e in valid_user])  # shape: (num_user_skills, embedding_dim)
    r_matrix = np.stack([e for _, e in valid_role])  # shape: (num_role_skills, embedding_dim)
    
    # Matrix of shape (num_role_skills, num_user_skills)
    sim_matrix = util.cos_sim(r_matrix, u_matrix).numpy()
    
    matched_skills = []
    match_details = []
    similarity_scores = {}
    
    # For each required role skill, find its highest matching user skill
    for r_idx, (r_name, _) in enumerate(valid_role):
        scores = sim_matrix[r_idx]
        best_u_idx = int(np.argmax(scores))
        best_score = float(scores[best_u_idx])
        
        # Record best score for this role skill
        similarity_scores[r_name] = round(best_score, 4)
        
        # If it passes the threshold, it is a match
        if best_score >= threshold:
            best_u_name = valid_user[best_u_idx][0]
            matched_skills.append(r_name)
            match_details.append({
                "role_skill": r_name,
                "user_skill": best_u_name,
                "score": round(best_score, 4)
            })
            
    result["matched_skills"] = matched_skills
    result["match_details"] = match_details
    result["similarity_scores"] = similarity_scores
    
    return result


# ===========================================================================
# Test Block
# ===========================================================================
if __name__ == "__main__":
    import json
    
    print("--------------------------------------------------")
    print("Testing Semantic Embedding Model (all-MiniLM-L6-v2)")
    print("--------------------------------------------------\n")
    
    # Ensure model is loadable
    m = load_model()
    if m is None:
        print("Model failed to load. Please verify sentence-transformers is installed.")
    else:
        # Example 1: Direct similarity comparison
        print("[Test 1] Testing single similarity logic:")
        t1, t2 = "ml", "machine learning"
        score = compute_similarity(t1, t2)
        print(f"Similarity between '{t1}' and '{t2}': {score:.4f}\n")
        
        # Example 2: List matching
        print("[Test 2] Testing bulk skill matching:")
        example_user_skills = ["python", "ml", "data viz", "neural networks"]
        example_role_skills = ["python", "machine learning", "deep learning", "tableau", "statistics"]
        
        print(f"User Skills: {example_user_skills}")
        print(f"Role Skills: {example_role_skills}")
        
        result_payload = match_skills(example_user_skills, example_role_skills, threshold=0.65)
        
        print("\nJSON Output:")
        # Provide clean JSON output
        slim_output = {
            "matched_skills": result_payload.get("matched_skills", [])
        }
        print(json.dumps(slim_output, indent=2))
        
        print("\nBonus: Detailed Output")
        print(json.dumps(result_payload.get("match_details", []), indent=2))
        
        # Example 3: Edge cases
        print("\n[Test 3] Edge cases (Empty inputs):")
        edge_result = match_skills([], example_role_skills)
        print("Empty user skills result:", edge_result.get("matched_skills"))
