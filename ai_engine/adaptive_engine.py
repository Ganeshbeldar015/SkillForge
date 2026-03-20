"""
adaptive_engine.py
------------------
Engine for generating dependency-aware and priority-sorted learning paths.
Implements DFS-based topological sorting and difficulty levels.
"""

import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

# --- 1. Skill Dependency Graph ---
def build_skill_graph() -> dict:
    return {
        "html": [],
        "css": ["html"],
        "javascript": ["html", "css"],
        "typescript": ["javascript"],
        "react": ["javascript", "html", "css"],
        "node": ["javascript"],
        "python": [],
        "pandas": ["python"],
        "machine learning": ["python", "pandas"],
        "deep learning": ["machine learning"],
        "sql": [],
        "postgresql": ["sql"],
        "rest api": ["python"],
        "fastapi": ["python", "rest api"],
        "docker": [],
        "kubernetes": ["docker"]
    }

# --- 2. Priority Maps ---
# Lower number -> Higher priority (learned first)
PRIORITY_MAP = {
    "html": 1,
    "css": 2,
    "javascript": 3,
    "python": 3,
    "sql": 3,
    "typescript": 4,
    "pandas": 4,
    "rest api": 4,
    "react": 5,
    "node": 5,
    "machine learning": 5,
    "fastapi": 5,
    "postgresql": 5,
    "docker": 6,
    "deep learning": 6,
    "kubernetes": 7
}

# Bonus: Difficulty levels
DIFFICULTY_MAP = {
    "html": "Beginner",
    "css": "Beginner",
    "javascript": "Intermediate",
    "python": "Beginner",
    "sql": "Beginner",
    "typescript": "Intermediate",
    "react": "Advanced",
    "node": "Intermediate",
    "pandas": "Intermediate",
    "machine learning": "Advanced",
    "deep learning": "Expert",
    "rest api": "Intermediate",
    "fastapi": "Advanced",
    "postgresql": "Intermediate",
    "docker": "Intermediate",
    "kubernetes": "Advanced"
}

# --- 3. DFS Algorithm for Dependency Handling ---
def generate_learning_path(user_skills: list, skill_gap: list, skill_graph: dict) -> list:
    """
    Generates an ordered learning path using Priority-Driven DFS to ensure all 
    prerequisites are met while respecting curriculum priorities natively.
    """
    user_skills_set = {s.lower().strip() for s in user_skills}
    skill_gap_clean = [s.lower().strip() for s in skill_gap]
    
    visited = set()
    ordered_list = []
    
    def dfs_traverse(skill: str):
        if skill in visited or skill in user_skills_set:
            return
            
        visited.add(skill)
        
        # Sort prerequisites by priority to enforce correct topological processing
        prereqs = skill_graph.get(skill, [])
        prereqs_sorted = sorted(prereqs, key=lambda s: PRIORITY_MAP.get(s, 99))
        
        for prereq in prereqs_sorted:
            if prereq not in visited and prereq not in user_skills_set:
                dfs_traverse(prereq)
                
        # Add skill after prerequisites are fulfilled
        ordered_list.append(skill)
        
    # Process skill gap from highest priority to lowest
    skill_gap_sorted = sorted(skill_gap_clean, key=lambda s: PRIORITY_MAP.get(s, 99))
    
    for skill in skill_gap_sorted:
        if skill not in user_skills_set:
            dfs_traverse(skill)
            
    return ordered_list


# --- 4. Generate 'Next Skills' List ---
def get_next_skills(learning_path: list) -> list:
    """Return the first 2-3 skills from the ordered learning path."""
    return learning_path[:3]


# --- 5. Generate Week-wise Roadmap ---
def create_roadmap(learning_path: list) -> list:
    """Formats raw ordered skills into a week-by-week roadmap with difficulty levels."""
    roadmap = []
    for idx, skill in enumerate(learning_path, 1):
        difficulty = DIFFICULTY_MAP.get(skill, "Intermediate")
        roadmap.append(f"Week {idx}: Learn {skill} ({difficulty})")
    return roadmap


# --- 6. Test Case Execution ---
if __name__ == "__main__":
    test_user_skills = ["javascript"]
    test_skill_gap   = ["html", "css", "typescript"]
    test_graph       = build_skill_graph()
    
    ordered_path = generate_learning_path(test_user_skills, test_skill_gap, test_graph)
    next_skills = get_next_skills(ordered_path)
    roadmap = create_roadmap(ordered_path)
    
    print("--- DFS Test Case ---")
    print(f"user_skills = {test_user_skills}")
    print(f"skill_gap   = {test_skill_gap}")
    print("\nExpected Output:\nhtml -> css -> typescript")
    print("\nActual Output:\n" + " -> ".join(ordered_path))
    
    print("\nRoadmap Verification:")
    import json
    print(json.dumps({"next_skills": next_skills, "learning_path": roadmap}, indent=2))
