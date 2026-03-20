"""
skill_model.py
--------------
Intelligent skill extraction and semantic matching module for the
AI-driven adaptive learning engine.

Architecture
------------
This module intentionally does NOT import spaCy directly, because spaCy's
transitive dependency (confection/thinc) is incompatible with pydantic v2
on Python 3.14. spaCy is used by resume_parser.py in its own isolated call.

Instead this module provides:
  1. Pure-Python NLP extraction  (regex, tokenisation, alias normalisation)
     → Always available, zero extra dependencies.
  2. Sentence-Transformer semantic matching (all-MiniLM-L6-v2)
     → Used automatically when sentence-transformers is installed.
     → Falls back to synonym + substring matching if not importable.

Install:
    pip install sentence-transformers
    (no extra spaCy model download needed for this file)

Integration with the rest of the engine:
    skill_gap.py        → supply user_skills list
    adaptive_engine.py  → pass matched_skills as the skill_gap
    backend/main.py     → call process_skills() after resume text is extracted
"""

import logging
import re
from functools import lru_cache
from typing import Optional

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SIMILARITY_THRESHOLD: float = 0.70     # cosine score above which → match
EMBEDDING_MODEL_NAME: str   = "all-MiniLM-L6-v2"

# ---------------------------------------------------------------------------
# Master skill vocabulary (extend freely – all LOWERCASE)
# ---------------------------------------------------------------------------
DEFAULT_SKILLS: list[str] = [
    # Core programming
    "python", "java", "javascript", "typescript", "c++", "c#",
    "go", "rust", "r", "scala", "kotlin", "swift", "bash",

    # AI / ML / Data
    "machine learning", "deep learning", "nlp",
    "natural language processing", "computer vision",
    "reinforcement learning", "statistics", "data analysis",
    "data science", "data engineering", "feature engineering",
    "mlops",

    # ML libraries
    "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
    "xgboost", "lightgbm", "huggingface", "transformers", "opencv",

    # Data tools
    "pandas", "numpy", "matplotlib", "seaborn", "plotly",
    "excel", "tableau", "power bi",

    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis",
    "elasticsearch", "sqlite", "cassandra",

    # Web / Backend
    "flask", "django", "fastapi", "rest api", "graphql",
    "html", "css", "react", "angular", "vue", "node", "nodejs",

    # DevOps / Cloud
    "docker", "kubernetes", "aws", "azure", "gcp", "google cloud",
    "terraform", "ansible", "git", "linux", "ci/cd",
]

# ---------------------------------------------------------------------------
# Alias / synonym map  (alias → canonical form, all LOWERCASE)
# Extend this to handle new abbreviations or domain jargon.
# ---------------------------------------------------------------------------
CANONICAL_MAP: dict[str, str] = {
    # AI/ML abbreviations
    "ml":                          "machine learning",
    "dl":                          "deep learning",
    "nlp":                         "natural language processing",
    "ai":                          "machine learning",            # treat "ai" as ML (practical)
    "cv":                          "computer vision",
    "sklearn":                     "scikit-learn",

    # Architecture / model names → canonical domains
    "deep neural network":         "deep learning",
    "deep neural networks":        "deep learning",
    "neural network":              "deep learning",
    "neural networks":             "deep learning",
    "transformer":                 "deep learning",
    "cnn":                         "deep learning",
    "rnn":                         "deep learning",
    "lstm":                        "deep learning",
    "llm":                         "natural language processing",
    "large language model":        "natural language processing",
    "language model":              "natural language processing",
    "random forest":               "machine learning",
    "decision tree":               "machine learning",
    "gradient boosting":           "machine learning",
    "svm":                         "machine learning",
    "support vector machine":      "machine learning",
    "regression":                  "statistics",
    "classification":              "machine learning",

    # Node.js variants
    "nodejs":                      "node",
    "node.js":                     "node",
    "express.js":                  "node",

    # Cloud abbreviations
    "gcp":                         "google cloud",
    "k8s":                         "kubernetes",

    # Database aliases
    "postgres":                    "postgresql",
    "pg":                          "postgresql",
    "mongo":                       "mongodb",

    # Library aliases
    "tf":                          "tensorflow",
    "hf":                          "huggingface",
    "plt":                         "matplotlib",
    "pd":                          "pandas",
    "np":                          "numpy",
    "sk":                          "scikit-learn",

    # Tools
    "powerbi":                     "power bi",
    "power-bi":                    "power bi",
    "rest":                        "rest api",
    "restful":                     "rest api",
    "restful api":                 "rest api",
    "restful apis":                "rest api",
    "cicd":                        "ci/cd",
    "ci cd":                       "ci/cd",
}


# ===========================================================================
# Optional: Sentence Transformers (semantic mode)
# ===========================================================================
try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    from sentence_transformers import util as _st_util
    _SEMANTIC_AVAILABLE = True
except ImportError:
    _SEMANTIC_AVAILABLE = False
    logger.warning(
        "sentence-transformers not available. Using synonym + NLP fallback."
    )


_embedding_model = None   # loaded once, reused


def _get_embedding_model():
    """Lazy-load the Sentence Transformer model (singleton)."""
    global _embedding_model
    if _embedding_model is None and _SEMANTIC_AVAILABLE:
        logger.info("Loading '%s'…", EMBEDDING_MODEL_NAME)
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model


@lru_cache(maxsize=64)
def _embed(skills_tuple: tuple):
    """Compute and cache embeddings for a tuple of skill strings."""
    model = _get_embedding_model()
    if model is None:
        return None
    return model.encode(list(skills_tuple), convert_to_numpy=True, normalize_embeddings=True)


# ===========================================================================
# Pure-Python text helpers (no spaCy dependency)
# ===========================================================================
# Simple tokeniser: split on whitespace and common punctuation
_TOKEN_PATTERN = re.compile(r"[a-z][a-z0-9+#.\-/]*")

def _tokenise(text: str) -> set[str]:
    """
    Return a set of lowercase word-like tokens from text.
    Handles compound words like "c++", "scikit-learn", etc.
    """
    return set(_TOKEN_PATTERN.findall(text.lower()))


def _word_boundary_search(pattern: str, text: str) -> bool:
    """Case-insensitive, word-boundary substring search."""
    return bool(re.search(r"\b" + re.escape(pattern) + r"\b", text, re.IGNORECASE))


# ===========================================================================
# A.  NLP-based Skill Extraction  (pure Python, no spaCy)
# ===========================================================================
def extract_skills_nlp(
    text: str,
    skill_list: Optional[list[str]] = None,
) -> list[str]:
    """
    Extract technical skills from resume text using regex tokenisation
    and alias normalisation — no spaCy required.

    Steps
    -----
    1. Tokenise text into lowercase word-like tokens.
    2. For each skill in the vocabulary:
       - Multi-word skill → word-boundary substring search.
       - Single-word skill → token set lookup or substring search.
    3. Scan the CANONICAL_MAP for aliases (e.g. "ml" → "machine learning").
    4. Normalise all matches through CANONICAL_MAP and deduplicate.

    Parameters
    ----------
    text : str
        Raw resume text.
    skill_list : list[str], optional
        Custom skill vocabulary. Defaults to DEFAULT_SKILLS.

    Returns
    -------
    list[str]
        Sorted, deduplicated, normalised skill list.
    """
    if not text or not text.strip():
        logger.warning("extract_skills_nlp: empty text received.")
        return []

    skill_list  = skill_list or DEFAULT_SKILLS
    lower_text  = text.lower()
    tokens      = _tokenise(lower_text)
    raw: set[str] = set()

    # ── Phase 1: skill vocabulary ────────────────────────────────────────────
    for skill in skill_list:
        s = skill.lower().strip()
        if " " in s or "-" in s or "/" in s:
            # Multi-token skill: word-boundary substring match
            if _word_boundary_search(s, lower_text):
                raw.add(s)
        else:
            # Single token: check token set (fast) or substring (with word boundary)
            if s in tokens or _word_boundary_search(s, lower_text):
                raw.add(s)

    # ── Phase 2: alias map scan ──────────────────────────────────────────────
    for alias, canonical in CANONICAL_MAP.items():
        if _word_boundary_search(alias, lower_text):
            raw.add(canonical)   # add the canonical form directly

    # ── Phase 3: normalise via CANONICAL_MAP ────────────────────────────────
    normalised: set[str] = set()
    for skill in raw:
        normalised.add(CANONICAL_MAP.get(skill, skill))

    return sorted(normalised)


# ===========================================================================
# B.  Semantic Skill Matching
# ===========================================================================
def match_skills_semantic(
    user_skills: list[str],
    role_skills:  list[str],
    threshold:    float = SIMILARITY_THRESHOLD,
) -> dict:
    """
    Match user skills against role skills using cosine similarity on
    sentence embeddings (semantic mode) or alias/synonym lookup (fallback).

    Handles synonyms automatically:
        "ml" ≈ "machine learning"   (cos similarity ~0.82)
        "sklearn" ≈ "scikit-learn"   (cos similarity ~0.91)

    Parameters
    ----------
    user_skills : list[str]
        Skills extracted from the resume.
    role_skills : list[str]
        Required skills for the target role.
    threshold : float
        Cosine similarity cutoff. Default: 0.70.

    Returns
    -------
    dict
        {
            "matched_skills":    [...],
            "unmatched_skills":  [...],
            "similarity_scores": {role_skill: score, ...},
            "match_details":     [{"role_skill", "user_skill", "score"}, ...],
            "mode":              "semantic" | "nlp_fallback"
        }
    """
    _empty = {
        "matched_skills":    [],
        "unmatched_skills":  list(role_skills),
        "similarity_scores": {s: 0.0 for s in role_skills},
        "match_details":     [],
        "mode":              "nlp_fallback",
    }

    if not user_skills or not role_skills:
        return _empty

    # ── Semantic mode ────────────────────────────────────────────────────────
    if _SEMANTIC_AVAILABLE:
        try:
            import numpy as _np
            u_embs = _embed(tuple(user_skills))
            r_embs = _embed(tuple(role_skills))
            sim    = _st_util.cos_sim(r_embs, u_embs).numpy()   # (R, U)

            matched, unmatched, scores, details = [], [], {}, []
            for r_idx, rs in enumerate(role_skills):
                row        = sim[r_idx]
                best_idx   = int(_np.argmax(row))
                best_score = float(row[best_idx])
                scores[rs] = round(best_score, 4)
                if best_score >= threshold:
                    matched.append(rs)
                    details.append({
                        "role_skill": rs,
                        "user_skill": user_skills[best_idx],
                        "score":      round(best_score, 4),
                    })
                else:
                    unmatched.append(rs)

            return {
                "matched_skills":    matched,
                "unmatched_skills":  unmatched,
                "similarity_scores": scores,
                "match_details":     details,
                "mode":              "semantic",
            }
        except Exception as exc:
            logger.warning("Semantic matching error (%s). Falling back.", exc)

    # ── Synonym/NLP fallback ─────────────────────────────────────────────────
    # Build an expanded user skill set (canonical + all aliases)
    user_set: set[str] = set()
    for skill in user_skills:
        sk = skill.lower().strip()
        user_set.add(sk)
        # If sk is already canonical, add its aliases
        for alias, canon in CANONICAL_MAP.items():
            if canon == sk:
                user_set.add(alias)
        # If sk is an alias, add its canonical form
        if sk in CANONICAL_MAP:
            user_set.add(CANONICAL_MAP[sk])

    matched, unmatched, scores, details = [], [], {}, []
    for rs in role_skills:
        rs_lower   = rs.lower().strip()
        candidates = {rs_lower, CANONICAL_MAP.get(rs_lower, rs_lower)}
        for alias, canon in CANONICAL_MAP.items():
            if canon == rs_lower:
                candidates.add(alias)

        hit = candidates & user_set
        if hit:
            best = next(iter(hit))
            score = 1.0 if best == rs_lower else 0.85
            matched.append(rs)
            scores[rs] = score
            details.append({"role_skill": rs, "user_skill": best, "score": score})
        else:
            unmatched.append(rs)
            scores[rs] = 0.0

    return {
        "matched_skills":    matched,
        "unmatched_skills":  unmatched,
        "similarity_scores": scores,
        "match_details":     details,
        "mode":              "nlp_fallback",
    }


# ===========================================================================
# C.  Combined Processing Pipeline
# ===========================================================================
def process_skills(
    text:        str,
    role_skills: list[str],
    skill_list:  Optional[list[str]] = None,
    threshold:   float = SIMILARITY_THRESHOLD,
) -> dict:
    """
    End-to-end intelligent skill processing pipeline.

    Steps:
        1. Pure-Python NLP extraction from resume text.
        2. Semantic / NLP matching of extracted skills vs role skills.

    Parameters
    ----------
    text : str
        Raw resume text (output of resume_parser.extract_text()).
    role_skills : list[str]
        Required skills for the target role (from skill_gap.get_required_skills()).
    skill_list : list[str], optional
        Custom skill vocabulary. Defaults to DEFAULT_SKILLS.
    threshold : float
        Cosine similarity cutoff (semantic mode). Default: 0.70.

    Returns
    -------
    dict
        {
            "extracted_skills":  [...],
            "matched_skills":    [...],
            "unmatched_skills":  [...],
            "match_details":     [...],
            "mode":              "semantic" | "nlp_fallback"
        }

    Example
    -------
    >>> result = process_skills("Experienced in Python and ML.", ["python", "machine learning"])
    >>> result["matched_skills"]
    ['machine learning', 'python']
    """
    # Step 1
    extracted = extract_skills_nlp(text, skill_list=skill_list)
    logger.info("process_skills: extracted %d skill(s).", len(extracted))

    if not extracted:
        return {
            "extracted_skills": [],
            "matched_skills":   [],
            "unmatched_skills": list(role_skills),
            "match_details":    [],
            "mode":             "nlp_fallback",
        }

    # Step 2
    result = match_skills_semantic(extracted, role_skills, threshold=threshold)
    result["extracted_skills"] = extracted
    return result


# ===========================================================================
# Helper – pretty printer
# ===========================================================================
def _print_result(result: dict, label: str = "") -> None:
    import json
    mode = result.get("mode", "unknown")
    print(f"\n{'=' * 60}")
    print(f"  {label or 'Skill Model Output'}   [{mode.upper()}]")
    print("=" * 60)

    ext = result.get("extracted_skills", [])
    print(f"\n🔍 Extracted ({len(ext)}):")
    for s in ext or ["(none)"]:
        print(f"   • {s}")

    details = result.get("match_details", [])
    print(f"\n✅ Matched ({len(details)}):")
    for m in details:
        sc  = m["score"]
        bar = "█" * int(sc * 20) + "░" * (20 - int(sc * 20))
        print(f"   {m['role_skill']:30s} ← '{m['user_skill']}' [{bar}] {sc:.2f}")

    unm = result.get("unmatched_skills", [])
    print(f"\n❌ Unmatched ({len(unm)}):")
    for s in unm or ["(none)"]:
        print(f"   • {s}")

    slim = {
        "extracted_skills": ext,
        "matched_skills":   result.get("matched_skills", []),
    }
    print("\nJSON Output:")
    print(json.dumps(slim, indent=2))
    print("=" * 60 + "\n")


# ===========================================================================
# Test block – python ai_engine/skill_model.py
# ===========================================================================
if __name__ == "__main__":
    mode_label = "SEMANTIC" if _SEMANTIC_AVAILABLE else "NLP FALLBACK + SYNONYM"
    print(f"\n🚀 skill_model.py — running in {mode_label} mode\n")

    # Test 1: Synonym / abbreviation handling
    print("[Test 1] 'ML', 'NLP', 'deep neural networks' → canonical matches")
    text1 = """
    Experienced Python developer with 3 years in ML and NLP.
    Built deep neural networks using TensorFlow and Keras.
    Strong in pandas, SQL, and data analysis. Deployed with Docker on AWS.
    """
    role1 = [
        "python", "machine learning", "deep learning",
        "natural language processing", "statistics",
        "tensorflow", "sql", "docker", "aws",
    ]
    r1 = process_skills(text1, role1)
    _print_result(r1, "AI Engineer – Test 1")

    # Test 2: Web Developer
    print("[Test 2] Web Developer profile")
    text2 = "Frontend engineer: React.js, Node.js, TypeScript, REST APIs, Git, HTML, CSS."
    role2 = ["react", "node", "typescript", "javascript", "rest api", "git", "html", "css"]
    r2 = process_skills(text2, role2)
    _print_result(r2, "Web Developer – Test 2")

    # Test 3: Empty text
    print("[Test 3] Empty text edge case")
    r3 = process_skills("", role1)
    _print_result(r3, "Empty – Test 3")

    # Test 4: Direct semantic matching
    import json
    print("[Test 4] match_skills_semantic(['ml','sklearn','python'] vs role)")
    m4 = match_skills_semantic(
        ["ml", "sklearn", "python"],
        ["machine learning", "scikit-learn", "python", "deep learning"],
    )
    print(json.dumps({k: v for k, v in m4.items() if k != "similarity_scores"}, indent=2))
