"""
Job Caching System for Career Compass AI
Provides in-memory caching for job recommendations to improve performance
"""

import time
import hashlib
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import asyncio
from threading import Lock

class JobCache:
    """
    In-memory cache for job recommendations with TTL (Time To Live) support
    """
    
    def __init__(self, default_ttl_minutes: int = 30):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl_minutes * 60  # Convert to seconds
        self.lock = Lock()
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'evictions': 0
        }
    
    def _generate_cache_key(self, skills: List[str], experience: str, 
                          last_jobs: List[str], location: Optional[str] = None) -> str:
        """Generate a unique cache key based on user profile"""
        # Create a consistent string representation
        profile_data = {
            'skills': sorted([skill.lower().strip() for skill in skills]),
            'experience': experience.lower().strip(),
            'last_jobs': sorted([job.lower().strip() for job in last_jobs]),
            'location': location.lower().strip() if location else ''
        }
        
        # Create hash of the profile data
        profile_str = json.dumps(profile_data, sort_keys=True)
        return hashlib.md5(profile_str.encode()).hexdigest()
    
    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if a cache entry has expired"""
        return time.time() > cache_entry['expires_at']
    
    def _cleanup_expired(self):
        """Remove expired entries from cache"""
        current_time = time.time()
        expired_keys = [
            key for key, entry in self.cache.items() 
            if current_time > entry['expires_at']
        ]
        
        for key in expired_keys:
            del self.cache[key]
            self.stats['evictions'] += 1
    
    def get(self, skills: List[str], experience: str, 
            last_jobs: List[str], location: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached job recommendations
        Returns None if not found or expired
        """
        with self.lock:
            # Clean up expired entries first
            self._cleanup_expired()
            
            cache_key = self._generate_cache_key(skills, experience, last_jobs, location)
            
            if cache_key in self.cache:
                entry = self.cache[cache_key]
                if not self._is_expired(entry):
                    self.stats['hits'] += 1
                    print(f"🎯 CACHE HIT: Found {len(entry['jobs'])} cached jobs for profile")
                    return entry['jobs']
                else:
                    # Remove expired entry
                    del self.cache[cache_key]
                    self.stats['evictions'] += 1
            
            self.stats['misses'] += 1
            print(f"❌ CACHE MISS: No cached jobs found for profile")
            return None
    
    def set(self, skills: List[str], experience: str, last_jobs: List[str], 
            jobs: List[Dict[str, Any]], location: Optional[str] = None, 
            ttl_minutes: Optional[int] = None) -> None:
        """
        Cache job recommendations with TTL
        """
        with self.lock:
            cache_key = self._generate_cache_key(skills, experience, last_jobs, location)
            ttl_seconds = (ttl_minutes or (self.default_ttl // 60)) * 60
            
            entry = {
                'jobs': jobs,
                'cached_at': time.time(),
                'expires_at': time.time() + ttl_seconds,
                'profile_hash': cache_key
            }
            
            self.cache[cache_key] = entry
            self.stats['sets'] += 1
            
            print(f"💾 CACHED: Stored {len(jobs)} jobs for profile (TTL: {ttl_seconds//60} minutes)")
    
    def invalidate(self, skills: List[str], experience: str, 
                   last_jobs: List[str], location: Optional[str] = None) -> bool:
        """
        Invalidate cached jobs for a specific profile
        Returns True if entry was found and removed
        """
        with self.lock:
            cache_key = self._generate_cache_key(skills, experience, last_jobs, location)
            
            if cache_key in self.cache:
                del self.cache[cache_key]
                print(f"🗑️  INVALIDATED: Removed cached jobs for profile")
                return True
            
            return False
    
    def clear_all(self) -> None:
        """Clear all cached entries"""
        with self.lock:
            cleared_count = len(self.cache)
            self.cache.clear()
            print(f"🧹 CLEARED: Removed {cleared_count} cached job entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'total_entries': len(self.cache),
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'hit_rate_percent': round(hit_rate, 2),
                'sets': self.stats['sets'],
                'evictions': self.stats['evictions'],
                'cache_size_mb': self._get_cache_size_mb()
            }
    
    def _get_cache_size_mb(self) -> float:
        """Estimate cache size in MB"""
        try:
            cache_str = json.dumps(self.cache)
            size_bytes = len(cache_str.encode('utf-8'))
            return round(size_bytes / (1024 * 1024), 2)
        except:
            return 0.0

class UserSessionCache:
    """
    Per-user session cache for job recommendations
    Tracks user-specific caching with session management
    """
    
    def __init__(self, session_ttl_hours: int = 8):
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
        self.session_ttl = session_ttl_hours * 3600  # Convert to seconds
        self.lock = Lock()
    
    def _is_session_expired(self, session_data: Dict[str, Any]) -> bool:
        """Check if user session has expired"""
        return time.time() > session_data.get('expires_at', 0)
    
    def _cleanup_expired_sessions(self):
        """Remove expired user sessions"""
        current_time = time.time()
        expired_users = [
            user_id for user_id, session in self.user_sessions.items()
            if current_time > session.get('expires_at', 0)
        ]
        
        for user_id in expired_users:
            del self.user_sessions[user_id]
    
    def get_user_jobs(self, user_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get cached jobs for a specific user"""
        with self.lock:
            self._cleanup_expired_sessions()
            
            if user_id in self.user_sessions:
                session = self.user_sessions[user_id]
                if not self._is_session_expired(session):
                    jobs = session.get('jobs', [])
                    print(f"👤 USER CACHE HIT: Found {len(jobs)} cached jobs for user {user_id}")
                    return jobs
                else:
                    del self.user_sessions[user_id]
            
            print(f"👤 USER CACHE MISS: No cached jobs for user {user_id}")
            return None
    
    def set_user_jobs(self, user_id: str, jobs: List[Dict[str, Any]], 
                      profile_data: Dict[str, Any]) -> None:
        """Cache jobs for a specific user with their profile"""
        with self.lock:
            session_data = {
                'jobs': jobs,
                'profile': profile_data,
                'cached_at': time.time(),
                'expires_at': time.time() + self.session_ttl,
                'refresh_count': self.user_sessions.get(user_id, {}).get('refresh_count', 0)
            }
            
            self.user_sessions[user_id] = session_data
            print(f"👤 USER CACHED: Stored {len(jobs)} jobs for user {user_id} (TTL: {self.session_ttl//3600} hours)")
    
    def invalidate_user(self, user_id: str) -> bool:
        """Invalidate cached jobs for a specific user"""
        with self.lock:
            if user_id in self.user_sessions:
                del self.user_sessions[user_id]
                print(f"👤 USER INVALIDATED: Removed cached jobs for user {user_id}")
                return True
            return False
    
    def refresh_user_jobs(self, user_id: str) -> None:
        """Mark user jobs for refresh (invalidate cache)"""
        with self.lock:
            if user_id in self.user_sessions:
                self.user_sessions[user_id]['refresh_count'] += 1
                del self.user_sessions[user_id]
                print(f"🔄 USER REFRESH: Invalidated cache for user {user_id}")

# Global cache instances
job_cache = JobCache(default_ttl_minutes=30)  # 30 minutes default TTL
user_session_cache = UserSessionCache(session_ttl_hours=8)  # 8 hours session TTL

def get_cached_jobs(skills: List[str], experience: str, last_jobs: List[str], 
                   location: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
    """Convenience function to get cached jobs"""
    return job_cache.get(skills, experience, last_jobs, location)

def cache_jobs(skills: List[str], experience: str, last_jobs: List[str], 
               jobs: List[Dict[str, Any]], location: Optional[str] = None, 
               ttl_minutes: int = 30) -> None:
    """Convenience function to cache jobs"""
    job_cache.set(skills, experience, last_jobs, jobs, location, ttl_minutes)

def get_user_cached_jobs(user_id: str) -> Optional[List[Dict[str, Any]]]:
    """Convenience function to get user-specific cached jobs"""
    return user_session_cache.get_user_jobs(user_id)

def cache_user_jobs(user_id: str, jobs: List[Dict[str, Any]], 
                   profile_data: Dict[str, Any]) -> None:
    """Convenience function to cache user-specific jobs"""
    user_session_cache.set_user_jobs(user_id, jobs, profile_data)

def invalidate_user_cache(user_id: str) -> bool:
    """Convenience function to invalidate user cache"""
    return user_session_cache.invalidate_user(user_id)

def refresh_user_cache(user_id: str) -> None:
    """Convenience function to refresh user cache"""
    user_session_cache.refresh_user_jobs(user_id)

def get_cache_stats() -> Dict[str, Any]:
    """Get comprehensive cache statistics"""
    job_stats = job_cache.get_stats()
    
    return {
        'job_cache': job_stats,
        'user_sessions': {
            'active_users': len(user_session_cache.user_sessions),
            'total_cached_jobs': sum(
                len(session.get('jobs', [])) 
                for session in user_session_cache.user_sessions.values()
            )
        },
        'performance_impact': {
            'api_calls_saved': job_stats['hits'],
            'estimated_time_saved_seconds': job_stats['hits'] * 3  # Assume 3 seconds per API call
        }
    } 