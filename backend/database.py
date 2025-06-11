import os
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

# Load environment variables
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

# Global variable to track database availability
database_available = False
supabase = None

# Try to initialize Supabase connection
if url and key and url != "https://placeholder.supabase.co" and key != "placeholder_key_for_development" and key != "placeholder_key":
    try:
        from supabase import create_client, Client
        supabase: Client = create_client(url, key)
        # Test the connection
        try:
            supabase.table("test_connection").select("*").limit(1).execute()
            database_available = True
            print("✅ Database connected successfully")
        except Exception:
            print("⚠️  Database connection test failed, using fallback mode")
            database_available = False
    except Exception as e:
        print(f"⚠️  Database not available: {e}")
        database_available = False
else:
    print("⚠️  Database credentials not configured, using fallback mode")

# Mock data for when database is not available
MOCK_USER_DATA = {
    # Removed all mock user data - no dummy profiles will be shown
}

class CVRecordService:
    @staticmethod
    def create_cv_record(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not database_available:
            # Return mock success response
            user_id = data.get("user_id", "user_1")
            MOCK_USER_DATA[user_id] = {
                "id": len(MOCK_USER_DATA) + 1,
                **data,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            return MOCK_USER_DATA[user_id]
        
        try:
            result = supabase.table("cv_records").insert(data).execute()
            if result.data:
                return result.data[0]
        except Exception as e:
            print(f"Error creating CV record: {e}")
        return None

    @staticmethod
    def get_cv_record_by_user(user_id: str) -> Optional[Dict[str, Any]]:
        if not database_available:
            # Return mock data if available for this user
            return MOCK_USER_DATA.get(user_id)
        
        try:
            result = supabase.table("cv_records").select("*").eq("user_id", user_id).execute()
            if result.data:
                return result.data[0]
        except Exception as e:
            print(f"Error getting CV record: {e}")
        return None

    @staticmethod
    def get_cv_record_by_id(record_id: int) -> Optional[Dict[str, Any]]:
        if not database_available:
            # Find mock data by ID
            for user_data in MOCK_USER_DATA.values():
                if user_data.get("id") == record_id:
                    return user_data
            return None
        
        try:
            result = supabase.table("cv_records").select("*").eq("id", record_id).execute()
            if result.data:
                return result.data[0]
        except Exception as e:
            print(f"Error getting CV record by ID: {e}")
        return None

    @staticmethod
    def update_cv_record(record_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not database_available:
            # Update mock data
            for user_id, user_data in MOCK_USER_DATA.items():
                if user_data.get("id") == record_id:
                    MOCK_USER_DATA[user_id].update(data)
                    MOCK_USER_DATA[user_id]["updated_at"] = datetime.now().isoformat()
                    return MOCK_USER_DATA[user_id]
            return None
        
        try:
            data["updated_at"] = datetime.now().isoformat()
            result = supabase.table("cv_records").update(data).eq("id", record_id).execute()
            if result.data:
                return result.data[0]
        except Exception as e:
            print(f"Error updating CV record: {e}")
        return None

    @staticmethod
    def get_all_cv_records_by_user(user_id: str) -> List[Dict[str, Any]]:
        if not database_available:
            user_data = MOCK_USER_DATA.get(user_id)
            return [user_data] if user_data else []
        
        try:
            result = supabase.table("cv_records").select("*").eq("user_id", user_id).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting all CV records: {e}")
            return []

class CareerPathService:
    @staticmethod
    def create_career_path(cv_record_id: int, user_id: str, job_title: str, experience_level: str, career_path_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not database_available:
            return {"id": 1, "cv_record_id": cv_record_id, "user_id": user_id, "job_title": job_title}
        
        try:
            data = {
                "cv_record_id": cv_record_id,
                "user_id": user_id,
                "job_title": job_title,
                "experience_level": experience_level,
                "career_path_data": json.dumps(career_path_data),
                "created_at": datetime.now().isoformat()
            }
            result = supabase.table("career_paths").insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating career path: {e}")
            return None

    @staticmethod
    def get_career_paths_by_user(user_id: str) -> List[Dict[str, Any]]:
        if not database_available:
            return []
        
        try:
            result = supabase.table("career_paths").select("*").eq("user_id", user_id).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting career paths: {e}")
            return []

class SkillGapService:
    @staticmethod
    def create_skill_gap(cv_record_id: int, user_id: str, job_description: str, analysis_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not database_available:
            return {"id": 1, "cv_record_id": cv_record_id, "user_id": user_id}
        
        try:
            data = {
                "cv_record_id": cv_record_id,
                "user_id": user_id,
                "job_description": job_description,
                "analysis_data": json.dumps(analysis_data),
                "created_at": datetime.now().isoformat()
            }
            result = supabase.table("skill_gaps").insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating skill gap: {e}")
            return None

    @staticmethod
    def get_skill_gaps_by_user(user_id: str) -> List[Dict[str, Any]]:
        if not database_available:
            return []
        
        try:
            result = supabase.table("skill_gaps").select("*").eq("user_id", user_id).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting skill gaps: {e}")
            return []

class ResumeOptimizationService:
    @staticmethod
    def create_resume_optimization(cv_record_id: int, user_id: str, job_description: str, optimization_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not database_available:
            return {"id": 1, "cv_record_id": cv_record_id, "user_id": user_id}
        
        try:
            data = {
                "cv_record_id": cv_record_id,
                "user_id": user_id,
                "job_description": job_description,
                "optimization_data": json.dumps(optimization_data),
                "created_at": datetime.now().isoformat()
            }
            result = supabase.table("resume_optimizations").insert(data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Error creating resume optimization: {e}")
            return None

    @staticmethod
    def get_resume_optimizations_by_user(user_id: str) -> List[Dict[str, Any]]:
        if not database_available:
            return []
        
        try:
            result = supabase.table("resume_optimizations").select("*").eq("user_id", user_id).execute()
            return result.data if result.data else []
        except Exception as e:
            print(f"Error getting resume optimizations: {e}")
            return [] 