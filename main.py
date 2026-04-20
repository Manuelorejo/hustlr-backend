from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Body
from scrapers import jobberman, linkedln, hotnigerianjobs, Jobsguru, MyJobMag
from services import analyze_resume, tailor_resume
import asyncio
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client
import io
import PyPDF2
import os
import base64
from fpdf import FPDF
from dotenv import load_dotenv
from typing import Optional
import json
import re

load_dotenv()






# --- CONFIG & INITIALIZATION ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") # Use Service Role for DB writes



# Diagnostic prints (Render will show these in the logs)
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") # Ensure this matches your Render name

print(f"DEBUG: URL found: {url is not None}")
print(f"DEBUG: Key found: {key is not None}")
if key:
    print(f"DEBUG: Key starts with: {key}")

# Initialize ONE strong client for the backend
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

origins = [
    "https://hustlr-delta.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- UTILITY FUNCTIONS ---
def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        pdf_stream = io.BytesIO(file_bytes)
        reader = PyPDF2.PdfReader(pdf_stream)
        full_text = [page.extract_text() for page in reader.pages if page.extract_text()]
        return "\n".join(full_text).strip()
    except Exception as e:
        print(f"PDF Extraction Error: {e}")
        return ""

# --- MODELS ---
class JobSaveRequest(BaseModel):
    user_id: str
    job_data: dict

class DirectTailorRequest(BaseModel):
    user_id: str
    job_description: str
    job_title: str
    company: Optional[str]

# --- ENDPOINTS ---

@app.get("/health")
def status():
    return {"status": "awake"}

@app.get("/search")
async def search_jobs(query: str, location: str = "Nigeria"):
    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(None, linkedln, query, location),
        loop.run_in_executor(None, jobberman, query, location),
        loop.run_in_executor(None, hotnigerianjobs, query),
        loop.run_in_executor(None, Jobsguru, query),
        loop.run_in_executor(None, MyJobMag, query, location)
    ]
    results = await asyncio.gather(*tasks)
    all_jobs = [job for source in results if source for job in source]
    return {"count": len(all_jobs), "jobs": all_jobs}

@app.post("/analyze-resume")
async def handle_resume_upload(file: UploadFile = File(...), user_id: str = Form(...)):
    """Extracts text and SAVES it to Supabase for the user."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    try:
        file_bytes = await file.read()
        resume_text = extract_text_from_pdf(file_bytes)
        
        if not resume_text:
            raise HTTPException(status_code=422, detail="Empty PDF or image scan.")

        # Save to database
        supabase.table("resumes").upsert({
            "user_id": user_id,
            "content": resume_text,
            "name": "Extracted User",
            "role": "Data Scientist"
        }, on_conflict="user_id").execute()
        
        return {"status": "success", "extracted_length": len(resume_text)}
    except Exception as e:
        print(f"Upload Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tailor-live-job")
async def tailor_live_job(req: DirectTailorRequest):
    """The 'Instant' Tailor: Pulls Saved Resume + Uses Live Job Card Details."""
    try:
        # 1. Get Saved Resume
        user_res = supabase.table("resumes").select("content").eq("user_id", req.user_id).single().execute()
        
        if not user_res.data:
            return {"status": "error", "message": "No resume found. Upload one first."}

        # 2. AI Tailoring
        tailored_text = tailor_resume(user_res.data['content'], req.job_description)

        # 3. Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=10)
        safe_text = tailored_text.encode('ascii', 'ignore').decode('ascii')
        pdf.multi_cell(0, 5, txt=safe_text)

        # 4. Return as Base64

        pdf_output_str = pdf.output(dest='S')
        pdf_bytes = pdf_output_str.encode('latin-1')
        b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')

        return {
            "status": "success",
            "pdf_base64": b64_pdf,
            "filename": f"Tailored_Resume_{req.company.replace(' ', '_')}.pdf"
        }
    except Exception as e:
        print(f"Tailoring Error: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/jobs/save")
async def save_job(request: JobSaveRequest):
    try:
        data = {
            "user_id": request.user_id,
            **request.job_data # Spreads the job dict into the DB columns
        }
        supabase.table("saved_jobs").insert(data).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/bookmarks/{user_id}")
async def get_bookmarks(user_id: str):
    response = supabase.table("saved_jobs").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
    return response.data

@app.delete("/bookmarks/{job_id}")
async def delete_bookmark(job_id: str):
    supabase.table("saved_jobs").delete().eq("id", job_id).execute()
    return {"status": "success"}


class LabAnalysisRequest(BaseModel):
    user_id: str
    target_field: str
    resume_text: Optional[str] = None # For fresh uploads



def clean_ai_json(raw_string: str):
    # Remove markdown code blocks if the AI included them
    clean_str = re.sub(r"```json|```", "", raw_string).strip()
    return json.loads(clean_str)

@app.post("/ai-lab/analyze")
async def ai_lab_analyze(req: LabAnalysisRequest):
    try:
        # Use provided text or fetch from DB
        text_to_analyze = req.resume_text
        if not text_to_analyze:
            res = supabase.table("resumes").select("content").eq("user_id", req.user_id).single().execute()
            text_to_analyze = res.data['content']

        if not text_to_analyze or len(text_to_analyze.strip()) < 50:
            return {"status": "error", "message": "Resume content is too short or empty. Please upload a full PDF."}

        # Call your AI service with a prompt requesting JSON
        # Example output: {"score": 75, "missing_keywords": ["Airflow", "Spark"], "tips": ["..."]}
        report = analyze_resume(text_to_analyze, req.target_field)
        
        try:
            if isinstance(report, str):
                report = clean_ai_json(report)
            return {"status": "success", "report": report}
        except Exception as e:
            print(f"JSON Parse Error: {e}")
            return {"status": "error", "message": "AI returned invalid format"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
