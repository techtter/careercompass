"""
Job Services Module for CareerCompassAI

This module provides job recommendation services using multiple job APIs
and AI-powered matching to deliver personalized job recommendations.
"""

import asyncio
import json
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

def _get_mock_job_recommendations(skills: List[str], experience: str, last_two_jobs: List[str], location: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Generate mock job recommendations for development/testing purposes.
    Returns realistic job data that matches the user's profile.
    """
    
    # Define job templates based on common skills and roles
    job_templates = [
        {
            "title": "Senior Software Engineer",
            "company": "TechCorp Solutions",
            "location": "San Francisco, CA",
            "salary_range": "$120,000 - $160,000",
            "description": "Join our team to build scalable web applications using modern technologies.",
            "required_skills": ["Python", "JavaScript", "React", "AWS"],
            "experience_level": "Senior",
            "job_type": "Full-time",
            "remote": True
        },
        {
            "title": "Data Engineer",
            "company": "DataFlow Inc",
            "location": "New York, NY",
            "salary_range": "$110,000 - $145,000",
            "description": "Design and maintain data pipelines for large-scale analytics.",
            "required_skills": ["Python", "SQL", "AWS", "ETL", "Spark"],
            "experience_level": "Mid-Senior",
            "job_type": "Full-time",
            "remote": False
        },
        {
            "title": "Full Stack Developer",
            "company": "StartupXYZ",
            "location": "Austin, TX",
            "salary_range": "$90,000 - $120,000",
            "description": "Build end-to-end web applications in a fast-paced startup environment.",
            "required_skills": ["JavaScript", "React", "Node.js", "MongoDB"],
            "experience_level": "Mid-level",
            "job_type": "Full-time",
            "remote": True
        },
        {
            "title": "Machine Learning Engineer",
            "company": "AI Innovations",
            "location": "Seattle, WA",
            "salary_range": "$130,000 - $170,000",
            "description": "Develop and deploy ML models for production systems.",
            "required_skills": ["Python", "TensorFlow", "AWS", "Machine Learning"],
            "experience_level": "Senior",
            "job_type": "Full-time",
            "remote": True
        },
        {
            "title": "DevOps Engineer",
            "company": "CloudTech Systems",
            "location": "Denver, CO",
            "salary_range": "$105,000 - $140,000",
            "description": "Manage cloud infrastructure and CI/CD pipelines.",
            "required_skills": ["AWS", "Docker", "Kubernetes", "Python"],
            "experience_level": "Mid-Senior",
            "job_type": "Full-time",
            "remote": True
        },
        {
            "title": "Product Manager",
            "company": "InnovateCorp",
            "location": "Los Angeles, CA",
            "salary_range": "$115,000 - $150,000",
            "description": "Lead product strategy and work with cross-functional teams.",
            "required_skills": ["Product Management", "Analytics", "Communication"],
            "experience_level": "Senior",
            "job_type": "Full-time",
            "remote": False
        },
        {
            "title": "Frontend Developer",
            "company": "WebSolutions Ltd",
            "location": "Chicago, IL",
            "salary_range": "$85,000 - $115,000",
            "description": "Create beautiful and responsive user interfaces.",
            "required_skills": ["JavaScript", "React", "CSS", "HTML"],
            "experience_level": "Mid-level",
            "job_type": "Full-time",
            "remote": True
        },
        {
            "title": "Backend Developer",
            "company": "ServerTech Inc",
            "location": "Boston, MA",
            "salary_range": "$95,000 - $125,000",
            "description": "Build robust APIs and server-side applications.",
            "required_skills": ["Python", "Django", "PostgreSQL", "Redis"],
            "experience_level": "Mid-level",
            "job_type": "Full-time",
            "remote": True
        },
        {
            "title": "Data Scientist",
            "company": "Analytics Pro",
            "location": "San Diego, CA",
            "salary_range": "$120,000 - $155,000",
            "description": "Extract insights from data to drive business decisions.",
            "required_skills": ["Python", "R", "SQL", "Machine Learning", "Statistics"],
            "experience_level": "Senior",
            "job_type": "Full-time",
            "remote": True
        },
        {
            "title": "Cloud Architect",
            "company": "CloudFirst Solutions",
            "location": "Portland, OR",
            "salary_range": "$140,000 - $180,000",
            "description": "Design scalable cloud infrastructure solutions.",
            "required_skills": ["AWS", "Azure", "Cloud Architecture", "Python"],
            "experience_level": "Senior",
            "job_type": "Full-time",
            "remote": True
        }
    ]
    
    # Calculate skill matches and generate personalized recommendations
    user_skills_lower = [skill.lower().strip() for skill in skills]
    matched_jobs = []
    
    for template in job_templates:
        # Calculate skill match score
        required_skills_lower = [skill.lower() for skill in template["required_skills"]]
        skill_matches = sum(1 for skill in user_skills_lower if any(req_skill in skill or skill in req_skill for req_skill in required_skills_lower))
        match_score = skill_matches / len(template["required_skills"]) if template["required_skills"] else 0
        
        # Check if job title matches user's experience
        title_match = any(job.lower() in template["title"].lower() or template["title"].lower() in job.lower() 
                         for job in last_two_jobs)
        
        if match_score > 0.2 or title_match:  # Include jobs with >20% skill match or title match
            job = {
                "id": f"job_{len(matched_jobs) + 1}",
                "title": template["title"],
                "company": template["company"],
                "location": template["location"],
                "salary_range": template["salary_range"],
                "description": template["description"],
                "required_skills": template["required_skills"],
                "experience_level": template["experience_level"],
                "job_type": template["job_type"],
                "remote": template["remote"],
                "match_score": round(match_score * 100),
                "skill_matches": skill_matches,
                "source": "CareerCompass AI",
                "posted_date": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                "daysAgo": random.randint(1, 30),
                "apply_url": f"https://example.com/jobs/{len(matched_jobs) + 1}",
                "company_logo": f"https://logo.clearbit.com/{template['company'].lower().replace(' ', '')}.com"
            }
            matched_jobs.append(job)
    
    # Sort by match score and return top results
    matched_jobs.sort(key=lambda x: x["match_score"], reverse=True)
    
    # Add some additional variety if we don't have enough matches
    if len(matched_jobs) < 15:
        additional_jobs = [
            {
                "id": f"job_{len(matched_jobs) + i + 1}",
                "title": f"Software Engineer",
                "company": f"TechCompany {i+1}",
                "location": "Remote",
                "salary_range": "$80,000 - $120,000",
                "description": "Exciting opportunity to work with cutting-edge technologies.",
                "required_skills": skills[:3] if skills else ["Programming"],
                "experience_level": "Mid-level",
                "job_type": "Full-time",
                "remote": True,
                "match_score": random.randint(60, 85),
                "skill_matches": min(len(skills), 3),
                "source": "CareerCompass AI",
                "posted_date": (datetime.now() - timedelta(days=random.randint(1, 20))).strftime("%Y-%m-%d"),
                "daysAgo": random.randint(1, 20),
                "apply_url": f"https://example.com/jobs/{len(matched_jobs) + i + 1}",
                "company_logo": f"https://via.placeholder.com/100x100?text=Company{i+1}"
            }
            for i in range(15 - len(matched_jobs))
        ]
        matched_jobs.extend(additional_jobs)
    
    return matched_jobs[:25]  # Return top 25 matches

async def get_personalized_job_recommendations(
    skills: List[str], 
    experience: str, 
    last_two_jobs: List[str], 
    location: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get personalized job recommendations based on user profile.
    
    Args:
        skills: List of user's skills
        experience: User's experience description
        last_two_jobs: User's last two job titles
        location: Preferred job location (optional)
    
    Returns:
        List of job recommendations with detailed information
    """
    try:
        # For now, return mock data
        # In production, this would integrate with real job APIs like:
        # - LinkedIn Jobs API
        # - Indeed API
        # - Glassdoor API
        # - RemoteOK API
        # - AngelList API
        
        print(f"🔍 Generating job recommendations for:")
        print(f"   Skills: {skills}")
        print(f"   Experience: {experience}")
        print(f"   Last jobs: {last_two_jobs}")
        print(f"   Location: {location}")
        
        # Simulate API call delay
        await asyncio.sleep(0.5)
        
        # Generate personalized recommendations
        recommendations = _get_mock_job_recommendations(skills, experience, last_two_jobs, location)
        
        print(f"✅ Generated {len(recommendations)} job recommendations")
        
        return recommendations
        
    except Exception as e:
        print(f"❌ Error in job recommendations: {e}")
        # Return fallback recommendations
        return [
            {
                "id": "fallback_1",
                "title": "Software Developer",
                "company": "Tech Solutions Inc",
                "location": "Remote",
                "salary_range": "$70,000 - $100,000",
                "description": "Join our team to build innovative software solutions.",
                "required_skills": skills[:3] if skills else ["Programming"],
                "experience_level": "Mid-level",
                "job_type": "Full-time",
                "remote": True,
                "match_score": 75,
                "skill_matches": min(len(skills), 3),
                "source": "CareerCompass AI",
                "posted_date": datetime.now().strftime("%Y-%m-%d"),
                "daysAgo": 5,
                "apply_url": "https://example.com/jobs/fallback_1",
                "company_logo": "https://via.placeholder.com/100x100?text=Company"
            }
        ]

# Additional utility functions for job services

def filter_jobs_by_location(jobs: List[Dict[str, Any]], location: str) -> List[Dict[str, Any]]:
    """Filter jobs by location preference"""
    if not location:
        return jobs
    
    location_lower = location.lower()
    filtered = []
    
    for job in jobs:
        job_location = job.get("location", "").lower()
        if (location_lower in job_location or 
            job_location in location_lower or 
            job.get("remote", False)):
            filtered.append(job)
    
    return filtered

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
                import re
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