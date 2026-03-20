"""
backend/main.py
---------------
FastAPI backend for the AI-driven Adaptive Learning Engine.

Exposes a single endpoint:
    POST /analyze
        - Accepts a PDF resume + target role string
        - Runs the full AI pipeline:
            resume_parser → skill_gap → adaptive_engine
        - Returns a structured JSON learning plan

How to run:
    From the project root:
        uvicorn backend.main:app --reload --port 8000

Swagger UI (interactive docs):
    http://127.0.0.1:8000/docs

Dependencies:
    pip install fastapi uvicorn python-multipart
    + pdfplumber spacy  (already needed by ai_engine modules)
"""

import logging
import os
import shutil
import sys
import uuid
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ---------------------------------------------------------------------------
# Make sure the project root is on sys.path so ai_engine imports work when
# the server is started from any working directory.
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent   # …/Hckthon art/
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# ---------------------------------------------------------------------------
# AI engine imports
# ---------------------------------------------------------------------------
from ai_engine.resume_parser import extract_text, extract_skills       # noqa: E402
from ai_engine.skill_gap import load_roles, get_required_skills, calculate_skill_gap  # noqa: E402
from ai_engine.adaptive_engine import build_skill_graph, generate_learning_path       # noqa: E402

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
UPLOADS_DIR  = PROJECT_ROOT / "uploads"      # temporary PDF storage
ROLES_FILE   = PROJECT_ROOT / "data" / "roles.json"

# Create the uploads directory on startup (safe even if it already exists)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------------------------
app = FastAPI(
    title="SkillForge API",
    description=(
        "Upload a PDF resume and specify a target role to receive a "
        "personalised skill gap analysis and week-by-week learning roadmap."
    ),
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS – allow the React frontend (and any local dev server) to connect
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # lock down to specific origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===========================================================================
# Health-check endpoint
# ===========================================================================
@app.get("/", summary="Health check", tags=["Status"])
def root():
    """
    Simple health check.
    Returns a 200 with a welcome message — useful for uptime monitoring.
    """
    return {"status": "ok", "message": "SkillForge API is running 🚀"}


# ===========================================================================
# GET /roles – list all available roles
# ===========================================================================
@app.get("/roles", summary="List available roles", tags=["Roles"])
def list_roles():
    """
    Return all role names that can be used as the `target_role` parameter
    in the /analyze endpoint.
    """
    roles_data = load_roles(str(ROLES_FILE))
    if not roles_data:
        raise HTTPException(status_code=500, detail="Could not load roles data.")
    return {"roles": sorted(roles_data.keys())}


# ===========================================================================
# POST /analyze – core AI pipeline
# ===========================================================================
@app.post("/analyze", summary="Analyse resume and generate learning path", tags=["Analysis"])
async def analyze(
    resume: UploadFile = File(
        ...,
        description="PDF resume file to analyse.",
    ),
    target_role: str = Form(
        ...,
        description='Target job role, e.g. "AI Engineer" or "Web Developer".',
    ),
):
    """
    Full AI pipeline:

    1. **Save** the uploaded PDF temporarily.
    2. **Extract** raw text from the PDF (`resume_parser`).
    3. **Identify** user skills via keyword + NLP matching.
    4. **Load** required skills for the target role (`roles.json`).
    5. **Calculate** the skill gap.
    6. **Generate** an ordered, week-by-week learning roadmap (`adaptive_engine`).
    7. **Delete** the temporary file.

    Returns a JSON object containing:
    - `user_skills` – skills detected in the resume
    - `required_skills` – skills the role demands
    - `skill_gap` – what the user is missing
    - `match_percentage` – how complete the user's profile is (0–100)
    - `next_skills` – immediate 3 skills to start learning
    - `learning_path` – full week-by-week roadmap
    """

    # ── Validate file type ──────────────────────────────────────────────────
    if not resume.filename.lower().endswith(".pdf"):
        logger.warning("Rejected upload: '%s' is not a PDF.", resume.filename)
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted. Please upload a .pdf resume.",
        )

    # ── Save upload to a temp file with a unique name ───────────────────────
    unique_name = f"{uuid.uuid4().hex}_{resume.filename}"
    temp_path   = UPLOADS_DIR / unique_name

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(resume.file, buffer)
        logger.info("Step 1 ✔ Saved upload → %s", temp_path.name)

    except Exception as exc:
        logger.error("Failed to save upload: %s", exc)
        raise HTTPException(status_code=500, detail=f"Could not save file: {exc}")

    try:
        # ── Step 2: Extract text ────────────────────────────────────────────
        logger.info("Step 2   Extracting text from PDF …")
        raw_text = extract_text(str(temp_path))

        if not raw_text or not raw_text.strip():
            raise HTTPException(
                status_code=422,
                detail=(
                    "No readable text could be extracted from the PDF. "
                    "The file may be scanned (image-only) or corrupted."
                ),
            )
        logger.info("Step 2 ✔ Extracted %d characters of text.", len(raw_text))

        # ── Step 3: Extract user skills ─────────────────────────────────────
        logger.info("Step 3   Extracting skills via NLP …")
        user_skills = extract_skills(raw_text)
        logger.info("Step 3 ✔ Found %d skill(s): %s", len(user_skills), user_skills)

        if not user_skills:
            logger.warning("No skills found in the resume — proceeding with empty skill set.")

        # ── Step 4: Load role data & required skills ─────────────────────────
        logger.info("Step 4   Loading role data for '%s' …", target_role)
        roles_data = load_roles(str(ROLES_FILE))

        if not roles_data:
            raise HTTPException(
                status_code=500,
                detail="Role dataset could not be loaded. Check that data/roles.json exists.",
            )

        required_skills = get_required_skills(target_role, roles_data)

        if not required_skills:
            available = sorted(roles_data.keys())
            raise HTTPException(
                status_code=404,
                detail=(
                    f"Role '{target_role}' not found. "
                    f"Available roles: {', '.join(available)}"
                ),
            )
        logger.info("Step 4 ✔ Role '%s' requires %d skills.", target_role, len(required_skills))

        # ── Step 5: Calculate skill gap ──────────────────────────────────────
        logger.info("Step 5   Calculating skill gap …")
        from ai_engine.skill_gap import expand_user_skills, SKILL_INFERENCE
        expanded_skills = expand_user_skills(user_skills, SKILL_INFERENCE)
        gap_result = calculate_skill_gap(expanded_skills, required_skills)
        skill_gap  = gap_result["skill_gap"]
        logger.info(
            "Step 5 ✔ Gap: %d missing skill(s). Match: %s%%",
            len(skill_gap),
            gap_result["match_percentage"],
        )

        # ── Step 6: Generate learning path ───────────────────────────────────
        logger.info("Step 6   Generating adaptive learning path …")
        skill_graph    = build_skill_graph()
        ordered_path = generate_learning_path(user_skills, skill_gap, skill_graph)
        
        from ai_engine.adaptive_engine import get_next_skills, create_roadmap
        next_skills = get_next_skills(ordered_path)
        roadmap = create_roadmap(ordered_path)

        logger.info("Step 6 ✔ Learning path: %d weeks.", len(roadmap))

        # ── Build final response ─────────────────────────────────────────────
        response = {
            "user_skills":      gap_result["user_skills"],
            "required_skills":  gap_result["required_skills"],
            "skill_gap":        skill_gap,
            "match_percentage": gap_result["match_percentage"],
            "next_skills":      next_skills,
            "learning_path":    roadmap,
        }

        logger.info("✅ Analysis complete for role '%s'.", target_role)
        return JSONResponse(status_code=200, content=response)

    except HTTPException:
        raise   # re-raise FastAPI HTTP exceptions as-is

    except Exception as exc:
        logger.exception("Unexpected error during analysis: %s", exc)
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred: {str(exc)}",
        )

    finally:
        # ── Step 7: Always clean up the temp file ────────────────────────────
        if temp_path.exists():
            try:
                os.remove(temp_path)
                logger.info("Step 7 ✔ Deleted temp file: %s", temp_path.name)
            except Exception as cleanup_err:
                logger.warning("Could not delete temp file '%s': %s", temp_path.name, cleanup_err)


# ===========================================================================
# Entry point – run directly with: python backend/main.py
# ===========================================================================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,       # auto-reload on file changes during development
        log_level="info",
    )
