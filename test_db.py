import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
s = create_client(url, key)

print("Attempting to fetch 1 row...")
try:
    res = s.table("saved_jobs").select("*").limit(1).execute()
    print("Connection Successful:", res.data)
except Exception as e:
    print("Connection Failed:", e)