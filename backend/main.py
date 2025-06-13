from fastapi import FastAPI, Depends, HTTPException, Request, Header, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from ai_services import generate_career_path, analyze_skill_gap, optimize_resume, parse_resume_content
import asyncio
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pdfplumber
import docx
import io
import json
from dotenv import load_dotenv
from database import (
    CVRecordService, CareerPathService, SkillGapService, 
    ResumeOptimizationService, LearningProgressService, database_available
)
import base64

# Load environment variables from .env file
load_dotenv()

# Initialize Clerk if available
try:
    from clerk import Clerk
    clerk_available = True
except ImportError:
    print("⚠️  Clerk not available, authentication disabled for development")
    clerk_available = False

# Mock services for when database is not available  
if not database_available:
    print("📦 Using mock database services for development")
    
    class MockService:
        @staticmethod
        def create_cv_record(*args, **kwargs):
            return {"id": 1, "user_id": "mock_user"}
        
        @staticmethod
        def get_cv_record_by_user(*args, **kwargs):
            return None  # Will trigger new user flow
        
        @staticmethod
        def create_career_path(*args, **kwargs):
            return {"id": 1}
        
        @staticmethod
        def create_skill_gap(*args, **kwargs):
            return {"id": 1}
        
        @staticmethod
        def create_resume_optimization(*args, **kwargs):
            return {"id": 1}

app = FastAPI(
    title="CareerCompassAI API",
    description="AI-powered career guidance and resume optimization platform",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    user_id: str
    cv_record_id: Optional[str] = None
    job_title: str
    experience: str
    skills: List[str]

class SkillGapRequest(BaseModel):
    user_id: str
    cv_record_id: Optional[str] = None
    skills: List[str]
    job_description: str
    target_role: Optional[str] = None

class ResumeOptimizationRequest(BaseModel):
    user_id: str
    cv_record_id: Optional[str] = None
    resume_text: str
    job_description: str

class ResumeParseRequest(BaseModel):
    resume_text: str

class SaveCVRequest(BaseModel):
    user_id: str
    filename: str
    file_type: str
    raw_text: str
    parsed_data: Dict[str, Any]

class JobRecommendationRequest(BaseModel):
    skills: List[str]
    experience: str
    lastTwoJobs: List[str]
    location: Optional[str] = None

class LearningGoalRequest(BaseModel):
    user_id: str
    skill_gap_id: Optional[str] = None
    skill_name: str
    learning_resource_type: str  # course, certification, book, video, etc.
    learning_resource_name: str
    learning_resource_url: Optional[str] = None
    target_completion_date: Optional[str] = None
    priority: str = "medium"  # high, medium, low

class LearningProgressUpdateRequest(BaseModel):
    goal_id: str
    progress_percentage: int  # 0-100
    status: str  # not_started, in_progress, completed, paused
    notes: Optional[str] = None

async def extract_text_from_file(file: UploadFile) -> str:
    """Extract text from uploaded file based on file type - optimized for Claude AI parsing"""
    try:
        if file.content_type == 'application/pdf':
            # Extract text from PDF using pdfplumber (better than PyPDF2)
            file_content = await file.read()
            pdf_content = io.BytesIO(file_content)
            text = ""
            with pdfplumber.open(pdf_content) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        
        elif file.content_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']:
            # Extract text from DOCX
            file_content = await file.read()
            doc_content = io.BytesIO(file_content)
            doc = docx.Document(doc_content)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        
        elif file.content_type == 'text/plain':
            # Extract text from TXT
            content = await file.read()
            return content.decode('utf-8')
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text from file: {str(e)}")

# Temporarily disabled authentication for development
# async def get_clerk_user(token: str = Depends(oauth2_scheme)) -> dict:
#     return {"id": "test-user"}

@app.get("/")
def read_root():
    return {"message": "Career Compass AI Backend", "status": "running"}

@app.post("/api/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    try:
        # Read file content for storage
        file_content = await file.read()
        
        # Reset file pointer for text extraction
        await file.seek(0)
        
        # Extract text from the uploaded file
        resume_text = await extract_text_from_file(file)
        
        if not resume_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the uploaded file")
        
        # Parse the resume using AI
        parsed_data = parse_resume_content(resume_text=resume_text)
        
        return {
            "parsed_data": parsed_data,
            "file_info": {
                "filename": file.filename,
                "file_type": file.content_type,
                "raw_text": resume_text,
                "file_size": len(file_content)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/save-cv")
async def save_cv(request: SaveCVRequest):
    try:
        # For now, we'll create a dummy file content since we don't have the actual file bytes
        # In a real implementation, you'd pass the file content from the frontend
        file_content = request.raw_text.encode('utf-8')
        
        # Parse the parsed_data if it's a JSON string
        parsed_data = request.parsed_data
        if isinstance(parsed_data, str):
            parsed_data = json.loads(parsed_data)
        
        # Prepare data dictionary for CVRecordService with new simplified structure
        cv_data = {
            "user_id": request.user_id,
            "filename": request.filename,
            "file_content": file_content,
            "file_type": request.file_type,
            "raw_text": request.raw_text,
            "firstName": parsed_data.get("firstName"),
            "lastName": parsed_data.get("lastName"),
            "email": parsed_data.get("email"), 
            "phone": parsed_data.get("phone"),
            "location": parsed_data.get("location"),
            "experienceYears": parsed_data.get("experienceYears"),
            "skills": json.dumps(parsed_data.get("skills", [])),
            "lastThreeJobTitles": json.dumps(parsed_data.get("lastThreeJobTitles", [])),
            "experienceSummary": parsed_data.get("experienceSummary"),
            "companies": json.dumps(parsed_data.get("companies", [])),
            "education": json.dumps(parsed_data.get("education", [])),
            "certifications": json.dumps(parsed_data.get("certifications", []))
        }
        
        cv_record = CVRecordService.create_cv_record(cv_data)
        
        if cv_record:
            return {"success": True, "cv_record_id": cv_record["id"], "message": "Profile saved successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to save profile")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cv-records/{user_id}")
async def get_user_cv_records(user_id: str):
    try:
        cv_record = CVRecordService.get_cv_record_by_user(user_id)
        if cv_record:
            # Parse JSON fields
            if cv_record.get("skills"):
                cv_record["skills"] = json.loads(cv_record["skills"])
            if cv_record.get("last_two_jobs"):
                cv_record["last_two_jobs"] = json.loads(cv_record["last_two_jobs"])
            return cv_record
        else:
            return {"message": "No CV record found for this user"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user-profile/{user_id}")
async def get_user_profile_with_jobs(user_id: str):
    """Get user profile and personalized job recommendations if user exists"""
    try:
        cv_record = CVRecordService.get_cv_record_by_user(user_id)
        
        if not cv_record:
            return {
                "user_exists": False,
                "message": "User not found. Please upload your CV to get started."
            }
        
        # Parse JSON fields if they are strings (for real database data)
        skills = cv_record.get("skills", [])
        if isinstance(skills, str):
            try:
                skills = json.loads(skills)
            except:
                skills = []
        
        last_three_job_titles = cv_record.get("lastThreeJobTitles", [])
        if isinstance(last_three_job_titles, str):
            try:
                last_three_job_titles = json.loads(last_three_job_titles)
            except:
                last_three_job_titles = []
        
        companies = cv_record.get("companies", [])
        if isinstance(companies, str):
            try:
                companies = json.loads(companies)
            except:
                companies = []
        
        education = cv_record.get("education", [])
        if isinstance(education, str):
            try:
                education = json.loads(education)
            except:
                education = []
        
        certifications = cv_record.get("certifications", [])
        if isinstance(certifications, str):
            try:
                certifications = json.loads(certifications)
            except:
                certifications = []
        
        # Create user profile from CV record with new simplified structure
        user_profile = {
            "firstName": cv_record.get("firstName"),
            "lastName": cv_record.get("lastName"),
            "email": cv_record.get("email"),
            "phone": cv_record.get("phone"),
            "location": cv_record.get("location"),
            "experienceYears": cv_record.get("experienceYears"),
            "skills": skills,
            "lastThreeJobTitles": last_three_job_titles,
            "experienceSummary": cv_record.get("experienceSummary"),
            "companies": companies,
            "education": education,
            "certifications": certifications
        }
        
        # Get personalized job recommendations
        job_recommendations = []
        try:
            from job_services import get_personalized_job_recommendations
            # Convert experience years to string format for job service
            experience_str = f"{user_profile['experienceYears']} years" if user_profile["experienceYears"] else "Entry level"
            job_recommendations = await get_personalized_job_recommendations(
                skills=user_profile["skills"],
                experience=experience_str,
                last_two_jobs=user_profile["lastThreeJobTitles"][:2],  # Use first two job titles
                location=user_profile.get("location")  # Use location from CV if available
            )
        except Exception as job_error:
            print(f"Error getting job recommendations: {job_error}")
            # Continue without jobs if job service fails
        
        full_name = f"{user_profile['firstName'] or ''} {user_profile['lastName'] or ''}".strip()
        return {
            "user_exists": True,
            "user_profile": user_profile,
            "cv_record_id": cv_record.get("id"),
            "cv_raw_text": cv_record.get("raw_text", ""),
            "cv_filename": cv_record.get("filename", "CV"),
            "job_recommendations": job_recommendations,
            "last_updated": cv_record.get("updated_at"),
            "message": f"Welcome back, {full_name or 'User'}! Here are your latest job recommendations."
        }
        
    except Exception as e:
        print(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/update-cv/{user_id}")
async def update_user_cv(user_id: str, file: UploadFile = File(...)):
    """Update user's existing CV with a new file"""
    try:
        # Check if user exists
        existing_cv = CVRecordService.get_cv_record_by_user(user_id)
        if not existing_cv:
            raise HTTPException(status_code=404, detail="User CV record not found")
        
        # Read file content for storage
        file_content = await file.read()
        
        # Reset file pointer for text extraction
        file.file.seek(0)
        
        # Extract text from the uploaded file
        resume_text = await extract_text_from_file(file)
        
        if not resume_text.strip():
            raise HTTPException(status_code=400, detail="Could not extract text from the uploaded file")
        
        # Parse the new resume using AI
        parsed_data = parse_resume_content(resume_text=resume_text)
        
        # Update the existing CV record
        file_content_b64 = None
        try:
            file_content_b64 = base64.b64encode(file_content).decode('utf-8')
        except Exception:
            pass  # Continue without base64 encoding if it fails
        
        # Ensure parsed_data is a dictionary
        if isinstance(parsed_data, str):
            try:
                parsed_data = json.loads(parsed_data)
            except:
                parsed_data = {}
        
        update_data = {
            "filename": file.filename,
            "file_content": file_content_b64,
            "file_type": file.content_type,
            "raw_text": resume_text,
            "firstName": parsed_data.get("firstName"),
            "lastName": parsed_data.get("lastName"),
            "email": parsed_data.get("email"),
            "phone": parsed_data.get("phone"),
            "location": parsed_data.get("location"),
            "experienceYears": parsed_data.get("experienceYears"),
            "skills": json.dumps(parsed_data.get("skills", [])),
            "lastThreeJobTitles": json.dumps(parsed_data.get("lastThreeJobTitles", [])),
            "experienceSummary": parsed_data.get("experienceSummary"),
            "companies": json.dumps(parsed_data.get("companies", [])),
            "education": json.dumps(parsed_data.get("education", [])),
            "certifications": json.dumps(parsed_data.get("certifications", []))
        }
        
        updated_cv = CVRecordService.update_cv_record(user_id, update_data)
        
        if not updated_cv:
            raise HTTPException(status_code=500, detail="Failed to update CV")
        
        return {
            "success": True,
            "message": "CV updated successfully",
            "parsed_data": parsed_data,
            "cv_record_id": updated_cv["id"],
            "file_info": {
                "filename": file.filename,
                "file_type": file.content_type,
                "raw_text": resume_text,
                "file_size": len(file_content)
            }
        }
        
    except Exception as e:
        print(f"Error updating CV: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-career-path")
async def get_career_path(request: CareerPathRequest):
    try:
        # Get CV data if cv_record_id is provided, otherwise use current data
        if request.cv_record_id:
            cv_record = CVRecordService.get_cv_record_by_id(request.cv_record_id)
            if cv_record:
                # Use skills from CV record
                skills_from_cv = json.loads(cv_record.get("skills", "[]"))
                skills_to_use = skills_from_cv if skills_from_cv else request.skills
            else:
                skills_to_use = request.skills
        else:
            skills_to_use = request.skills
        
        career_path = generate_career_path(
            job_title=request.job_title,
            experience=request.experience,
            skills=skills_to_use
        )
        
        # Save career path to database
        if request.cv_record_id:
            CareerPathService.create_career_path({
                "cv_record_id": request.cv_record_id,
                "user_id": request.user_id,
                "job_title": request.job_title,
                "experience_level": request.experience,
                "career_path_data": career_path
            })
        
        return {"career_path": career_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/skill-gap-analysis")
async def get_skill_gap_analysis(request: SkillGapRequest):
    try:
        # Get CV data if cv_record_id is provided, otherwise use current data
        if request.cv_record_id:
            cv_record = CVRecordService.get_cv_record_by_id(request.cv_record_id)
            if cv_record:
                # Use skills from CV record
                skills_from_cv = json.loads(cv_record.get("skills", "[]"))
                skills_to_use = skills_from_cv if skills_from_cv else request.skills
            else:
                skills_to_use = request.skills
        else:
            skills_to_use = request.skills
        
        analysis = analyze_skill_gap(
            skills=skills_to_use,
            job_description=request.job_description,
            target_role=request.target_role
        )
        
        # Save skill gap analysis to database
        if request.cv_record_id:
            SkillGapService.create_skill_gap({
                "cv_record_id": request.cv_record_id,
                "user_id": request.user_id,
                "job_description": request.job_description,
                "analysis_data": analysis
            })
        
        return {"analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/optimize-resume")
async def get_resume_optimization(request: ResumeOptimizationRequest):
    try:
        # Get CV data if cv_record_id is provided, otherwise use current data
        resume_text_to_use = request.resume_text
        if request.cv_record_id:
            cv_record = CVRecordService.get_cv_record_by_id(request.cv_record_id)
            if cv_record:
                # Use raw text from CV record if available
                resume_text_to_use = cv_record.get("raw_text", request.resume_text)
        
        optimization = optimize_resume(
            resume_text=resume_text_to_use,
            job_description=request.job_description
        )
        
        # Save resume optimization to database
        if request.cv_record_id:
            ResumeOptimizationService.create_resume_optimization({
                "cv_record_id": request.cv_record_id,
                "user_id": request.user_id,
                "job_description": request.job_description,
                "optimization_data": optimization
            })
        
        return {"optimization": optimization}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/career-paths/{user_id}")
async def get_user_career_paths(user_id: str):
    try:
        career_paths = CareerPathService.get_career_paths_by_user(user_id)
        return {"career_paths": career_paths}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/skill-gaps/{user_id}")
async def get_user_skill_gaps(user_id: str):
    try:
        skill_gaps = SkillGapService.get_skill_gaps_by_user(user_id)
        return {"skill_gaps": skill_gaps}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/resume-optimizations/{user_id}")
async def get_user_resume_optimizations(user_id: str):
    try:
        optimizations = ResumeOptimizationService.get_resume_optimizations_by_user(user_id)
        return {"resume_optimizations": optimizations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/job-recommendations")
async def get_job_recommendations(request: JobRecommendationRequest):
    try:
        from job_services import get_personalized_job_recommendations
        
        # Get job recommendations using AI and multiple job APIs
        job_recommendations = await get_personalized_job_recommendations(
            skills=request.skills,
            experience=request.experience,
            last_two_jobs=request.lastTwoJobs,
            location=request.location
        )
        
        return {
            "success": True,
            "jobs": job_recommendations,
            "total": len(job_recommendations),
            "message": f"Found {len(job_recommendations)} job recommendations"
        }
    except Exception as e:
        print(f"Error getting job recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/learning-goals")
async def create_learning_goal(request: LearningGoalRequest):
    """Create a new learning goal based on skill gap analysis"""
    try:
        goal_data = {
            "user_id": request.user_id,
            "skill_gap_id": request.skill_gap_id,
            "skill_name": request.skill_name,
            "learning_resource_type": request.learning_resource_type,
            "learning_resource_name": request.learning_resource_name,
            "learning_resource_url": request.learning_resource_url,
            "target_completion_date": request.target_completion_date,
            "priority": request.priority,
            "progress_percentage": 0,
            "status": "not_started"
        }
        
        learning_goal = LearningProgressService.create_learning_goal(goal_data)
        
        if learning_goal:
            return {"success": True, "learning_goal": learning_goal}
        else:
            raise HTTPException(status_code=500, detail="Failed to create learning goal")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/learning-goals/{goal_id}/progress")
async def update_learning_progress(goal_id: str, request: LearningProgressUpdateRequest):
    """Update progress for a learning goal"""
    try:
        progress_data = {
            "progress_percentage": request.progress_percentage,
            "status": request.status,
            "notes": request.notes
        }
        
        updated_goal = LearningProgressService.update_learning_progress(goal_id, progress_data)
        
        if updated_goal:
            return {"success": True, "learning_goal": updated_goal}
        else:
            raise HTTPException(status_code=404, detail="Learning goal not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/learning-goals/{user_id}")
async def get_user_learning_goals(user_id: str):
    """Get all learning goals for a user"""
    try:
        learning_goals = LearningProgressService.get_learning_goals_by_user(user_id)
        return {"learning_goals": learning_goals}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/learning-recommendations/{skill_gap_id}")
async def get_learning_recommendations(skill_gap_id: str):
    """Get learning recommendations based on skill gap analysis"""
    try:
        recommendations = LearningProgressService.get_learning_recommendations_by_skill_gap(skill_gap_id)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Webhook handler temporarily disabled for development 