"""
skill_gap.py
------------
Skill Gap Analysis module for the AI-driven adaptive learning engine.

Given a user's current skills (e.g. from resume_parser.py) and a target
role (e.g. "AI Engineer"), this module identifies which skills the user
is missing and assigns a priority score to each gap so the learning
engine knows what to teach first.

Dependencies:
  - Python standard library only (json, os, logging)
  - No external packages required

Usage:
  from ai_engine.skill_gap import analyse_skill_gap

  result = analyse_skill_gap(
      user_skills=["python", "sql"],
      role="AI Engineer",
      roles_file="data/roles.json"
  )
  print(result)
"""

import json
import logging
import os
from typing import Optional

# ---------------------------------------------------------------------------
# Logging – informational messages only; set to DEBUG for verbose output
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Skill Inference Mapping (for implicit prerequisite logic)
# ---------------------------------------------------------------------------
SKILL_INFERENCE = {
    "react": ["html", "css", "javascript"],
    "node": ["javascript"],
    "nodejs": ["javascript"],
    "typescript": ["javascript"],
    "angular": ["html", "css", "javascript", "typescript"],
    "vue": ["html", "css", "javascript"],
    "fastapi": ["python", "rest api"],
    "django": ["python", "sql"],
    "flask": ["python"],
    "machine learning": ["python", "pandas", "numpy", "statistics"],
    "deep learning": ["machine learning"],
    "kubernetes": ["docker"]
}

def expand_user_skills(user_skills: list, skill_inference: dict) -> list:
    """
    Expands the user's skill list by inferring foundational skills.
    e.g., Knowing "react" implies knowing "html", "css", and "javascript".
    
    Bonus Feature: Generates a confidence score map where explicitly named
    skills get 1.0 and inferred skills get 0.85 confidence.
    """
    expanded = set()
    confidence_map = {}
    
    for skill in (user_skills or []):
        clean_skill = str(skill).lower().strip()
        if not clean_skill:
            continue
            
        # Direct skills have 100% confidence
        expanded.add(clean_skill)
        confidence_map[clean_skill] = 1.0
        
        # Add all foundational inferred skills
        if clean_skill in skill_inference:
            inferred_skills = skill_inference[clean_skill]
            for inf in inferred_skills:
                inf_clean = inf.lower().strip()
                expanded.add(inf_clean)
                
                # Assign 85% confidence to dynamically inferred skills
                if inf_clean not in confidence_map:
                    confidence_map[inf_clean] = 0.85
                    
    return sorted(list(expanded))

# ---------------------------------------------------------------------------
# Default path to the roles dataset (relative to project root)
# ---------------------------------------------------------------------------
_DEFAULT_ROLES_PATH = os.path.join(
    os.path.dirname(__file__),   # ai_engine/
    "..",                         # project root
    "data",
    "roles.json",
)


# ---------------------------------------------------------------------------
# Function 1 – Load roles dataset
# ---------------------------------------------------------------------------
def load_roles(file_path: str) -> dict:
    """
    Load role-to-skills mapping from a JSON file.

    Parameters
    ----------
    file_path : str
        Path to the roles JSON file (absolute or relative).

    Returns
    -------
    dict
        A dictionary mapping role names → list of required skills.
        Returns an empty dict on any failure so callers don't crash.

    Example
    -------
    >>> roles = load_roles("data/roles.json")
    >>> roles["AI Engineer"]
    ['python', 'machine learning', 'deep learning', ...]
    """
    if not file_path or not os.path.exists(file_path):
        logger.error("Roles file not found: '%s'", file_path)
        return {}

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict) or not data:
            logger.warning("Roles file is empty or not a valid JSON object.")
            return {}

        # Normalise: lowercase all skill names in every role
        normalised = {
            role: [s.lower().strip() for s in skills]
            for role, skills in data.items()
        }
        logger.info("Loaded %d role(s) from '%s'.", len(normalised), file_path)
        return normalised

    except json.JSONDecodeError as exc:
        logger.error("Invalid JSON in '%s': %s", file_path, exc)
        return {}
    except Exception as exc:
        logger.error("Could not read '%s': %s", file_path, exc)
        return {}


# ---------------------------------------------------------------------------
# Function 2 – Get required skills for a role
# ---------------------------------------------------------------------------
def get_required_skills(role: str, roles_data: dict) -> list:
    """
    Return the list of skills required for a given role.

    The lookup is case-insensitive so "ai engineer" and "AI Engineer"
    both work correctly.

    Parameters
    ----------
    role : str
        Target role name (e.g. "AI Engineer").
    roles_data : dict
        Loaded roles dictionary from load_roles().

    Returns
    -------
    list[str]
        List of required skills (lowercase, deduplicated).
        Returns an empty list when the role is not found.
    """
    if not role or not isinstance(role, str):
        logger.warning("get_required_skills: invalid role argument '%s'.", role)
        return []

    if not roles_data:
        logger.warning("get_required_skills: roles_data is empty.")
        return []

    # Case-insensitive lookup
    role_lower = role.strip().lower()
    for key, skills in roles_data.items():
        if key.lower() == role_lower:
            # Deduplicate while preserving order (important for priority scoring)
            seen = set()
            deduped = []
            for s in skills:
                if s not in seen:
                    seen.add(s)
                    deduped.append(s)
            return deduped

    # Role not found – list available roles to help the caller
    available = ", ".join(sorted(roles_data.keys()))
    logger.warning(
        "Role '%s' not found. Available roles: %s", role, available
    )
    return []


# ---------------------------------------------------------------------------
# Function 3 – Calculate skill gap
# ---------------------------------------------------------------------------
def calculate_skill_gap(
    user_skills: list,
    required_skills: list,
) -> dict:
    """
    Compute the difference between required and user skills.

    Skill Gap = Required Skills − User Skills

    Parameters
    ----------
    user_skills : list[str]
        Skills the user already has (from resume_parser.py or manual input).
    required_skills : list[str]
        Skills the target role demands (from get_required_skills()).

    Returns
    -------
    dict with keys:
        "user_skills"      – normalised, deduplicated user skill list
        "required_skills"  – normalised required skill list
        "skill_gap"        – missing skills (in role-definition order)
        "gap_with_priority"– list of {"skill": ..., "priority": ...} dicts
        "match_percentage" – how many required skills the user already has (0–100)

    Priority scores
    ---------------
    Skills are scored by their position in the role's required list.
    The first skill has the highest priority (score = total skills),
    the last has the lowest (score = 1).  This reflects domain conventions
    where the most critical skills are typically listed first.
    """
    # ---- Normalise inputs --------------------------------------------------
    def _normalise(skills: list) -> list:
        """Lowercase, strip whitespace, remove blanks, deduplicate."""
        seen = set()
        result = []
        for s in (skills or []):
            clean = str(s).lower().strip()
            if clean and clean not in seen:
                seen.add(clean)
                result.append(clean)
        return result

    norm_user = _normalise(user_skills)
    norm_required = _normalise(required_skills)

    # ---- Core gap calculation -----------------------------------------------
    user_set = set(norm_user)
    gap = [skill for skill in norm_required if skill not in user_set]

    # ---- Priority scoring ---------------------------------------------------
    # Skills earlier in the required list get a higher priority number.
    total = len(norm_required)
    priority_map = {
        skill: total - idx
        for idx, skill in enumerate(norm_required)
    }

    gap_with_priority = [
        {"skill": skill, "priority": priority_map.get(skill, 0)}
        for skill in gap
    ]
    # Sort so highest-priority gaps come first
    gap_with_priority.sort(key=lambda x: x["priority"], reverse=True)

    # ---- Match percentage ---------------------------------------------------
    if total == 0:
        match_pct = 0.0
    else:
        matched = sum(1 for s in norm_required if s in user_set)
        match_pct = round((matched / total) * 100, 1)

    return {
        "user_skills": norm_user,
        "required_skills": norm_required,
        "skill_gap": gap,
        "gap_with_priority": gap_with_priority,
        "match_percentage": match_pct,
    }


# ---------------------------------------------------------------------------
# Function 4 – High-level convenience wrapper (public API)
# ---------------------------------------------------------------------------
def analyse_skill_gap(
    user_skills: list,
    role: str,
    roles_file: Optional[str] = None,
) -> dict:
    """
    End-to-end skill gap analysis.

    Combines load_roles → get_required_skills → calculate_skill_gap
    into a single call for easy integration with the rest of the engine.

    Parameters
    ----------
    user_skills : list[str]
        Skills extracted from the resume (or supplied manually).
    role : str
        Target job role, e.g. "AI Engineer".
    roles_file : str, optional
        Path to roles.json. Defaults to data/roles.json relative to project root.

    Returns
    -------
    dict
        Full skill gap report (see calculate_skill_gap for schema).
        Returns a safe empty report on any failure.

    Example
    -------
    >>> result = analyse_skill_gap(["python", "sql"], "AI Engineer")
    >>> result["skill_gap"]
    ['machine learning', 'deep learning', 'nlp', 'statistics', ...]
    """
    _empty_report = {
        "user_skills": [],
        "required_skills": [],
        "skill_gap": [],
        "gap_with_priority": [],
        "match_percentage": 0.0,
    }

    # Resolve roles file path
    path = roles_file or _DEFAULT_ROLES_PATH

    # Step 1 – Load dataset
    roles_data = load_roles(path)
    if not roles_data:
        logger.error("analyse_skill_gap: could not load roles data.")
        return _empty_report

    # Step 2 – Get required skills for the role
    required = get_required_skills(role, roles_data)
    if not required:
        logger.warning("analyse_skill_gap: no required skills found for role '%s'.", role)
        return {**_empty_report, "user_skills": [s.lower().strip() for s in (user_skills or [])]}

    # Step 3 – Compute gap using intelligent inference
    expanded_skills = expand_user_skills(user_skills, SKILL_INFERENCE)
    return calculate_skill_gap(expanded_skills, required)


# ---------------------------------------------------------------------------
# Helper – pretty-print utility
# ---------------------------------------------------------------------------
def _print_report(report: dict, role: str) -> None:
    """Display the skill gap report in a readable format."""
    print("\n" + "=" * 55)
    print(f"  Skill Gap Report  ›  Target Role: {role}")
    print("=" * 55)

    print(f"\n✅ Your skills ({len(report['user_skills'])}):")
    for s in report["user_skills"] or ["(none)"]:
        print(f"   • {s}")

    print(f"\n🎯 Required skills ({len(report['required_skills'])}):")
    for s in report["required_skills"] or ["(none)"]:
        marker = "✔" if s in report["user_skills"] else "✘"
        print(f"   {marker} {s}")

    print(f"\n❌ Skill gaps ({len(report['skill_gap'])}):")
    if report["gap_with_priority"]:
        for item in report["gap_with_priority"]:
            print(f"   • {item['skill']:30s}  priority: {item['priority']}")
    else:
        print("   (none – you already have all required skills! 🎉)")

    print(f"\n📊 Profile match: {report['match_percentage']}%")
    print("=" * 55 + "\n")

    # Also print raw JSON for programmatic use
    print("JSON Output:")
    # Slim output matching the spec (user_skills, required_skills, skill_gap)
    slim = {
        "user_skills":     report["user_skills"],
        "required_skills": report["required_skills"],
        "skill_gap":       report["skill_gap"],
    }
    print(json.dumps(slim, indent=2))
    print()


# ---------------------------------------------------------------------------
# Test block – run directly:  python ai_engine/skill_gap.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    import os

    # ── Test case 1: Partial match ──────────────────────────────────────────
    test_user_skills = ["python", "sql", "pandas"]
    test_role = "AI Engineer"

    print("\n[Test 1] Partial skill match")
    result1 = analyse_skill_gap(
        user_skills=test_user_skills,
        role=test_role,
    )
    _print_report(result1, test_role)

    # ── Test case 2: All skills already present ─────────────────────────────
    print("[Test 2] User already has all skills")
    full_skills = [
        "html", "css", "javascript", "react", "node",
        "typescript", "rest api", "git", "sql"
    ]
    result2 = analyse_skill_gap(full_skills, "Web Developer")
    _print_report(result2, "Web Developer")

    # ── Test case 3: Implicit Skills Validation ─────────────────────────────
    print("\n[Test 3] Implicit Skills Validation (React & Node)")
    inf_user_skills = ["react", "node"]
    inf_required_skills = ["html", "css", "javascript", "react", "node", "typescript"]
    
    inf_expanded = expand_user_skills(inf_user_skills, SKILL_INFERENCE)
    inf_result = calculate_skill_gap(inf_expanded, inf_required_skills)
    
    print(f"user_skills = {inf_user_skills}")
    print(f"required_skills = {inf_required_skills}")
    print(f"Expected Output:\nSkill Gap = ['typescript']")
    print(f"Actual Output:\nSkill Gap = {inf_result['skill_gap']}")

    # ── Test case 4: Role not found ─────────────────────────────────────────
    print("[Test 4] Unknown role")
    result4 = analyse_skill_gap(["python"], "Quantum Wizard")
    _print_report(result4, "Quantum Wizard")
