"""
Enhanced Job Services with Caching for Career Compass AI
Provides real job recommendations from multiple APIs with intelligent caching
"""

import asyncio
import json
import random
import os
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from job_api_services import JobAggregator, validate_job_posting, check_job_availability
from job_cache import (
    get_cached_jobs, cache_jobs, get_user_cached_jobs, cache_user_jobs,
    invalidate_user_cache, refresh_user_cache, get_cache_stats
)

# Import real job API services
try:
    REAL_APIS_AVAILABLE = True
    print("✅ Real job API services loaded successfully")
except ImportError as e:
    print(f"⚠️  Import error for job_api_services: {e}")
    REAL_APIS_AVAILABLE = False
except Exception as e:
    print(f"⚠️  Unexpected error loading job_api_services: {e}")
    REAL_APIS_AVAILABLE = False

# Force enable real APIs for testing
print(f"🔧 REAL_APIS_AVAILABLE status: {REAL_APIS_AVAILABLE}")

# Override to always try real APIs first
USE_REAL_JOBS = os.getenv('USE_REAL_JOBS', 'true').lower() == 'true'
print(f"🔧 USE_REAL_JOBS environment variable: {USE_REAL_JOBS}")

if USE_REAL_JOBS:
    print("🚀 Real job APIs are ENABLED - will fetch from external APIs")
else:
    print("⚠️  Real job APIs are DISABLED - will return empty results")

def _extract_country_from_location(location: str) -> str:
    """
    Extract country from location string with enhanced Netherlands detection.
    Prioritizes Netherlands and European countries for better job matching.
    """
    if not location:
        return ""
    
    location_lower = location.lower().strip()
    
    # Enhanced country mapping with Netherlands priority
    country_mapping = {
        # Netherlands variations (highest priority)
        'netherlands': 'Netherlands',
        'holland': 'Netherlands', 
        'nl': 'Netherlands',
        'nederland': 'Netherlands',
        'dutch': 'Netherlands',
        
        # Netherlands cities
        'amsterdam': 'Netherlands', 'rotterdam': 'Netherlands', 'utrecht': 'Netherlands', 'the hague': 'Netherlands', 'eindhoven': 'Netherlands',
        'groningen': 'Netherlands', 'tilburg': 'Netherlands', 'almere': 'Netherlands', 'breda': 'Netherlands', 'nijmegen': 'Netherlands',
        'apeldoorn': 'Netherlands', 'haarlem': 'Netherlands', 'arnhem': 'Netherlands', 'zaanstad': 'Netherlands', 'haarlemmermeer': 'Netherlands',
        
        # Other European countries
        'germany': 'Germany', 'deutschland': 'Germany', 'de': 'Germany',
        'berlin': 'Germany', 'munich': 'Germany', 'hamburg': 'Germany', 'cologne': 'Germany', 'frankfurt': 'Germany',
        
        'united kingdom': 'United Kingdom', 'uk': 'United Kingdom', 'britain': 'United Kingdom', 'england': 'United Kingdom',
        'london': 'United Kingdom', 'manchester': 'United Kingdom', 'birmingham': 'United Kingdom',
        
        'france': 'France', 'french': 'France', 'fr': 'France',
        'paris': 'France', 'lyon': 'France', 'marseille': 'France',
        
        'belgium': 'Belgium', 'brussels': 'Belgium', 'antwerp': 'Belgium',
        'switzerland': 'Switzerland', 'zurich': 'Switzerland', 'geneva': 'Switzerland',
        'austria': 'Austria', 'vienna': 'Austria',
        'sweden': 'Sweden', 'stockholm': 'Sweden',
        'norway': 'Norway', 'oslo': 'Norway',
        'denmark': 'Denmark', 'copenhagen': 'Denmark',
        'finland': 'Finland', 'helsinki': 'Finland',
        'italy': 'Italy', 'rome': 'Italy', 'milan': 'Italy',
        'spain': 'Spain', 'madrid': 'Spain', 'barcelona': 'Spain',
        
        # North America
        'united states': 'United States', 'usa': 'United States', 'us': 'United States', 'america': 'United States',
        'canada': 'Canada',
        
        # Other regions
        'australia': 'Australia', 'singapore': 'Singapore', 'india': 'India', 'japan': 'Japan', 'china': 'China'
    }
    
    # Enhanced regex patterns for Netherlands detection
    netherlands_patterns = [
        r'\bnetherlands\b|\bholland\b|\bnl\b|\bdutch\b',
        r'\bamsterdam\b|\brotterdam\b|\butrecht\b|\bthe hague\b|\beindhoven\b',
        r'\bgroningen\b|\btilburg\b|\balmere\b|\bbreda\b|\bnijmegen\b'
    ]
    
    # Check for Netherlands patterns first (priority)
    for pattern in netherlands_patterns:
        if re.search(pattern, location_lower):
            print(f"🇳🇱 Netherlands detected from location: '{location}' -> pattern: {pattern}")
            return 'Netherlands'
    
    # Check other country mappings
    for location_key, country in country_mapping.items():
        if location_key in location_lower:
            print(f"🌍 Country detected from location: '{location}' -> '{location_key}' -> {country}")
            return country
    
    # Check for common location patterns (City, Country)
    if ',' in location:
        parts = [part.strip() for part in location.split(',')]
        if len(parts) >= 2:
            country_part = parts[-1].lower()  # Last part is usually country
            for location_key, country in country_mapping.items():
                if location_key == country_part:
                    print(f"🌍 Country detected from location part: '{country_part}' -> {country}")
                    return country
    
    print(f"🌍 No country detected from location: '{location}'")
    return ""

def _prioritize_jobs_by_location(jobs: List[Dict[str, Any]], user_location: str, user_country: str) -> List[Dict[str, Any]]:
    """
    Prioritize jobs based on user's location and country.
    Netherlands users get Netherlands jobs first, then European jobs, then global jobs.
    """
    if not jobs:
        return jobs
    
    print(f"🎯 Prioritizing {len(jobs)} jobs for user location: {user_location}, country: {user_country}")
    
    # Categorize jobs by location priority
    netherlands_jobs = []
    european_jobs = []
    global_jobs = []
    
    # Enhanced Netherlands detection patterns
    netherlands_indicators = [
        # Country names
        'netherlands', 'holland', 'nederland', 'nl',
        # Major cities
        'amsterdam', 'rotterdam', 'utrecht', 'the hague', 'den haag', 'eindhoven', 
        'groningen', 'tilburg', 'almere', 'breda', 'nijmegen', 'apeldoorn', 
        'haarlem', 'arnhem', 'zaanstad', 'haarlemmermeer', 'veldhoven',
        # Dutch provinces
        'noord-holland', 'zuid-holland', 'noord-brabant', 'zuid-brabant',
        'gelderland', 'overijssel', 'limburg', 'friesland', 'drenthe',
        'flevoland', 'zeeland', 'utrecht', 'groningen'
    ]
    
    european_countries = {
        'Germany', 'United Kingdom', 'France', 'Belgium', 'Switzerland', 'Austria',
        'Sweden', 'Norway', 'Denmark', 'Finland', 'Italy', 'Spain', 'Portugal'
    }
    
    for job in jobs:
        job_location = job.get('location', '').lower()
        job_country = job.get('country', '').lower()
        
        # Enhanced Netherlands detection
        is_netherlands_job = False
        
        if user_country == 'Netherlands':
            # Check for Netherlands indicators in location or country
            for indicator in netherlands_indicators:
                if indicator in job_location or indicator in job_country:
                    is_netherlands_job = True
                    break
        
        if is_netherlands_job:
            netherlands_jobs.append(job)
            print(f"🇳🇱 Netherlands job: {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')} - {job.get('location', 'Unknown')}")
        
        # Check if job is in Europe (for Netherlands users)
        elif (user_country == 'Netherlands' and 
              any(country.lower() in job_location or country.lower() in job_country 
                  for country in european_countries)):
            european_jobs.append(job)
            print(f"🇪🇺 European job: {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')} - {job.get('location', 'Unknown')}")
        
        # Check if job matches user's country (for non-Netherlands users)
        elif (user_country and user_country != 'Netherlands' and
              (user_country.lower() in job_location or user_country.lower() in job_country)):
            netherlands_jobs.append(job)  # Use same priority as Netherlands jobs for user's country
            print(f"🏠 Local job for {user_country}: {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')} - {job.get('location', 'Unknown')}")
        
        else:
            global_jobs.append(job)
            print(f"🌍 Global job: {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')} - {job.get('location', 'Unknown')}")
    
    # Combine jobs with location priority
    prioritized_jobs = netherlands_jobs + european_jobs + global_jobs
    
    print(f"📊 Job prioritization results:")
    print(f"   🇳🇱 Netherlands/Local jobs: {len(netherlands_jobs)}")
    print(f"   🇪🇺 European jobs: {len(european_jobs)}")
    print(f"   🌍 Global jobs: {len(global_jobs)}")
    print(f"   📋 Total prioritized jobs: {len(prioritized_jobs)}")
    
    return prioritized_jobs

def _calculate_job_relevance_score(job: Dict[str, Any], user_skills: List[str], user_jobs: List[str], user_experience: str) -> int:
    """
    Calculate comprehensive job relevance score based on multiple factors.
    Returns score from 0-100.
    """
    score = 0
    
    # 1. Skills matching (40% weight)
    job_skills = job.get('required_skills', [])
    job_description = job.get('description', '').lower()
    
    if user_skills:
        skill_matches = 0
        for skill in user_skills:
            skill_lower = skill.lower()
            # Check exact skill matches
            if any(skill_lower in req_skill.lower() for req_skill in job_skills):
                skill_matches += 2  # Exact match gets 2 points
            # Check skill mentions in description
            elif skill_lower in job_description:
                skill_matches += 1  # Description mention gets 1 point
        
        skill_score = min(40, (skill_matches / len(user_skills)) * 40)
        score += skill_score
    
    # 2. Job title matching (30% weight)
    job_title = job.get('title', '').lower()
    title_score = 0
    
    if user_jobs:
        for user_job in user_jobs:
            if user_job:
                user_job_words = user_job.lower().split()
                job_title_words = job_title.split()
                
                # Check for exact title matches
                if user_job.lower() in job_title:
                    title_score += 15
                # Check for keyword matches
                else:
                    word_matches = sum(1 for word in user_job_words if word in job_title_words and len(word) > 2)
                    title_score += min(10, word_matches * 3)
        
        title_score = min(30, title_score)
        score += title_score
    
    # 3. Experience level matching (20% weight)
    job_level = job.get('experience_level', '').lower()
    experience_score = 0
    
    if user_experience:
        # Extract years from experience
        experience_years = 0
        experience_match = re.search(r'(\d+)', user_experience)
        if experience_match:
            experience_years = int(experience_match.group(1))
        
        # Map experience to levels
        if experience_years >= 10:
            user_level = ['senior', 'lead', 'principal', 'staff']
        elif experience_years >= 5:
            user_level = ['senior', 'mid', 'intermediate']
        elif experience_years >= 2:
            user_level = ['mid', 'intermediate', 'junior']
        else:
            user_level = ['junior', 'entry', 'graduate']
        
        if any(level in job_level for level in user_level):
            experience_score = 20
        elif 'senior' in job_level and experience_years >= 3:
            experience_score = 15
        elif 'junior' in job_level and experience_years <= 5:
            experience_score = 15
        else:
            experience_score = 10
    
    score += experience_score
    
    # 4. Company and role quality (10% weight)
    quality_indicators = ['senior', 'lead', 'principal', 'architect', 'manager', 'director']
    if any(indicator in job_title for indicator in quality_indicators):
        score += 5
    
    # Check for reputable company indicators
    company = job.get('company', '').lower()
    if any(indicator in company for indicator in ['tech', 'data', 'software', 'digital', 'innovation']):
        score += 5
    
    return min(100, int(score))

def _get_location_priority_score(job_location: str, job_country: str, user_country: str, is_remote: bool = False) -> int:
    """
    Calculate location priority score for job recommendations.
    Higher score = higher priority in results.
    ENHANCED to give maximum priority to user's exact country.
    
    Priority order (ENHANCED):
    1. User's exact country (120 points) - MAXIMUM PRIORITY
    2. Remote jobs (100 points) - Very high priority
    3. Same region/nearby countries (85-80 points)
    4. Tech hub countries (75-70 points)
    5. English-speaking countries (70 points)
    6. Other countries (60-50 points)
    """
    if not user_country:
        # If no user country, prioritize remote jobs and tech hubs
        if is_remote or 'remote' in job_location.lower():
            return 100
        # Prioritize major tech hubs when no user location
        tech_hubs = ['United States', 'United Kingdom', 'Germany', 'Netherlands', 'Canada', 'Singapore', 'Australia']
        if job_country in tech_hubs:
            return 75
        return 60
    
    # ENHANCED: User's exact country gets MAXIMUM priority (increased from 100 to 120)
    if job_country == user_country:
        print(f"🏠 EXACT COUNTRY MATCH: {job_country} = {user_country} - Priority Score: 120")
        return 120
    
    # Remote jobs get very high priority regardless of user location (increased from 95 to 100)
    if is_remote or 'remote' in job_location.lower():
        print(f"🌐 REMOTE JOB DETECTED - Priority Score: 100")
        return 100
    
    # Define country groups for proximity scoring
    european_countries = ['Germany', 'Austria', 'Switzerland', 'Netherlands', 'Belgium', 'United Kingdom', 'Sweden', 'Norway', 'Denmark', 'Finland', 'France', 'Spain', 'Italy', 'Ireland', 'Poland', 'Czech Republic', 'Portugal']
    english_speaking = ['United States', 'United Kingdom', 'Canada', 'Australia', 'Ireland', 'Singapore', 'New Zealand']
    tech_hubs = ['United States', 'United Kingdom', 'Germany', 'Netherlands', 'Canada', 'Singapore', 'UAE', 'Australia', 'Switzerland', 'Sweden', 'Denmark', 'Norway']
    
    # ENHANCED: Regional proximity scoring with higher scores
    if user_country in european_countries and job_country in european_countries:
        # Same European region gets high priority
        if user_country in ['Netherlands', 'Germany', 'Belgium'] and job_country in ['Netherlands', 'Germany', 'Belgium']:
            return 90  # DACH/Benelux region (increased from 85)
        elif user_country in ['Sweden', 'Norway', 'Denmark', 'Finland'] and job_country in ['Sweden', 'Norway', 'Denmark', 'Finland']:
            return 90  # Nordic region (increased from 85)
        else:
            return 85  # General European (increased from 80)
    
    # English-speaking country preference (enhanced)
    if user_country in english_speaking and job_country in english_speaking:
        return 85  # Increased from 80
    
    # Tech hub countries get medium-high priority
    if job_country in tech_hubs:
        return 75
    
    # English-speaking countries get preference for non-English speakers
    if job_country in english_speaking:
        return 70
    
    # European countries get preference for European users
    if user_country in european_countries and job_country in european_countries:
        return 70
    
    # All other countries get lower priority
    return 50

def _prioritize_jobs_by_relevance_and_location(jobs: List[Dict[str, Any]], user_skills: List[str], user_jobs: List[str], user_experience: str, user_country: str) -> List[Dict[str, Any]]:
    """
    Sort jobs by combined relevance and location priority.
    Enhanced prioritization algorithm that gives stronger weight to:
    1. User's location/country (highest priority)
    2. Current job title relevance 
    3. Experience level matching
    4. Skills matching
    """
    for job in jobs:
        # Calculate relevance score
        relevance_score = _calculate_job_relevance_score(job, user_skills, user_jobs, user_experience)
        job['relevance_score'] = relevance_score
        
        # Calculate location priority
        job_location = job.get('location', '')
        job_country = job.get('country', '')
        is_remote = job.get('remote', False) or 'remote' in job_location.lower()
        
        location_priority = _get_location_priority_score(job_location, job_country, user_country, is_remote)
        job['location_priority'] = location_priority
        
        # Enhanced job title matching score (separate from general relevance)
        job_title_score = _calculate_job_title_relevance(job.get('title', ''), user_jobs)
        job['job_title_score'] = job_title_score
        
        # Enhanced experience level matching score
        experience_match_score = _calculate_experience_match(job.get('experience_level', ''), user_experience)
        job['experience_match_score'] = experience_match_score
        
        # Enhanced skills matching score
        skills_match_score = _calculate_skills_match(job, user_skills)
        job['skills_match_score'] = skills_match_score
        
        # ENHANCED COMBINED SCORE CALCULATION with stronger location priority
        if user_country and job_country == user_country:
            # User's country jobs get MAXIMUM boost - these should appear first
            job['combined_score'] = (
                (location_priority * 0.5) +      # 50% weight for location (user country = 120 points)
                (job_title_score * 0.2) +        # 20% weight for job title relevance
                (skills_match_score * 0.2) +     # 20% weight for skills matching
                (experience_match_score * 0.1)   # 10% weight for experience matching
            ) + 40  # +40 bonus points for user's country (increased from +30)
            print(f"🎯 USER COUNTRY PRIORITY: {job['title']} at {job['company']} ({job_country}) - Score: {job['combined_score']:.1f}")
            
        elif is_remote:
            # Remote jobs get high priority but less than user's country
            job['combined_score'] = (
                (location_priority * 0.4) +      # 40% weight for location (remote = 100 points)
                (job_title_score * 0.25) +       # 25% weight for job title relevance
                (skills_match_score * 0.25) +    # 25% weight for skills matching
                (experience_match_score * 0.1)   # 10% weight for experience matching
            ) + 20  # +20 bonus for remote work (increased from +15)
            print(f"🌐 REMOTE JOB: {job['title']} at {job['company']} - Score: {job['combined_score']:.1f}")
            
        else:
            # Standard scoring for other countries
            job['combined_score'] = (
                (location_priority * 0.25) +     # 25% weight for location
                (job_title_score * 0.35) +       # 35% weight for job title relevance
                (skills_match_score * 0.25) +    # 25% weight for skills matching
                (experience_match_score * 0.15)  # 15% weight for experience matching
            )
            
        # Keep original match_score for backward compatibility
        job['match_score'] = relevance_score
    
    # ENHANCED SORTING: Primary sort by combined score, secondary sorts for tie-breaking
    jobs.sort(key=lambda x: (
        x.get('combined_score', 0),           # Primary: Combined score
        x.get('location_priority', 0),        # Secondary: Location priority
        x.get('job_title_score', 0),          # Tertiary: Job title relevance
        x.get('skills_match_score', 0),       # Quaternary: Skills matching
        x.get('experience_match_score', 0)    # Quinary: Experience matching
    ), reverse=True)
    
    # Enhanced debug logging for top jobs
    print(f"🔝 TOP 10 PRIORITIZED JOBS (Enhanced Algorithm):")
    for i, job in enumerate(jobs[:10]):
        country_flag = "🏠" if job.get('country') == user_country else "🌍"
        remote_flag = "🌐" if job.get('remote') or 'remote' in job.get('location', '').lower() else ""
        print(f"   {i+1}. {country_flag}{remote_flag} {job['title']} at {job['company']} ({job.get('country', 'Unknown')})")
        print(f"      📊 Combined: {job.get('combined_score', 0):.1f} | 📍 Location: {job.get('location_priority', 0)} | 💼 Title: {job.get('job_title_score', 0):.1f} | 🛠️ Skills: {job.get('skills_match_score', 0):.1f}")
    
    return jobs

def _calculate_job_title_relevance(job_title: str, user_jobs: List[str]) -> float:
    """
    Calculate ENHANCED job title relevance score with strong focus on role matching.
    Returns score from 0-100 based on how well the job title matches user's previous roles.
    PRIORITIZES exact role matches (Data Engineer, Data Architect, etc.)
    """
    if not user_jobs or not job_title:
        return 0.0
    
    job_title_lower = job_title.lower()
    total_score = 0.0
    
    # Define role-specific keywords with high weights
    data_engineering_keywords = ['data engineer', 'data engineering', 'data pipeline', 'etl', 'data architect', 'data architecture', 'big data', 'data platform']
    software_engineering_keywords = ['software engineer', 'software developer', 'backend engineer', 'frontend engineer', 'full stack', 'web developer']
    senior_keywords = ['senior', 'lead', 'principal', 'staff', 'architect', 'manager', 'director', 'head of']
    
    for user_job in user_jobs:
        if not user_job:
            continue
            
        user_job_clean = user_job.replace('❖', '').strip().lower()
        # Remove contact info and certifications
        user_job_clean = re.sub(r'\+?\d{1,3}[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}', '', user_job_clean)
        user_job_clean = re.sub(r'\S+@\S+', '', user_job_clean)
        user_job_clean = re.sub(r'certified|certification', '', user_job_clean).strip()
        
        if len(user_job_clean) < 3:
            continue
        
        # HIGHEST PRIORITY: Exact role type matching
        user_is_data_role = any(keyword in user_job_clean for keyword in data_engineering_keywords)
        job_is_data_role = any(keyword in job_title_lower for keyword in data_engineering_keywords)
        
        user_is_software_role = any(keyword in user_job_clean for keyword in software_engineering_keywords)
        job_is_software_role = any(keyword in job_title_lower for keyword in software_engineering_keywords)
        
        # Perfect role match gets maximum score
        if user_is_data_role and job_is_data_role:
            total_score += 80.0  # VERY HIGH score for data role match
            print(f"🎯 PERFECT DATA ROLE MATCH: {job_title} matches {user_job_clean}")
        elif user_is_software_role and job_is_software_role:
            total_score += 70.0  # High score for software role match
        elif user_is_data_role and job_is_software_role:
            total_score += 20.0  # Low score - role mismatch
        elif user_is_software_role and job_is_data_role:
            total_score += 25.0  # Slightly better - could transition
        
        # Exact title match (additional bonus)
        if user_job_clean in job_title_lower or job_title_lower in user_job_clean:
            total_score += 30.0
            continue
        
        # Word-by-word matching (reduced weight)
        user_words = [word for word in user_job_clean.split() if len(word) > 2]
        job_words = [word for word in job_title_lower.split() if len(word) > 2]
        
        word_matches = 0
        for user_word in user_words:
            for job_word in job_words:
                if user_word == job_word:
                    word_matches += 3  # Exact word match
                elif user_word in job_word or job_word in user_word:
                    word_matches += 1  # Partial word match
        
        if user_words:
            word_score = min(20.0, (word_matches / len(user_words)) * 20)  # Reduced from 40
            total_score += word_score
        
        # Seniority level matching
        user_is_senior = any(keyword in user_job_clean for keyword in senior_keywords)
        job_is_senior = any(keyword in job_title_lower for keyword in senior_keywords)
        
        if user_is_senior and job_is_senior:
            total_score += 15.0
        elif not user_is_senior and not job_is_senior:
            total_score += 5.0
    
    return min(100.0, total_score)

def _calculate_experience_match(job_experience_level: str, user_experience: str) -> float:
    """
    Calculate enhanced experience level matching score.
    Returns score from 0-100 based on how well the job's experience requirements match user's experience.
    """
    if not user_experience:
        return 50.0  # Neutral score if no user experience provided
    
    # Extract years from user experience
    experience_years = 0
    experience_match = re.search(r'(\d+)', user_experience)
    if experience_match:
        experience_years = int(experience_match.group(1))
    
    job_level_lower = job_experience_level.lower()
    
    # Define experience level mappings
    if experience_years >= 15:
        user_levels = ['principal', 'staff', 'director', 'vp', 'senior', 'lead']
        ideal_score = 100.0
    elif experience_years >= 10:
        user_levels = ['senior', 'lead', 'principal', 'staff']
        ideal_score = 95.0
    elif experience_years >= 7:
        user_levels = ['senior', 'lead', 'mid', 'intermediate']
        ideal_score = 90.0
    elif experience_years >= 5:
        user_levels = ['senior', 'mid', 'intermediate']
        ideal_score = 85.0
    elif experience_years >= 3:
        user_levels = ['mid', 'intermediate', 'senior']
        ideal_score = 80.0
    elif experience_years >= 1:
        user_levels = ['junior', 'mid', 'intermediate', 'entry']
        ideal_score = 75.0
    else:
        user_levels = ['entry', 'junior', 'graduate', 'intern']
        ideal_score = 70.0
    
    # Check for exact level matches
    for level in user_levels:
        if level in job_level_lower:
            return ideal_score
    
    # Partial matching logic
    if experience_years >= 8 and any(keyword in job_level_lower for keyword in ['senior', 'lead']):
        return 85.0
    elif experience_years >= 3 and any(keyword in job_level_lower for keyword in ['mid', 'intermediate']):
        return 80.0
    elif experience_years <= 2 and any(keyword in job_level_lower for keyword in ['junior', 'entry']):
        return 75.0
    
    # Default score for unclear or missing job level
    return 60.0

def _calculate_skills_match(job: Dict[str, Any], user_skills: List[str]) -> float:
    """
    Calculate ENHANCED skills matching score with focus on technical relevance.
    Returns score from 0-100 based on how well user's skills match job requirements.
    PRIORITIZES data engineering and architecture skills.
    """
    if not user_skills:
        return 0.0
    
    job_skills = job.get('required_skills', [])
    job_description = job.get('description', '').lower()
    job_title = job.get('title', '').lower()
    
    total_score = 0.0
    skill_matches = 0
    
    # Define skill categories with different weights
    data_engineering_skills = ['python', 'sql', 'spark', 'kafka', 'airflow', 'snowflake', 'aws', 'azure', 'gcp', 'etl', 'data pipeline', 'big data', 'hadoop', 'hive', 'cassandra', 'elasticsearch', 'mongodb', 'postgresql', 'mysql', 'redshift', 'databricks', 'dbt', 'terraform', 'docker', 'kubernetes']
    
    architecture_skills = ['microservices', 'system design', 'distributed systems', 'cloud architecture', 'solution architect', 'data architecture', 'api design', 'scalability', 'performance']
    
    programming_skills = ['java', 'scala', 'python', 'javascript', 'typescript', 'go', 'rust', 'c++']
    
    for skill in user_skills:
        skill_lower = skill.lower().strip()
        if len(skill_lower) < 2:
            continue
        
        skill_score = 0.0
        
        # Check for exact skill matches in required skills (highest priority)
        for req_skill in job_skills:
            if skill_lower in req_skill.lower() or req_skill.lower() in skill_lower:
                # Higher score for data engineering skills
                if any(de_skill in skill_lower for de_skill in data_engineering_skills):
                    skill_score = max(skill_score, 15.0)  # VERY HIGH for data skills
                elif any(arch_skill in skill_lower for arch_skill in architecture_skills):
                    skill_score = max(skill_score, 12.0)  # HIGH for architecture skills
                else:
                    skill_score = max(skill_score, 8.0)   # Standard for other skills
        
        # Check for skill mentions in job title (high priority)
        if skill_lower in job_title:
            if any(de_skill in skill_lower for de_skill in data_engineering_skills):
                skill_score = max(skill_score, 12.0)
            else:
                skill_score = max(skill_score, 6.0)
        
        # Check for skill mentions in job description (medium priority)
        if skill_lower in job_description:
            if any(de_skill in skill_lower for de_skill in data_engineering_skills):
                skill_score = max(skill_score, 8.0)
            else:
                skill_score = max(skill_score, 3.0)
        
        # Special bonus for critical data engineering skills
        critical_data_skills = ['python', 'sql', 'spark', 'kafka', 'aws', 'azure', 'airflow', 'snowflake']
        if any(critical_skill in skill_lower for critical_skill in critical_data_skills):
            skill_score *= 1.5  # 50% bonus for critical data skills
        
        total_score += skill_score
        if skill_score > 0:
            skill_matches += 1
    
    # Calculate final score with emphasis on skill relevance
    if user_skills:
        base_score = (total_score / len(user_skills)) * 8  # Scale to 0-100
        # Bonus for high percentage of skills matched
        match_percentage = skill_matches / len(user_skills)
        bonus = match_percentage * 30  # Up to 30 bonus points for high match percentage
        
        final_score = min(100.0, base_score + bonus)
        return final_score
    
    return 0.0

async def get_real_job_recommendations(
    skills: List[str], 
    experience: str, 
    last_two_jobs: List[str], 
    location: Optional[str] = None,
    use_cache: bool = True
) -> List[Dict[str, Any]]:
    """
    Get real job recommendations from multiple job APIs with caching
    """
    print("🌐 Starting real job API search with caching...")
    
    # Check cache first if enabled
    if use_cache:
        cached_jobs = get_cached_jobs(skills, experience, last_two_jobs, location)
        if cached_jobs:
            print(f"🎯 CACHE HIT: Returning {len(cached_jobs)} cached jobs")
            return cached_jobs
    
    print("🔍 CACHE MISS: Fetching fresh jobs from APIs...")
    
    # Always try RemoteOK API first (no API key required)
    remoteok_jobs = []
    try:
        print("📡 Trying RemoteOK API (no API key required)...")
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get("https://remoteok.io/api") as response:
                if response.status == 200:
                    data = await response.json()
                    # Parse RemoteOK jobs
                    for job_data in data[1:11]:  # Skip first item (metadata) and get 10 jobs
                        if isinstance(job_data, dict):
                            job = {
                                'id': job_data.get('id', f"remoteok_{len(remoteok_jobs)}"),
                                'title': job_data.get('position', 'Software Developer'),
                                'company': job_data.get('company', 'Remote Company'),
                                'location': 'Remote',
                                'country': 'Global',
                                'salary': job_data.get('salary', 'Competitive'),
                                'description': job_data.get('description', 'Remote job opportunity')[:500] + '...',
                                'required_skills': job_data.get('tags', [])[:5],
                                'experience_level': 'Mid-level',
                                'job_type': 'Full-time',
                                'remote': True,
                                'source': 'RemoteOK',
                                'postedDate': job_data.get('date', ''),
                                'daysAgo': 1,
                                'applyUrl': job_data.get('url', f"https://remoteok.io/remote-jobs/{job_data.get('id', 'job')}"),
                                'company_logo': job_data.get('logo', ''),
                                'match_score': 80,
                                'is_real_job': True
                            }
                            remoteok_jobs.append(job)
                    print(f"✅ Fetched {len(remoteok_jobs)} jobs from RemoteOK API")
                else:
                    print(f"❌ RemoteOK API returned status: {response.status}")
    except Exception as e:
        print(f"❌ Error fetching from RemoteOK API: {e}")

    # Try to use JobAggregator if available
    aggregator_jobs = []
    if REAL_APIS_AVAILABLE:
        try:
            print("📡 Trying JobAggregator (JSearch + Adzuna APIs)...")
            # Extract country for better API targeting
            user_country = _extract_country_from_location(location) if location else ""
            print(f"🌍 Detected Country: {user_country}")
            
            # Special handling for Netherlands
            if user_country and user_country.lower() == 'netherlands':
                print("🇳🇱 Netherlands location detected - Dutch job boards will be included in search!")
            
            # Create search queries based on user profile
            search_queries = []
            
            # Generate TARGETED queries from job titles
            for job_title in last_two_jobs:
                if job_title and len(job_title.strip()) > 2:
                    # Clean job title (remove certifications, contact info)
                    clean_title = job_title.replace('❖', '').strip()
                    # Remove phone numbers and emails
                    clean_title = re.sub(r'\+?\d{1,3}[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}', '', clean_title)
                    clean_title = re.sub(r'\S+@\S+', '', clean_title)
                    clean_title = re.sub(r'certified|certification', '', clean_title, flags=re.IGNORECASE)
                    clean_title = clean_title.strip()
                    
                    if clean_title and len(clean_title) > 5:
                        # Prioritize data engineering roles
                        if any(keyword in clean_title.lower() for keyword in ['data engineer', 'data architect', 'data platform', 'data pipeline']):
                            search_queries.insert(0, clean_title)  # Add to front for priority
                        else:
                            search_queries.append(clean_title)
            
            # Generate SPECIFIC queries from skills (focus on data technologies)
            data_skills = []
            for skill in skills[:10]:  # Top 10 skills
                skill_clean = skill.strip()
                if len(skill_clean) > 2 and not any(cert in skill_clean.lower() for cert in ['certified', 'certification']):
                    # Prioritize data engineering skills
                    if any(data_tech in skill_clean.lower() for data_tech in ['python', 'sql', 'spark', 'kafka', 'airflow', 'snowflake', 'aws', 'azure', 'data']):
                        data_skills.insert(0, skill_clean)
                    else:
                        data_skills.append(skill_clean)
            
            # Create targeted skill-based queries
            if data_skills:
                # Combine top data skills for targeted search
                if len(data_skills) >= 3:
                    search_queries.append(f"Data Engineer {' '.join(data_skills[:3])}")
                    search_queries.append(f"Data Architect {' '.join(data_skills[:2])}")
                else:
                    search_queries.append(f"Data Engineer {' '.join(data_skills)}")
            
            # Fallback queries based on user profile analysis
            if not search_queries:
                # Analyze user skills to determine best fallback
                user_skills_lower = [skill.lower() for skill in skills]
                
                if any('data' in skill for skill in user_skills_lower):
                    if any(skill in user_skills_lower for skill in ['architect', 'architecture', 'solution']):
                        search_queries.extend(['Data Architect', 'Solution Architect Data', 'Data Platform Architect'])
                    else:
                        search_queries.extend(['Data Engineer', 'Senior Data Engineer', 'Data Pipeline Engineer'])
                elif any(skill in user_skills_lower for skill in ['software', 'developer', 'programming']):
                    search_queries.extend(['Software Engineer', 'Backend Engineer', 'Full Stack Engineer'])
                else:
                    search_queries.extend(['Software Developer', 'Engineer'])
            
            print(f"🔍 Targeted search queries: {search_queries[:5]}")  # Show first 5
            
            # Search all available APIs with different queries
            aggregator = JobAggregator()
            
            for query in search_queries[:3]:  # Limit to 3 queries to avoid rate limits
                try:
                    jobs = await aggregator.search_all_apis(
                        query=query,
                        location=location or "",
                        country=user_country
                    )
                    aggregator_jobs.extend(jobs)
                    
                    # Add small delay between queries
                    await asyncio.sleep(0.5)
                    
                except Exception as e:
                    print(f"❌ Error searching with query '{query}': {e}")
                    continue
            
            print(f"✅ Fetched {len(aggregator_jobs)} jobs from JobAggregator APIs")
            
        except Exception as e:
            print(f"❌ Error using JobAggregator: {e}")
    else:
        print("⚠️  JobAggregator not available, skipping JSearch/Adzuna APIs")

    # Combine all real jobs
    all_real_jobs = remoteok_jobs + aggregator_jobs
    
    if all_real_jobs:
        # Remove duplicates and validate jobs
        unique_jobs = []
        seen_jobs = set()
        
        for job in all_real_jobs:
            # Create unique key
            job_key = (job.get('title', '').lower(), job.get('company', '').lower())
            
            if job_key not in seen_jobs:
                seen_jobs.add(job_key)
                # Validate job has required fields
                if job.get('title') and job.get('company'):
                    unique_jobs.append(job)
        
        # ENHANCED FILTERING: Remove irrelevant jobs based on user profile
        filtered_jobs = []
        user_is_data_professional = any(
            keyword in ' '.join(last_two_jobs).lower() 
            for keyword in ['data engineer', 'data architect', 'data scientist', 'data analyst', 'data platform']
        )
        
        for job in unique_jobs:
            job_title_lower = job.get('title', '').lower()
            
            # If user is a data professional, filter out non-data roles
            if user_is_data_professional:
                # Keep data-related roles
                if any(keyword in job_title_lower for keyword in [
                    'data engineer', 'data architect', 'data scientist', 'data analyst', 
                    'data platform', 'data pipeline', 'analytics engineer', 'ml engineer',
                    'machine learning', 'big data', 'etl', 'data warehouse'
                ]):
                    filtered_jobs.append(job)
                    print(f"✅ RELEVANT DATA ROLE: {job.get('title')} at {job.get('company')}")
                # Also keep senior technical roles that could be relevant
                elif any(keyword in job_title_lower for keyword in [
                    'solution architect', 'cloud architect', 'platform engineer',
                    'devops engineer', 'infrastructure engineer'
                ]) and any(tech in job_title_lower for tech in ['senior', 'lead', 'principal']):
                    filtered_jobs.append(job)
                    print(f"✅ RELEVANT SENIOR ROLE: {job.get('title')} at {job.get('company')}")
                else:
                    print(f"❌ FILTERED OUT: {job.get('title')} (not relevant for data professional)")
            else:
                # For non-data professionals, keep all technical roles
                if any(keyword in job_title_lower for keyword in [
                    'engineer', 'developer', 'architect', 'analyst', 'scientist'
                ]):
                    filtered_jobs.append(job)
                else:
                    print(f"❌ FILTERED OUT: {job.get('title')} (not technical role)")
        
        print(f"🎯 Filtered from {len(unique_jobs)} to {len(filtered_jobs)} relevant jobs")
        
        # Apply location-based prioritization to filtered jobs
        user_country = _extract_country_from_location(location) if location else ""
        if user_country and filtered_jobs:
            filtered_jobs = _prioritize_jobs_by_relevance_and_location(filtered_jobs, skills, last_two_jobs, experience, user_country)
            print(f"📍 Applied location prioritization for {user_country} to filtered jobs")
        else:
            # Sort by match score only if no user country
            filtered_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        print(f"✅ Returning {len(filtered_jobs)} highly relevant job recommendations")
        final_jobs = filtered_jobs[:15]  # Return top 15 most relevant jobs
        
        # Cache the results for future requests
        if use_cache and final_jobs:
            cache_jobs(skills, experience, last_two_jobs, final_jobs, location, ttl_minutes=30)
            print(f"💾 CACHED: Stored {len(final_jobs)} jobs for 30 minutes")
        
        return final_jobs
    else:
        print("❌ No real jobs found from any API")
        return []

def filter_jobs_by_location(jobs: List[Dict[str, Any]], location: str) -> List[Dict[str, Any]]:
    """Filter jobs by location preference"""
    if not location:
        return jobs
    
    location_lower = location.lower()
    filtered_jobs = []
    
    for job in jobs:
        job_location = job.get("location", "").lower()
        job_country = job.get("country", "").lower()
        
        # Check if job matches location
        if (location_lower in job_location or 
            location_lower in job_country or
            job.get("remote", False) or
            "remote" in job_location):
            filtered_jobs.append(job)
    
    return filtered_jobs

def calculate_salary_match(jobs: List[Dict[str, Any]], target_salary: Optional[int] = None) -> List[Dict[str, Any]]:
    """Add salary match scores to jobs"""
    if not target_salary:
        return jobs
    
    for job in jobs:
        salary_range = job.get("salary_range", "")
        # Simple salary parsing - in production would be more sophisticated
        if "$" in salary_range:
            try:
                # Extract numbers from salary range
                numbers = re.findall(r'\d+,?\d*', salary_range.replace(",", ""))
                if len(numbers) >= 2:
                    min_salary = int(numbers[0]) * 1000
                    max_salary = int(numbers[1]) * 1000
                    avg_salary = (min_salary + max_salary) / 2
                    
                    # Calculate salary match (closer to target = higher score)
                    salary_diff = abs(avg_salary - target_salary)
                    max_diff = target_salary * 0.5  # 50% difference = 0 score
                    salary_match = max(0, 100 - (salary_diff / max_diff * 100))
                    job["salary_match"] = round(salary_match)
            except:
                job["salary_match"] = 50  # Default neutral score
        else:
            job["salary_match"] = 50
    
    return jobs

async def get_personalized_job_recommendations(
    skills: List[str], 
    experience: str, 
    last_two_jobs: List[str], 
    location: Optional[str] = None,
    user_id: Optional[str] = None,
    use_cache: bool = True
) -> List[Dict[str, Any]]:
    """
    Get personalized job recommendations using REAL job APIs with enhanced location prioritization and caching.
    NO MOCK DATA - Only real jobs from legitimate job APIs.
    """
    if not REAL_APIS_AVAILABLE:
        print("❌ Real job APIs not available")
        return []
    
    # Check user-specific cache first if user_id provided
    if use_cache and user_id:
        cached_user_jobs = get_user_cached_jobs(user_id)
        if cached_user_jobs:
            print(f"👤 USER CACHE HIT: Returning {len(cached_user_jobs)} cached jobs for user {user_id}")
            return cached_user_jobs
    
    # Check general profile cache
    if use_cache:
        cached_jobs = get_cached_jobs(skills, experience, last_two_jobs, location)
        if cached_jobs:
            print(f"🎯 PROFILE CACHE HIT: Returning {len(cached_jobs)} cached jobs")
            # Also cache for user if user_id provided
            if user_id:
                profile_data = {
                    'skills': skills,
                    'experience': experience,
                    'last_jobs': last_two_jobs,
                    'location': location
                }
                cache_user_jobs(user_id, cached_jobs, profile_data)
            return cached_jobs
    
    print("🔍 CACHE MISS: Fetching fresh personalized jobs from APIs...")
    
    # Extract country from location for better job targeting
    user_country = _extract_country_from_location(location) if location else ""
    
    print(f"🔍 Generating job recommendations for:")
    print(f"   Skills: {skills}")
    print(f"   Experience: {experience}")
    print(f"   Last jobs: {last_two_jobs}")
    print(f"   Location: {location}")
    print(f"   Detected Country: {user_country}")
    
    try:
        # Initialize job aggregator
        job_aggregator = JobAggregator()
        
        # Create search query from skills and job titles
        search_terms = []
        
        # Add job titles to search terms
        if last_two_jobs:
            for job_title in last_two_jobs[:2]:  # Use last 2 jobs
                if job_title and len(job_title.strip()) > 0:
                    # Clean job title for search
                    clean_title = re.sub(r'[^\w\s]', ' ', job_title).strip()
                    if clean_title:
                        search_terms.append(clean_title)
        
        # Add key skills to search terms
        if skills:
            # Prioritize important technical skills
            priority_skills = [
                'Data Engineer', 'Software Engineer', 'Python', 'Java', 'Scala',
                'AWS', 'Azure', 'GCP', 'Spark', 'Kafka', 'SQL', 'Machine Learning',
                'DevOps', 'Kubernetes', 'Docker', 'Microservices'
            ]
            
            for skill in skills:
                if any(priority in skill for priority in priority_skills):
                    search_terms.append(skill)
                    if len(search_terms) >= 3:  # Limit search terms
                        break
        
        # Fallback search terms if none found
        if not search_terms:
            search_terms = ['Software Engineer', 'Data Engineer', 'Developer']
        
        # Set location for API search
        search_location = ""
        search_country = ""
        
        if user_country:
            search_country = user_country
            if user_country == 'Netherlands':
                search_location = "Netherlands"
            elif user_country == 'Germany':
                search_location = "Germany"
            elif user_country == 'United Kingdom':
                search_location = "United Kingdom"
            else:
                search_location = user_country
        
        # Search for jobs using multiple APIs
        all_jobs = []
        
        for search_term in search_terms[:2]:  # Limit to 2 search terms to avoid rate limits
            try:
                print(f"🔍 Searching for '{search_term}' jobs in {search_location or 'global'}")
                
                jobs = await job_aggregator.search_all_apis(
                    query=search_term,
                    location=search_location,
                    country=search_country
                )
                
                if jobs:
                    print(f"✅ Found {len(jobs)} jobs for '{search_term}'")
                    all_jobs.extend(jobs)
                else:
                    print(f"❌ No jobs found for '{search_term}'")
                    
            except Exception as e:
                print(f"❌ Error searching for '{search_term}': {e}")
                continue
        
        if not all_jobs:
            print("❌ No jobs found from any API")
            return []
        
        # Remove duplicates based on job title and company
        unique_jobs = []
        seen_jobs = set()
        
        for job in all_jobs:
            job_key = f"{job.get('title', '').lower()}_{job.get('company', '').lower()}"
            if job_key not in seen_jobs:
                seen_jobs.add(job_key)
                unique_jobs.append(job)
        
        print(f"📋 Found {len(unique_jobs)} unique jobs after deduplication")
        
        # Prioritize jobs by location (Netherlands users get Netherlands jobs first)
        prioritized_jobs = _prioritize_jobs_by_location(unique_jobs, location, user_country)
        
        # Limit to 15 jobs and ensure they're valid
        final_jobs = []
        for job in prioritized_jobs[:15]:
            if validate_job_posting(job):
                final_jobs.append(job)
        
        print(f"✅ Generated {len(final_jobs)} job recommendations")
        
        # Cache the results
        if use_cache and final_jobs:
            # Cache for general profile
            cache_jobs(skills, experience, last_two_jobs, final_jobs, location, ttl_minutes=30)
            print(f"💾 CACHED: Stored {len(final_jobs)} jobs for profile (30 minutes)")
            
            # Cache for specific user if user_id provided
            if user_id:
                profile_data = {
                    'skills': skills,
                    'experience': experience,
                    'last_jobs': last_two_jobs,
                    'location': location
                }
                cache_user_jobs(user_id, final_jobs, profile_data)
                print(f"👤 USER CACHED: Stored {len(final_jobs)} jobs for user {user_id}")
        
        return final_jobs
        
    except Exception as e:
        print(f"❌ Error generating job recommendations: {e}")
        return [] 