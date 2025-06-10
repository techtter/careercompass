import os
import clerk
from dotenv import load_dotenv

load_dotenv()

clerk.api_key = os.environ.get("CLERK_SECRET_KEY")

# To get your CLERK_SECRET_KEY, go to your Clerk dashboard's
# API Keys section and get the secret key.

if not clerk.api_key:
    raise ValueError("Clerk API Key must be set in your .env file") 