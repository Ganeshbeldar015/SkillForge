# SkillForge Deployment Guide

This guide covers deploying SkillForge with:
- **Frontend** on Vercel
- **Backend** on Render

---

## Step 1: Deploy Backend to Render

### 1. Create Render Account
- Go to [render.com](https://render.com) and sign up/login

### 2. Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub/GitLab repository
3. Search for and select the SkillForge repo

### 3. Configure Service
| Setting | Value |
|---------|-------|
| Name | `skillforge-backend` |
| Runtime | Python 3 |
| Build Command | `pip install -r backend/requirements.txt && python -m spacy download en_core_web_sm` |
| Start Command | `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Plan | Free |

### 4. Add Environment Variables
In the Render dashboard, add:
- `OPENAI_API_KEY` = your OpenAI API key

### 5. Deploy
Click **"Create Web Service"**

Wait for deployment to complete. Note the URL: `https://skillforge-backend.onrender.com`

---

## Step 2: Deploy Frontend to Vercel

### 1. Create Vercel Account
- Go to [vercel.com](https://vercel.com) and sign up/login

### 2. Import Project
1. Click **"Add New..."** → **"Project"**
2. Import your GitHub/GitLab repository

### 3. Configure Project
| Setting | Value |
|---------|-------|
| Framework Preset | Create React App |
| Root Directory | `frontend` |
| Build Command | `npm run build` |
| Output Directory | `build` |

### 4. Add Environment Variables
Add this variable:
- `REACT_APP_API_URL` = `https://skillforge-backend.onrender.com` (your Render backend URL)

### 5. Deploy
Click **"Deploy"**

Your frontend will be live at `https://skillforge-frontend.vercel.app` (or similar)

---

## Important Notes

### CORS Configuration
The backend already allows all origins (`allow_origins=["*"]`), which works for deployment. For production security, update `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-vercel-app.vercel.app"],  # Your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Environment Files Created
- `render.yaml` - Render service configuration
- `vercel.json` - Vercel deployment configuration
- `frontend/.env.example` - Frontend env template
- `.env.example` - Backend env template

### Post-Deployment Verification
1. Backend health check: Visit `https://your-render-url/`
   - Should show: `{"status": "ok", "message": "SkillForge API is running 🚀"}`
2. Frontend: Visit your Vercel URL
3. Test: Upload a resume and analyze

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 500 errors | Check Render logs; verify OPENAI_API_KEY |
| CORS errors | Ensure CORS origins include your Vercel domain |
| spacy model error | Ensure `python -m spacy download en_core_web_sm` runs in build |
| API not connecting | Verify REACT_APP_API_URL matches Render URL |
