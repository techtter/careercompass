from fastapi import FastAPI, Depends, HTTPException, Request, Header
from fastapi.security import OAuth2PasswordBearer
from clerk import Clerk
from clerk.client import ClerkClient
from .database import supabase
from .ai_services import generate_career_path, analyze_skill_gap, optimize_resume
import os
from svix.webhooks import Webhook, WebhookVerificationError
from pydantic import BaseModel
from typing import List, Dict, Any

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UserData(BaseModel):
    id: str
    email_addresses: List[Dict[str, Any]]
    first_name: str
    last_name: str

class WebhookEvent(BaseModel):
    data: UserData
    object: str
    type: str

class CareerPathRequest(BaseModel):
    job_title: str
    experience: str
    skills: List[str]

class SkillGapRequest(BaseModel):
    skills: List[str]
    job_description: str

class ResumeOptimizationRequest(BaseModel):
    resume_text: str
    job_description: str

async def get_clerk_user(token: str = Depends(oauth2_scheme)) -> dict:
    clerk_client = ClerkClient()
    try:
        decoded_token = clerk_client.tokens.verify_token(token)
        user = clerk_client.users.get_user(decoded_token["sub"])
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/users")
def get_users():
    response = supabase.table('users').select("*").execute()
    return response.data

@app.get("/me")
async def read_users_me(current_user: dict = Depends(get_clerk_user)):
    return current_user

@app.post("/api/generate-career-path")
async def get_career_path(request: CareerPathRequest, current_user: dict = Depends(get_clerk_user)):
    try:
        career_path = generate_career_path(
            job_title=request.job_title,
            experience=request.experience,
            skills=request.skills
        )
        return {"career_path": career_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/skill-gap-analysis")
async def get_skill_gap_analysis(request: SkillGapRequest, current_user: dict = Depends(get_clerk_user)):
    try:
        analysis = analyze_skill_gap(
            skills=request.skills,
            job_description=request.job_description
        )
        return {"analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/optimize-resume")
async def get_resume_optimization(request: ResumeOptimizationRequest, current_user: dict = Depends(get_clerk_user)):
    try:
        optimization = optimize_resume(
            resume_text=request.resume_text,
            job_description=request.job_description
        )
        return {"optimization": optimization}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/webhooks/clerk")
async def clerk_webhook(request: Request, svix_id: str = Header(None), svix_timestamp: str = Header(None), svix_signature: str = Header(None)):
    payload = await request.body()
    secret = os.environ.get("CLERK_WEBHOOK_SECRET")
    
    if not secret:
        raise HTTPException(status_code=500, detail="CLERK_WEBHOOK_SECRET not configured")

    try:
        wh = Webhook(secret)
        event = wh.verify(payload, {"svix-id": svix_id, "svix-timestamp": svix_timestamp, "svix-signature": svix_signature})
    except WebhookVerificationError as e:
        raise HTTPException(status_code=400, detail="Webhook verification failed")

    event_data = WebhookEvent(**event)

    if event_data.type == 'user.created':
        user_data = event_data.data
        try:
            supabase.table('users').insert({
                'clerk_id': user_data.id,
                'email': user_data.email_addresses[0]['email_address'],
                'first_name': user_data.first_name,
                'last_name': user_data.last_name,
            }).execute()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create user in database: {e}")

    return {"status": "success"} 