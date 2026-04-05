import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase_client: Client = create_client(url, key)

def save_job_to_db(job_data):
    """Saves a single job listing to Supabase, avoiding duplicates via the link."""
    try:
        supabase_client.table("jobs").upsert(job_data, on_conflict="link").execute()
    except Exception as e:
        print(f"Error saving job: {e}")

def get_stored_jobs(role):
    """Fetches jobs from the cloud database instantly."""
    response = supabase_client.table("jobs").select("*").ilike("title", f"%{role}%").execute()
    return response.data