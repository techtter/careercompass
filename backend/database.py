import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import json
from datetime import datetime

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_KEY")

# To get your SUPABASE_URL and SUPABASE_ANON_KEY, go to your Supabase project's
# API settings: Project Settings -> API -> Project API keys

if not url or not key:
    raise ValueError("Supabase URL and Key must be set in environment variables")

supabase: Client = create_client(url, key)

class CVRecordService:
    """Service for managing CV records in Supabase"""
    
    @staticmethod
    def create_cv_record(
        user_id: str,
        filename: str,
        file_content: bytes,
        file_type: str,
        raw_text: str,
        parsed_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new CV record in Supabase"""
        try:
            # Convert file content to base64 for storage
            import base64
            file_content_b64 = base64.b64encode(file_content).decode('utf-8')
            
            cv_data = {
                "user_id": user_id,
                "filename": filename,
                "file_content": file_content_b64,
                "file_type": file_type,
                "raw_text": raw_text,
                "name": parsed_data.get("name"),
                "email": parsed_data.get("email"),
                "phone": parsed_data.get("phone"),
                "location": parsed_data.get("location"),
                "experience": parsed_data.get("experience"),
                "skills": json.dumps(parsed_data.get("skills", [])),
                "education": parsed_data.get("education"),
                "last_two_jobs": json.dumps(parsed_data.get("lastTwoJobs", [])),
                "summary": parsed_data.get("summary"),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = supabase.table("cv_records").insert(cv_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating CV record: {e}")
            return None
    
    @staticmethod
    def get_cv_record_by_user(user_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest CV record for a user"""
        try:
            result = supabase.table("cv_records").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(1).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting CV record: {e}")
            return None
    
    @staticmethod
    def get_cv_record_by_id(cv_id: int) -> Optional[Dict[str, Any]]:
        """Get a CV record by ID"""
        try:
            result = supabase.table("cv_records").select("*").eq("id", cv_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error getting CV record: {e}")
            return None
    
    @staticmethod
    def update_cv_record(cv_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a CV record"""
        try:
            updates["updated_at"] = datetime.utcnow().isoformat()
            result = supabase.table("cv_records").update(updates).eq("id", cv_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error updating CV record: {e}")
            return None

class CareerPathService:
    """Service for managing career path records"""
    
    @staticmethod
    def create_career_path(
        cv_record_id: int,
        user_id: str,
        job_title: str,
        experience_level: str,
        career_path_data: str
    ) -> Dict[str, Any]:
        """Create a new career path record"""
        try:
            data = {
                "cv_record_id": cv_record_id,
                "user_id": user_id,
                "job_title": job_title,
                "experience_level": experience_level,
                "career_path_data": career_path_data,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = supabase.table("career_paths").insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating career path: {e}")
            return None
    
    @staticmethod
    def get_career_paths_by_user(user_id: str):
        """Get career paths for a user"""
        try:
            result = supabase.table("career_paths").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            return result.data
        except Exception as e:
            print(f"Error getting career paths: {e}")
            return []

class SkillGapService:
    """Service for managing skill gap analysis records"""
    
    @staticmethod
    def create_skill_gap(
        cv_record_id: int,
        user_id: str,
        job_description: str,
        analysis_data: str
    ) -> Dict[str, Any]:
        """Create a new skill gap analysis record"""
        try:
            data = {
                "cv_record_id": cv_record_id,
                "user_id": user_id,
                "job_description": job_description,
                "analysis_data": analysis_data,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = supabase.table("skill_gaps").insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating skill gap analysis: {e}")
            return None
    
    @staticmethod
    def get_skill_gaps_by_user(user_id: str):
        """Get skill gap analyses for a user"""
        try:
            result = supabase.table("skill_gaps").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            return result.data
        except Exception as e:
            print(f"Error getting skill gaps: {e}")
            return []

class ResumeOptimizationService:
    """Service for managing resume optimization records"""
    
    @staticmethod
    def create_resume_optimization(
        cv_record_id: int,
        user_id: str,
        job_description: str,
        optimization_data: str
    ) -> Dict[str, Any]:
        """Create a new resume optimization record"""
        try:
            data = {
                "cv_record_id": cv_record_id,
                "user_id": user_id,
                "job_description": job_description,
                "optimization_data": optimization_data,
                "created_at": datetime.utcnow().isoformat()
            }
            
            result = supabase.table("resume_optimizations").insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating resume optimization: {e}")
            return None
    
    @staticmethod
    def get_resume_optimizations_by_user(user_id: str):
        """Get resume optimizations for a user"""
        try:
            result = supabase.table("resume_optimizations").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
            return result.data
        except Exception as e:
            print(f"Error getting resume optimizations: {e}")
            return [] 