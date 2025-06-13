import os
from typing import Dict, Any, List, Optional
import json
from datetime import datetime

# Environment variables
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_ANON_KEY")

# Global variable to track database availability
database_available = False
supabase = None

# In-memory storage for development mode
MEMORY_STORE = {
    "cv_records": {},
    "career_paths": {},
    "skill_gaps": {},
    "resume_optimizations": {}
}

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
            print("⚠️  Database connection test failed, using in-memory storage")
            database_available = False
    except Exception as e:
        print(f"⚠️  Database not available: {e}, using in-memory storage")
        database_available = False
else:
    print("⚠️  Database credentials not configured, using in-memory storage for development")

class CVRecordService:
    @staticmethod
    def create_cv_record(cv_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if database_available:
            try:
                result = supabase.table("cv_records").insert(cv_data).execute()
                return result.data[0] if result.data else None
            except Exception as e:
                print(f"Database error, falling back to memory: {e}")
                return CVRecordService._create_cv_record_memory(cv_data)
        else:
            return CVRecordService._create_cv_record_memory(cv_data)
    
    @staticmethod
    def _create_cv_record_memory(cv_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = cv_data["user_id"]
        record_id = f"cv_{len(MEMORY_STORE['cv_records']) + 1}"
        
        record = {
            "id": record_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            **cv_data
        }
        
        MEMORY_STORE["cv_records"][user_id] = record
        return record
    
    @staticmethod
    def get_cv_record_by_user(user_id: str) -> Optional[Dict[str, Any]]:
        if database_available:
            try:
                result = supabase.table("cv_records").select("*").eq("user_id", user_id).execute()
                return result.data[0] if result.data else None
            except Exception as e:
                print(f"Database error, falling back to memory: {e}")
                return MEMORY_STORE["cv_records"].get(user_id)
        else:
            return MEMORY_STORE["cv_records"].get(user_id)
    
    @staticmethod
    def get_cv_record_by_id(record_id: str) -> Optional[Dict[str, Any]]:
        if database_available:
            try:
                result = supabase.table("cv_records").select("*").eq("id", record_id).execute()
                return result.data[0] if result.data else None
            except Exception as e:
                print(f"Database error, falling back to memory: {e}")
                # Search in memory store by ID
                for user_id, record in MEMORY_STORE["cv_records"].items():
                    if record.get("id") == record_id:
                        return record
                return None
        else:
            # Search in memory store by ID
            for user_id, record in MEMORY_STORE["cv_records"].items():
                if record.get("id") == record_id:
                    return record
            return None
    
    @staticmethod
    def update_cv_record(user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if database_available:
            try:
                result = supabase.table("cv_records").update(update_data).eq("user_id", user_id).execute()
                return result.data[0] if result.data else None
            except Exception as e:
                print(f"Database error, falling back to memory: {e}")
                return CVRecordService._update_cv_record_memory(user_id, update_data)
        else:
            return CVRecordService._update_cv_record_memory(user_id, update_data)
    
    @staticmethod
    def _update_cv_record_memory(user_id: str, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if user_id in MEMORY_STORE["cv_records"]:
            MEMORY_STORE["cv_records"][user_id].update(update_data)
            MEMORY_STORE["cv_records"][user_id]["updated_at"] = datetime.now().isoformat()
            return MEMORY_STORE["cv_records"][user_id]
        return None

class CareerPathService:
    @staticmethod
    def create_career_path(path_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if database_available:
            try:
                result = supabase.table("career_paths").insert(path_data).execute()
                return result.data[0] if result.data else None
            except Exception as e:
                print(f"Database error, falling back to memory: {e}")
                return CareerPathService._create_career_path_memory(path_data)
        else:
            return CareerPathService._create_career_path_memory(path_data)
    
    @staticmethod
    def _create_career_path_memory(path_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = path_data["user_id"]
        record_id = f"career_{len(MEMORY_STORE['career_paths']) + 1}"
        
        record = {
            "id": record_id,
            "created_at": datetime.now().isoformat(),
            **path_data
        }
        
        if user_id not in MEMORY_STORE["career_paths"]:
            MEMORY_STORE["career_paths"][user_id] = []
        MEMORY_STORE["career_paths"][user_id].append(record)
        return record
    
    @staticmethod
    def get_career_paths_by_user(user_id: str) -> List[Dict[str, Any]]:
        if database_available:
            try:
                result = supabase.table("career_paths").select("*").eq("user_id", user_id).execute()
                return result.data if result.data else []
            except Exception as e:
                print(f"Database error, falling back to memory: {e}")
                return MEMORY_STORE["career_paths"].get(user_id, [])
        else:
            return MEMORY_STORE["career_paths"].get(user_id, [])

class SkillGapService:
    @staticmethod
    def create_skill_gap(gap_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if database_available:
            try:
                result = supabase.table("skill_gaps").insert(gap_data).execute()
                return result.data[0] if result.data else None
            except Exception as e:
                print(f"Database error, falling back to memory: {e}")
                return SkillGapService._create_skill_gap_memory(gap_data)
        else:
            return SkillGapService._create_skill_gap_memory(gap_data)
    
    @staticmethod
    def _create_skill_gap_memory(gap_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = gap_data["user_id"]
        record_id = f"skill_gap_{len(MEMORY_STORE['skill_gaps']) + 1}"
        
        record = {
            "id": record_id,
            "created_at": datetime.now().isoformat(),
            **gap_data
        }
        
        if user_id not in MEMORY_STORE["skill_gaps"]:
            MEMORY_STORE["skill_gaps"][user_id] = []
        MEMORY_STORE["skill_gaps"][user_id].append(record)
        return record
    
    @staticmethod
    def get_skill_gaps_by_user(user_id: str) -> List[Dict[str, Any]]:
        if database_available:
            try:
                result = supabase.table("skill_gaps").select("*").eq("user_id", user_id).execute()
                return result.data if result.data else []
            except Exception as e:
                print(f"Database error, falling back to memory: {e}")
                return MEMORY_STORE["skill_gaps"].get(user_id, [])
        else:
            return MEMORY_STORE["skill_gaps"].get(user_id, [])

class ResumeOptimizationService:
    @staticmethod
    def create_resume_optimization(optimization_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if database_available:
            try:
                result = supabase.table("resume_optimizations").insert(optimization_data).execute()
                return result.data[0] if result.data else None
            except Exception as e:
                print(f"Database error, falling back to memory: {e}")
                return ResumeOptimizationService._create_resume_optimization_memory(optimization_data)
        else:
            return ResumeOptimizationService._create_resume_optimization_memory(optimization_data)
    
    @staticmethod
    def _create_resume_optimization_memory(optimization_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = optimization_data["user_id"]
        record_id = f"resume_opt_{len(MEMORY_STORE['resume_optimizations']) + 1}"
        
        record = {
            "id": record_id,
            "created_at": datetime.now().isoformat(),
            **optimization_data
        }
        
        if user_id not in MEMORY_STORE["resume_optimizations"]:
            MEMORY_STORE["resume_optimizations"][user_id] = []
        MEMORY_STORE["resume_optimizations"][user_id].append(record)
        return record
    
    @staticmethod
    def get_resume_optimizations_by_user(user_id: str) -> List[Dict[str, Any]]:
        if database_available:
            try:
                result = supabase.table("resume_optimizations").select("*").eq("user_id", user_id).execute()
                return result.data if result.data else []
            except Exception as e:
                print(f"Database error, falling back to memory: {e}")
                return MEMORY_STORE["resume_optimizations"].get(user_id, [])
        else:
            return MEMORY_STORE["resume_optimizations"].get(user_id, [])

class LearningProgressService:
    """Service for tracking learning progress as per PRD section 4.3"""
    
    @staticmethod
    def create_learning_goal(goal_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new learning goal"""
        if database_available:
            try:
                result = supabase.table("learning_goals").insert(goal_data).execute()
                return result.data[0] if result.data else None
            except Exception as e:
                print(f"Database error, falling back to memory: {e}")
                return LearningProgressService._create_learning_goal_memory(goal_data)
        else:
            return LearningProgressService._create_learning_goal_memory(goal_data)
    
    @staticmethod
    def _create_learning_goal_memory(goal_data: Dict[str, Any]) -> Dict[str, Any]:
        user_id = goal_data["user_id"]
        record_id = f"learning_goal_{len(MEMORY_STORE.get('learning_goals', {})) + 1}"
        
        record = {
            "id": record_id,
            "created_at": datetime.now().isoformat(),
            **goal_data
        }
        
        if "learning_goals" not in MEMORY_STORE:
            MEMORY_STORE["learning_goals"] = {}
        if user_id not in MEMORY_STORE["learning_goals"]:
            MEMORY_STORE["learning_goals"][user_id] = []
        MEMORY_STORE["learning_goals"][user_id].append(record)
        return record
    
    @staticmethod
    def update_learning_progress(goal_id: str, progress_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update progress for a learning goal"""
        if database_available:
            try:
                result = supabase.table("learning_goals").update(progress_data).eq("id", goal_id).execute()
                return result.data[0] if result.data else None
            except Exception as e:
                print(f"Database error, falling back to memory: {e}")
                return LearningProgressService._update_learning_progress_memory(goal_id, progress_data)
        else:
            return LearningProgressService._update_learning_progress_memory(goal_id, progress_data)
    
    @staticmethod
    def _update_learning_progress_memory(goal_id: str, progress_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if "learning_goals" not in MEMORY_STORE:
            return None
        
        for user_id, goals in MEMORY_STORE["learning_goals"].items():
            for goal in goals:
                if goal["id"] == goal_id:
                    goal.update(progress_data)
                    goal["updated_at"] = datetime.now().isoformat()
                    return goal
        return None
    
    @staticmethod
    def get_learning_goals_by_user(user_id: str) -> List[Dict[str, Any]]:
        """Get all learning goals for a user"""
        if database_available:
            try:
                result = supabase.table("learning_goals").select("*").eq("user_id", user_id).execute()
                return result.data if result.data else []
            except Exception as e:
                print(f"Database error, falling back to memory: {e}")
                return MEMORY_STORE.get("learning_goals", {}).get(user_id, [])
        else:
            return MEMORY_STORE.get("learning_goals", {}).get(user_id, [])
    
    @staticmethod
    def get_learning_recommendations_by_skill_gap(skill_gap_id: str) -> List[Dict[str, Any]]:
        """Get learning recommendations based on skill gap analysis"""
        if database_available:
            try:
                result = supabase.table("learning_recommendations").select("*").eq("skill_gap_id", skill_gap_id).execute()
                return result.data if result.data else []
            except Exception as e:
                print(f"Database error, falling back to memory: {e}")
                return MEMORY_STORE.get("learning_recommendations", {}).get(skill_gap_id, [])
        else:
            return MEMORY_STORE.get("learning_recommendations", {}).get(skill_gap_id, [])
    
    @staticmethod
    def create_learning_recommendation(recommendation_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a learning recommendation from skill gap analysis"""
        if database_available:
            try:
                result = supabase.table("learning_recommendations").insert(recommendation_data).execute()
                return result.data[0] if result.data else None
            except Exception as e:
                print(f"Database error, falling back to memory: {e}")
                return LearningProgressService._create_learning_recommendation_memory(recommendation_data)
        else:
            return LearningProgressService._create_learning_recommendation_memory(recommendation_data)
    
    @staticmethod
    def _create_learning_recommendation_memory(recommendation_data: Dict[str, Any]) -> Dict[str, Any]:
        skill_gap_id = recommendation_data["skill_gap_id"]
        record_id = f"learning_rec_{len(MEMORY_STORE.get('learning_recommendations', {})) + 1}"
        
        record = {
            "id": record_id,
            "created_at": datetime.now().isoformat(),
            **recommendation_data
        }
        
        if "learning_recommendations" not in MEMORY_STORE:
            MEMORY_STORE["learning_recommendations"] = {}
        if skill_gap_id not in MEMORY_STORE["learning_recommendations"]:
            MEMORY_STORE["learning_recommendations"][skill_gap_id] = []
        MEMORY_STORE["learning_recommendations"][skill_gap_id].append(record)
        return record 