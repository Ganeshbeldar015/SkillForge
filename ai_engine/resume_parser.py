"""
resume_parser.py
----------------
A lightweight resume parsing module for the AI-driven adaptive learning engine.

Key capabilities:
  - Extract raw text from a PDF resume using pdfplumber
  - Identify technical skills using spaCy NLP + keyword matching
  - Return structured JSON output for downstream skill-gap analysis

Dependencies:
  pip install pdfplumber spacy
  python -m spacy download en_core_web_sm
"""

import json
import logging
import pdfplumber
from .llm_client import is_llm_active, get_llm_client

# ---------------------------------------------------------------------------
# Logging setup – keeps debug messages out of production output by default
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Load the spaCy language model once at module level (cheap reuse)
# ---------------------------------------------------------------------------
nlp = None
try:
    import spacy
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        logger.warning(
            "spaCy model 'en_core_web_sm' not found.\n"
            "Run:  python -m spacy download en_core_web_sm"
        )
except Exception as e:
    logger.warning(f"Failed to load spaCy (likely Python 3.14 pydantic issue): {e}. Falling back to basic tokenization.")

# ---------------------------------------------------------------------------
# Master skill list – extend this list freely to support new domains.
# All entries MUST be lowercase for matching to work correctly.
# ---------------------------------------------------------------------------
DEFAULT_SKILLS = [
    "python",
    "machine learning",
    "deep learning",
    "nlp",
    "natural language processing",
    "sql",
    "mysql",
    "postgresql",
    "react",
    "node",
    "nodejs",
    "data analysis",
    "statistics",
    "tensorflow",
    "pytorch",
    "scikit-learn",
    "pandas",
    "numpy",
    "java",
    "javascript",
    "typescript",
    "c++",
    "docker",
    "kubernetes",
    "aws",
    "azure",
    "git",
    "linux",
    "rest api",
    "graphql",
    "flask",
    "django",
    "fastapi",
    "excel",
    "tableau",
    "power bi",
]


# ---------------------------------------------------------------------------
# Function 1 – Text extraction
# ---------------------------------------------------------------------------
def extract_text(pdf_path: str) -> str:
    """
    Extract all text from a PDF file using pdfplumber.

    Parameters
    ----------
    pdf_path : str
        Absolute or relative path to the PDF resume.

    Returns
    -------
    str
        Concatenated text from all pages, or an empty string on failure.

    Raises
    ------
    FileNotFoundError
        If the file path does not exist.
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if len(pdf.pages) == 0:
                logger.warning("PDF '%s' has no pages.", pdf_path)
                return ""

            pages_text = []
            for page in pdf.pages:
                page_content = page.extract_text()
                if page_content:              # some pages may return None
                    pages_text.append(page_content)

            full_text = "\n".join(pages_text).strip()

            if not full_text:
                logger.warning("No readable text found in '%s'.", pdf_path)

            return full_text

    except FileNotFoundError:
        logger.error("File not found: '%s'", pdf_path)
        raise
    except Exception as exc:
        # Catch pdfplumber / corrupted-file errors gracefully
        logger.error("Could not read PDF '%s': %s", pdf_path, exc)
        return ""


# ---------------------------------------------------------------------------
# Function 2 – Skill extraction
# ---------------------------------------------------------------------------
def extract_skills(text: str, skill_list: list[str] = None) -> list[str]:
    """
    Identify technical skills present in the resume text.

    Strategy
    --------
    1. Lowercase + tokenise the text with spaCy (handles punctuation cleanly).
    2. For single-word skills, check against the token set directly.
    3. For multi-word skills (e.g. "machine learning"), do a substring search
       on the lowercased full text – fast and accurate enough for this use case.

    Parameters
    ----------
    text : str
        Raw resume text returned by extract_text().
    skill_list : list[str], optional
        Custom skill list. Defaults to DEFAULT_SKILLS.

    Returns
    -------
    list[str]
        Sorted, deduplicated list of matched skill names (lowercase).
    """
    if not text:
        return []

    if skill_list is None:
        skill_list = DEFAULT_SKILLS

    # Normalize the resume text once
    lower_text = text.lower()

    if nlp is not None:
        # Use spaCy to get individual tokens (strips punctuation, etc.)
        doc = nlp(lower_text)
        token_set = {token.lemma_ for token in doc if not token.is_space}
    else:
        # Fallback tokenization if spaCy failed to load (e.g. on Python 3.14)
        import re
        words = re.findall(r'\b\w+\b', lower_text)
        token_set = set(words)

    matched_skills = set()

    for skill in skill_list:
        skill_lower = skill.lower()

        if " " in skill_lower:
            # Multi-word skill: substring match on the full text
            if skill_lower in lower_text:
                matched_skills.add(skill_lower)
        else:
            # Single-word skill: check against spaCy token lemmas
            if skill_lower in token_set or skill_lower in lower_text:
                matched_skills.add(skill_lower)

    return sorted(matched_skills)   # sorted for deterministic output


# ---------------------------------------------------------------------------
# Function 2.5 – LLM Skill Extraction (OpenAI)
# ---------------------------------------------------------------------------
def extract_skills_llm(text: str) -> list[str]:
    """Uses OpenAI API to extract technical skills accurately."""
    client = get_llm_client()
    if not client:
        return []
        
    prompt = f"Extract a clean, comma-separated list of ONLY the technical skills from this resume text. Return ONLY the skills, all lowercase, separated by commas. No extra conversational text.\n\nResume Text:\n{text}"
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a precise technical skill extractor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1
        )
        content = response.choices[0].message.content.strip()
        if content:
            skills = [s.strip().lower() for s in content.split(',')]
            return sorted(list(set(s for s in skills if s)))
    except Exception as e:
        logger.error(f"LLM extraction failed: {e}")
        
    return []


# ---------------------------------------------------------------------------
# Function 3 – Public API entry point
# ---------------------------------------------------------------------------
def parse_resume(pdf_path: str, skill_list: list[str] = None) -> dict:
    """
    Parse a resume PDF and return a structured result dictionary.

    Parameters
    ----------
    pdf_path : str
        Path to the PDF resume file.
    skill_list : list[str], optional
        Custom skill list. Defaults to DEFAULT_SKILLS.

    Returns
    -------
    dict
        {
            "skills": ["python", "sql", ...]   # matched skills, sorted
        }
        Returns {"skills": []} when no skills are found or on parse failure.

    Example
    -------
    >>> result = parse_resume("resumes/john_doe.pdf")
    >>> print(result)
    {'skills': ['machine learning', 'python', 'sql']}
    """
    result = {"skills": []}

    # Step 1 – Extract text
    text = extract_text(pdf_path)
    if not text:
        logger.warning("parse_resume: empty text extracted from '%s'.", pdf_path)
        return result

    # Step 2 – Extract skills
    if is_llm_active():
        logger.info("parse_resume: Using OpenAI LLM for skill extraction...")
        skills = extract_skills_llm(text)
        if not skills:
            logger.warning("LLM extraction failed/empty. Falling back to local NLP.")
            skills = extract_skills(text, skill_list=skill_list)
    else:
        skills = extract_skills(text, skill_list=skill_list)

    if not skills:
        logger.info("parse_resume: no matching skills found in '%s'.", pdf_path)

    result["skills"] = skills
    return result


# ---------------------------------------------------------------------------
# Helper – pretty-print utility
# ---------------------------------------------------------------------------
def _print_result(result: dict, pdf_path: str) -> None:
    """Print the parsed result in a human-readable format."""
    print("\n" + "=" * 50)
    print(f"Resume : {pdf_path}")
    print("=" * 50)

    skills = result.get("skills", [])
    if skills:
        print(f"✅ Skills found ({len(skills)}):")
        for skill in skills:
            print(f"   • {skill}")
    else:
        print("⚠️  No recognised skills found.")

    print("\nJSON output:")
    print(json.dumps(result, indent=2))
    print("=" * 50 + "\n")


# ---------------------------------------------------------------------------
# Test block – run this file directly to try it out
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    # Accept an optional PDF path as a CLI argument; fall back to a placeholder
    if len(sys.argv) > 1:
        sample_pdf = sys.argv[1]
    else:
        # ⚠️  Replace this path with a real PDF on your machine for testing
        sample_pdf = "sample_resume.pdf"

    print(f"\nParsing resume: {sample_pdf}")

    try:
        parsed = parse_resume(sample_pdf)
        _print_result(parsed, sample_pdf)

    except FileNotFoundError:
        print(f"\n❌ File not found: '{sample_pdf}'")
        print("Usage:  python resume_parser.py path/to/resume.pdf")

    except Exception as unexpected:
        print(f"\n❌ Unexpected error: {unexpected}")
