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
    ResumeOptimizationService, LearningProgressService as LearningGoalService, database_available
)
import base64
from job_cache import (
    get_cache_stats, invalidate_user_cache, refresh_user_cache,
    get_user_cached_jobs, cache_user_jobs
)

# Import job services for job recommendations
try:
    from job_services import get_personalized_job_recommendations
    job_services_available = True
except ImportError as e:
    print(f"⚠️  Job services not available: {e}")
    job_services_available = False

# Load environment variables from .env file (preferred) or config.env as fallback
load_dotenv('.env')  # Try .env first
load_dotenv('config.env')  # Fallback to config.env

# Initialize Clerk if available
try:
    from clerk import Clerk
    clerk_available = True
except ImportError:
    print("⚠️  Clerk not available, authentication disabled for development")
    clerk_available = False

# Database services are already imported at the top, check if they're working
print(f"📦 Database available: {database_available}")
if database_available:
    print("✅ Using real database services with in-memory fallback")
else:
    print("⚠️  Database not configured, using in-memory storage only")

# Mock services for when database is not available  
if False:  # Disable empty services - always use real services
    print("📦 Using empty database services - no mock data")
    
    class EmptyService:
        @staticmethod
        def create_cv_record(*args, **kwargs):
            return None
        
        @staticmethod
        def get_cv_record_by_user(user_id):
            # Return None - no mock data
            print(f"🔍 DEBUG: EmptyService.get_cv_record_by_user called with user_id: {user_id}")
            print(f"🔍 DEBUG: No CV record found - user needs to upload CV")
            return None
        
        @staticmethod
        def get_cv_record_by_id(cv_id):
            return None
        
        @staticmethod
        def update_cv_record(user_id, update_data):
            return None
        
        @staticmethod
        def create_career_path(*args, **kwargs):
            return None
        
        @staticmethod
        def create_skill_gap(*args, **kwargs):
            return None
        
        @staticmethod
        def create_resume_optimization(*args, **kwargs):
            return None
        
        @staticmethod
        def create_learning_goal(*args, **kwargs):
            return None
        
        @staticmethod
        def get_career_paths_by_user(user_id):
            return []
        
        @staticmethod
        def get_skill_gaps_by_user(user_id):
            return []
        
        @staticmethod
        def get_resume_optimizations_by_user(user_id):
            return []
        
        @staticmethod
        def get_learning_goals_by_user(user_id):
            return []
    
    # Use empty services - no mock data
    CVRecordService = EmptyService
    CareerPathService = EmptyService
    SkillGapService = EmptyService
    ResumeOptimizationService = EmptyService
    LearningGoalService = EmptyService

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

class UserProfileUpdateRequest(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    experienceYears: Optional[int] = None
    skills: Optional[List[str]] = None
    lastThreeJobTitles: Optional[List[str]] = None
    experienceSummary: Optional[str] = None
    companies: Optional[List[str]] = None
    education: Optional[List[str]] = None
    certifications: Optional[List[str]] = None
    raw_text: Optional[str] = None  # For saving the actual CV content

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
        
        # Enhanced location extraction and validation
        location = parsed_data.get("location", "")
        print(f"🌍 DEBUG: Location from parsed data: '{location}'")
        
        # If no location found in parsed data, try to extract from raw text
        if not location:
            print(f"🌍 DEBUG: No location in parsed data, extracting from raw text...")
            try:
                from ai_services import _extract_country_from_work_history
                companies = parsed_data.get("companies", [])
                job_titles = parsed_data.get("lastThreeJobTitles", [])
                location = _extract_country_from_work_history(request.raw_text, companies, job_titles)
                print(f"🌍 DEBUG: Extracted location from raw text: '{location}'")
                
                # Update parsed_data with extracted location
                if location:
                    parsed_data["location"] = location
            except Exception as e:
                print(f"🌍 DEBUG: Error extracting location: {e}")
        
        print(f"🌍 DEBUG: Final location to save: '{location}'")
        
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
            "location": location,  # Use the processed location
            "experienceYears": parsed_data.get("experienceYears"),
            "skills": json.dumps(parsed_data.get("skills", [])),
            "lastThreeJobTitles": json.dumps(parsed_data.get("lastThreeJobTitles", [])),
            "experienceSummary": parsed_data.get("experienceSummary"),
            "companies": json.dumps(parsed_data.get("companies", [])),
            "education": json.dumps(parsed_data.get("education", [])),
            "certifications": json.dumps(parsed_data.get("certifications", []))
        }
        
        print(f"🌍 DEBUG: Saving CV data with location: '{cv_data.get('location')}'")
        
        cv_record = CVRecordService.create_cv_record(cv_data)
        
        if cv_record:
            print(f"✅ DEBUG: CV saved successfully with location: '{cv_record.get('location')}'")
            return {
                "success": True, 
                "cv_record_id": cv_record["id"], 
                "message": "Profile saved successfully",
                "debug_info": {
                    "saved_location": cv_record.get("location"),
                    "extracted_location": location
                }
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to save profile")
    except Exception as e:
        print(f"❌ Error saving CV: {e}")
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
        print(f"🔍 DEBUG: Getting user profile for user {user_id}")
        cv_record = CVRecordService.get_cv_record_by_user(user_id)
        
        if not cv_record:
            print(f"🔍 DEBUG: No CV record found for user {user_id}")
            return {
                "user_exists": False,
                "message": "User not found. Please upload your CV to get started."
            }
        
        print(f"🔍 DEBUG: CV record found: {cv_record}")
        
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
        
        # Extract location with enhanced debugging
        location = cv_record.get("location", "")
        print(f"🌍 DEBUG: Raw location from database: '{location}'")
        
        # If no location in database, try to extract from raw text
        if not location:
            raw_text = cv_record.get("raw_text", "")
            if raw_text:
                print(f"🌍 DEBUG: No location in database, trying to extract from raw text...")
                try:
                    from ai_services import _extract_country_from_work_history
                    location = _extract_country_from_work_history(raw_text, companies, last_three_job_titles)
                    print(f"🌍 DEBUG: Extracted location from raw text: '{location}'")
                    
                    # Save the extracted location back to the database
                    if location:
                        update_data = {"location": location}
                        CVRecordService.update_cv_record(user_id, update_data)
                        print(f"🌍 DEBUG: Saved extracted location '{location}' to database")
                except Exception as e:
                    print(f"🌍 DEBUG: Error extracting location from raw text: {e}")
        
        print(f"🌍 DEBUG: Final location for job search: '{location}'")
        
        # Create user profile from CV record with new simplified structure
        user_profile = {
            "firstName": cv_record.get("firstName"),
            "lastName": cv_record.get("lastName"),
            "email": cv_record.get("email"),
            "phone": cv_record.get("phone"),
            "location": location,  # Use the processed location
            "experienceYears": cv_record.get("experienceYears"),
            "skills": skills,
            "lastThreeJobTitles": last_three_job_titles,
            "experienceSummary": cv_record.get("experienceSummary"),
            "companies": companies,
            "education": education,
            "certifications": certifications
        }
        
        # Get personalized job recommendations with enhanced location targeting
        job_recommendations = []
        try:
            from job_services import get_personalized_job_recommendations
            # Convert experience years to string format for job service
            experience_str = f"{user_profile['experienceYears']} years" if user_profile["experienceYears"] else "Entry level"
            
            print(f"🔍 DEBUG: Calling job recommendations with location: '{location}'")
            job_recommendations = await get_personalized_job_recommendations(
                skills=user_profile["skills"],
                experience=experience_str,
                last_two_jobs=user_profile["lastThreeJobTitles"][:2],  # Use first two job titles
                location=location  # Use the processed location
            )
            print(f"🔍 DEBUG: Got {len(job_recommendations)} job recommendations")
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
            "message": f"Welcome back, {full_name or 'User'}! Here are your latest job recommendations.",
            "debug_info": {
                "location_from_db": cv_record.get("location", ""),
                "final_location": location,
                "job_count": len(job_recommendations)
            }
        }
        
    except Exception as e:
        print(f"Error getting user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/user-profile/{user_id}")
async def update_user_profile(user_id: str, request: UserProfileUpdateRequest):
    """Update comprehensive user profile information including all CV details"""
    try:
        # Check if user exists
        existing_cv = CVRecordService.get_cv_record_by_user(user_id)
        if not existing_cv:
            raise HTTPException(status_code=404, detail="User profile not found")
        
        # Prepare update data - only include fields that are provided
        update_data = {}
        
        # Basic profile fields
        if request.firstName is not None:
            update_data["firstName"] = request.firstName
        if request.lastName is not None:
            update_data["lastName"] = request.lastName
        if request.email is not None:
            update_data["email"] = request.email
        if request.phone is not None:
            update_data["phone"] = request.phone
        if request.location is not None:
            update_data["location"] = request.location
        if request.experienceYears is not None:
            update_data["experienceYears"] = request.experienceYears
        if request.experienceSummary is not None:
            update_data["experienceSummary"] = request.experienceSummary
        
        # Array fields - convert to JSON strings for database storage
        if request.skills is not None:
            update_data["skills"] = json.dumps(request.skills)
        if request.lastThreeJobTitles is not None:
            update_data["lastThreeJobTitles"] = json.dumps(request.lastThreeJobTitles)
        if request.companies is not None:
            update_data["companies"] = json.dumps(request.companies)
        if request.education is not None:
            update_data["education"] = json.dumps(request.education)
        if request.certifications is not None:
            update_data["certifications"] = json.dumps(request.certifications)
        
        # CV content
        if request.raw_text is not None:
            update_data["raw_text"] = request.raw_text
        
        # Update the CV record with new profile information
        updated_cv = CVRecordService.update_cv_record(user_id, update_data)
        
        if not updated_cv:
            raise HTTPException(status_code=500, detail="Failed to update user profile")
        
        return {
            "success": True,
            "message": "Complete profile saved successfully! All details have been updated in the database.",
            "updated_fields": list(update_data.keys()),
            "profile_data": {
                "firstName": request.firstName,
                "lastName": request.lastName,
                "email": request.email,
                "phone": request.phone,
                "location": request.location,
                "experienceYears": request.experienceYears,
                "skills": request.skills,
                "lastThreeJobTitles": request.lastThreeJobTitles,
                "experienceSummary": request.experienceSummary,
                "companies": request.companies,
                "education": request.education,
                "certifications": request.certifications
            }
        }
        
    except Exception as e:
        print(f"Error updating user profile: {e}")
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
        if not job_services_available:
            print("❌ Job services not available - returning empty results")
            return {
                "success": True,
                "jobs": [],
                "total": 0,
                "message": "Job services not available. Please configure API keys to enable real job search."
            }

        # Get REAL job recommendations using multiple job APIs with caching - NO MOCK DATA
        job_recommendations = await get_personalized_job_recommendations(
            skills=request.skills,
            experience=request.experience,
            last_two_jobs=request.lastTwoJobs,
            location=request.location,
            user_id=None,  # No user ID for direct requests
            use_cache=True
        )

        if job_recommendations:
            return {
                "success": True,
                "jobs": job_recommendations,
                "total": len(job_recommendations),
                "message": f"Found {len(job_recommendations)} real job recommendations"
            }
        else:
            return {
                "success": True,
                "jobs": [],
                "total": 0,
                "message": "No real jobs found for your profile. Please try different search criteria or configure additional API keys."
            }
    except Exception as e:
        print(f"Error getting job recommendations: {e}")
        return {
            "success": True,
            "jobs": [],
            "total": 0,
            "message": f"Error fetching jobs: {str(e)}"
        }

@app.get("/api/job-recommendations/{user_id}")
async def get_user_job_recommendations(user_id: str):
    """Get personalized job recommendations based on user's saved profile data from database"""
    try:
        print(f"🔍 DEBUG: Starting job recommendations for user {user_id}")
        
        # Get user's CV record from database
        print(f"🔍 DEBUG: Calling CVRecordService.get_cv_record_by_user({user_id})")
        cv_record = CVRecordService.get_cv_record_by_user(user_id)
        print(f"🔍 DEBUG: CV record result: {cv_record}")
        
        if not cv_record:
            print(f"🔍 DEBUG: No CV record found for user {user_id}")
            return {
                "success": False,
                "jobs": [],
                "total": 0,
                "message": "User profile not found. Please upload your CV first to get personalized job recommendations.",
                "user_location": None,
                "user_country": None,
                "profile_source": "none",
                "error": "no_profile"
            }
        
        print(f"🔍 DEBUG: Processing CV record data...")
        
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
        
        # Extract user profile data from database
        experience_years = cv_record.get("experienceYears", 0)
        experience_str = f"{experience_years} years" if experience_years else "Entry level"
        location = cv_record.get("location")  # This is the key - use saved location from database
        
        print(f"🔍 Generating job recommendations from DATABASE profile for user {user_id}:")
        print(f"   Skills: {skills}")
        print(f"   Experience: {experience_str}")
        print(f"   Last jobs: {last_three_job_titles[:2]}")
        print(f"   Location: {location}")
        print(f"   Detected Country: {location}")
        
        print(f"🔍 DEBUG: Fetching REAL jobs for user profile...")
        
        # Get REAL job recommendations based on user's saved profile - NO MOCK DATA
        if not job_services_available:
            print("❌ Job services not available - returning empty results")
            return {
                "success": True,
                "jobs": [],
                "total": 0,
                "message": "Job services not available. Please configure API keys to enable real job search.",
                "user_location": location,
                "user_country": location,
                "profile_source": "database"
            }
        
        try:
            real_jobs = await get_personalized_job_recommendations(
                skills=skills,
                experience=experience_str,
                last_two_jobs=last_three_job_titles[:2],
                location=location,
                user_id=user_id,  # Pass user_id for user-specific caching
                use_cache=True
            )
            
            if real_jobs:
                print(f"✅ Found {len(real_jobs)} real jobs for user profile")
                return {
                    "success": True,
                    "jobs": real_jobs,
                    "total": len(real_jobs),
                    "message": f"Found {len(real_jobs)} real job recommendations from saved profile",
                    "user_location": location,
                    "user_country": location,
                    "profile_source": "database"
                }
            else:
                print("❌ No real jobs found for user profile")
                return {
                    "success": True,
                    "jobs": [],
                    "total": 0,
                    "message": "No real jobs found for your profile. Please try updating your skills or location, or configure additional API keys.",
                    "user_location": location,
                    "user_country": location,
                    "profile_source": "database"
                }
        except Exception as e:
            print(f"❌ Error fetching real jobs for user profile: {e}")
            return {
                "success": True,
                "jobs": [],
                "total": 0,
                "message": f"Error fetching jobs for your profile: {str(e)}",
                "user_location": location,
                "user_country": location,
                "profile_source": "database"
            }
        
    except Exception as e:
        print(f"🔍 DEBUG: General Exception: {e}")
        print(f"Error getting user job recommendations: {e}")
        return {
            "success": False,
            "jobs": [],
            "total": 0,
            "message": f"Error retrieving job recommendations: {str(e)}",
            "user_location": None,
            "user_country": None,
            "profile_source": "error",
            "error": "server_error"
        }

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

# Cache Management Endpoints
@app.get("/api/cache/stats")
async def get_cache_statistics():
    """Get comprehensive cache statistics for monitoring performance"""
    try:
        stats = get_cache_stats()
        return {
            "success": True,
            "cache_stats": stats,
            "message": "Cache statistics retrieved successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve cache statistics"
        }

@app.post("/api/cache/refresh/{user_id}")
async def refresh_user_job_cache(user_id: str):
    """Force refresh job cache for a specific user"""
    try:
        refresh_user_cache(user_id)
        return {
            "success": True,
            "message": f"Cache refreshed for user {user_id}. Next job request will fetch fresh data."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to refresh cache for user {user_id}"
        }

@app.delete("/api/cache/user/{user_id}")
async def invalidate_user_job_cache(user_id: str):
    """Invalidate job cache for a specific user"""
    try:
        invalidated = invalidate_user_cache(user_id)
        if invalidated:
            return {
                "success": True,
                "message": f"Cache invalidated for user {user_id}"
            }
        else:
            return {
                "success": True,
                "message": f"No cache found for user {user_id}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to invalidate cache for user {user_id}"
        }

@app.delete("/api/cache/clear-all")
async def clear_all_job_cache():
    """Clear all job cache entries (admin function)"""
    try:
        from job_cache import job_cache, user_session_cache
        job_cache.clear_all()
        user_session_cache.user_sessions.clear()
        return {
            "success": True,
            "message": "All job cache entries cleared successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to clear job cache"
        } 