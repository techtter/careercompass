import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

# To get your SUPABASE_URL and SUPABASE_KEY, go to your Supabase project's
# API settings: Project Settings -> API -> Project API keys

if not url or not key:
    raise ValueError("Supabase URL and Key must be set in your .env file")

supabase: Client = create_client(url, key) 