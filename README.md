# SkillForge: AI-Driven Adaptive Learning Engine

A full-stack application that analyzes resumes, identifies skill gaps, and dynamically generates dependency-aware, priority-sorted learning syllabuses. 

## Features
* **Resume Parser:** Intelligent scraping of PDFs.
* **LLM Integration:** Automatically expands implicit foundational skills and generates rich weekly curriculums using OpenAI.
* **Offline Fallbacks:** Includes an automatic safety net that forces local Regex/NLP processing if the Wi-Fi drops or the API key expires.
* **DFS Adaptive Engine:** Prioritizes prerequisites using topological Depth-First-Search ensuring logically ordered learning roadmaps.

## 🚀 Full Setup Workflow

### 1. Backend Setup (FastAPI & Python AI Engine)
1. Open a terminal and navigate to the project root.
2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   
   # Windows:
   .\venv\Scripts\activate
   
   # Mac/Linux:
   source venv/bin/activate
   ```
3. Install the engine dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
4. Configure your API Key:
   * Open the `.env` file in the root directory and paste your OpenAI API Key:
   ```text
   OPENAI_API_KEY="sk-your-key-here"
   ```
   *(Note: If left empty, the engine automatically falls back to local NLP tokenization so the demo never crashes!)*
5. Start the backend server:
   ```bash
   # Make sure you are in your backend folder!
   cd backend
   python main.py
   ```
   *The backend will run on `http://127.0.0.1:8000`*

---

### 2. Frontend Setup (React)
1. Open a **second** new terminal and navigate to the frontend folder.
2. Install the Node dependencies:
   ```bash
   cd frontend
   npm install
   ```
3. Start the React development server:
   ```bash
   npm start
   ```
   *The web app will automatically open in your browser at `http://localhost:3000`*

## How to Test During the Hackathon
1. Keep both the Backend and Frontend terminal windows running simultaneously.
2. Go to `http://localhost:3000` in Google Chrome.
3. Upload a sample PDF resume and type in a target role (e.g., "AI Engineer", "Web Developer").
4. Click submit and watch the AI dynamically calculate the skill gap and generate the perfectly ordered DFS syllabus!
