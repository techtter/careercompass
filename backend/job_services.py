"""
Job Services Module for CareerCompassAI

This module provides job recommendation services using multiple job APIs
and AI-powered matching to deliver personalized job recommendations.
"""

import asyncio
import json
import random
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Import real job API services
try:
    from job_api_services import JobAggregator, validate_job_posting, check_job_availability
    REAL_APIS_AVAILABLE = True
except ImportError:
    REAL_APIS_AVAILABLE = False
    print("⚠️  Real job APIs not available, using mock data")

def _extract_country_from_location(location: str) -> str:
    """
    Extract country name from location string using word boundaries to prevent partial matches.
    """
    if not location:
        return ""
    
    location_lower = location.lower()
    
    # Country mapping with word boundary patterns
    country_patterns = {
        r'\busa\b|\bus\b|\bunited states\b|\bamerica\b': 'United States',
        r'\buk\b|\bunited kingdom\b|\bbritain\b|\bengland\b': 'United Kingdom',
        r'\bcanada\b': 'Canada',
        r'\bgermany\b|\bdeutschland\b': 'Germany',
        r'\bfrance\b': 'France',
        r'\bspain\b': 'Spain',
        r'\bitaly\b': 'Italy',
        r'\bnetherlands\b|\bholland\b': 'Netherlands',
        r'\bbelgium\b': 'Belgium',
        r'\bswitzerland\b': 'Switzerland',
        r'\baustria\b': 'Austria',
        r'\bsweden\b': 'Sweden',
        r'\bnorway\b': 'Norway',
        r'\bdenmark\b': 'Denmark',
        r'\bfinland\b': 'Finland',
        r'\bindia\b': 'India',
        r'\bchina\b': 'China',
        r'\bjapan\b': 'Japan',
        r'\bsingapore\b': 'Singapore',
        r'\baustralia\b': 'Australia',
        r'\bbrazil\b': 'Brazil',
        r'\bmexico\b': 'Mexico',
        r'\bireland\b': 'Ireland',
        r'\bpoland\b': 'Poland',
        r'\bczech republic\b': 'Czech Republic'
    }
    
    # Check for country patterns using word boundaries
    import re
    for pattern, country in country_patterns.items():
        if re.search(pattern, location_lower):
            return country
    
    # Check for US state abbreviations
    us_states = ['ca', 'ny', 'tx', 'fl', 'wa', 'il', 'pa', 'oh', 'ga', 'nc', 'mi', 'nj', 'va', 'tn', 'az', 'ma', 'in', 'mo', 'md', 'wi', 'co', 'mn', 'sc', 'al', 'la', 'ky', 'or', 'ok', 'ct', 'ut', 'ia', 'nv', 'ar', 'ms', 'ks', 'nm', 'ne', 'wv', 'id', 'hi', 'nh', 'me', 'mt', 'ri', 'de', 'sd', 'nd', 'ak', 'vt', 'wy']
    for state in us_states:
        pattern = rf'\b{state}\b'
        if re.search(pattern, location_lower):
            return 'United States'
    
    return location  # Return original if no mapping found

async def get_real_job_recommendations(
    skills: List[str], 
    experience: str, 
    last_two_jobs: List[str], 
    location: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get real job recommendations from multiple job APIs
    """
    if not REAL_APIS_AVAILABLE:
        return []
    
    try:
        # Extract country for better API targeting
        user_country = _extract_country_from_location(location) if location else ""
        
        # Create search queries based on user profile
        search_queries = []
        
        # Generate queries from job titles
        for job_title in last_two_jobs:
            if job_title and len(job_title.strip()) > 2:
                # Clean job title (remove certifications, contact info)
                clean_title = job_title.replace('❖', '').strip()
                # Remove phone numbers and emails
                import re
                clean_title = re.sub(r'\+?\d{1,3}[-.\s]?\d{3,4}[-.\s]?\d{3,4}[-.\s]?\d{3,4}', '', clean_title)
                clean_title = re.sub(r'\S+@\S+', '', clean_title)
                clean_title = clean_title.strip()
                
                if clean_title and len(clean_title) > 5:
                    search_queries.append(clean_title)
        
        # Generate queries from skills (focus on main technologies)
        tech_skills = []
        for skill in skills[:5]:  # Top 5 skills
            skill_clean = skill.strip()
            if len(skill_clean) > 2 and not any(cert in skill_clean.lower() for cert in ['certified', 'certification']):
                tech_skills.append(skill_clean)
        
        if tech_skills:
            search_queries.append(' '.join(tech_skills[:3]))  # Combine top 3 skills
        
        # Fallback queries if no good job titles
        if not search_queries:
            if any('data' in skill.lower() for skill in skills):
                search_queries.append('Data Engineer')
            elif any('software' in skill.lower() or 'developer' in skill.lower() for skill in skills):
                search_queries.append('Software Engineer')
            else:
                search_queries.append('Software Developer')
        
        print(f"🔍 Searching real job APIs with queries: {search_queries}")
        print(f"   Location: {location}")
        print(f"   Country: {user_country}")
        
        # Search all APIs with different queries
        aggregator = JobAggregator()
        all_jobs = []
        
        for query in search_queries[:3]:  # Limit to 3 queries to avoid rate limits
            try:
                jobs = await aggregator.search_all_apis(
                    query=query,
                    location=location or "",
                    country=user_country
                )
                all_jobs.extend(jobs)
                
                # Add small delay between queries
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"❌ Error searching with query '{query}': {e}")
                continue
        
        # Remove duplicates and validate jobs
        unique_jobs = []
        seen_jobs = set()
        
        for job in all_jobs:
            # Create unique key
            job_key = (job.get('title', '').lower(), job.get('company', '').lower())
            
            if job_key not in seen_jobs and validate_job_posting(job):
                seen_jobs.add(job_key)
                unique_jobs.append(job)
        
        # Sort by match score and limit results
        unique_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        print(f"✅ Found {len(unique_jobs)} real job recommendations from APIs")
        
        return unique_jobs[:20]  # Return top 20 jobs
        
    except Exception as e:
        print(f"❌ Error getting real job recommendations: {e}")
        return []

def _get_mock_job_recommendations(skills: List[str], experience: str, last_two_jobs: List[str], location: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Generate mock job recommendations for development/testing purposes.
    Returns realistic job data that matches the user's profile.
    Enhanced to better match recent job titles and location.
    """
    
    print(f"🔍 Generating MOCK job recommendations for:")
    print(f"   Skills: {skills}")
    print(f"   Experience: {experience}")
    print(f"   Last jobs: {last_two_jobs}")
    print(f"   Location: {location}")
    
    # Extract country from location for better job matching
    user_country = _extract_country_from_location(location) if location else None
    print(f"   Detected Country: {user_country}")
    
    # Enhanced job templates with more variety and better matching
    job_templates = [
        # Data Engineering Jobs
        {
            "title": "Senior Data Engineer",
            "company": "DataFlow Technologies",
            "location": "San Francisco, CA" if user_country == "United States" else "London, UK" if user_country == "United Kingdom" else "Berlin, Germany" if user_country == "Germany" else "Toronto, Canada" if user_country == "Canada" else "Sydney, Australia" if user_country == "Australia" else "Remote",
            "salary_range": "$140,000 - $180,000" if user_country == "United States" else "£80,000 - £120,000" if user_country == "United Kingdom" else "€70,000 - €100,000" if user_country == "Germany" else "CAD $120,000 - $160,000" if user_country == "Canada" else "AUD $130,000 - $170,000" if user_country == "Australia" else "$120,000 - $160,000",
            "description": f"Lead data engineering initiatives in {user_country or 'a global environment'}. Build scalable data pipelines and work with cutting-edge technologies.",
            "required_skills": ["Python", "Apache Spark", "Kafka", "AWS", "SQL"],
            "experience_level": "Senior",
            "job_type": "Full-time",
            "remote": user_country not in ["United States", "United Kingdom", "Germany"],
            "keywords": ["data", "engineer", "spark", "kafka", "etl", "pipeline"]
        },
        {
            "title": "Lead Data Engineer / Solution Architect",
            "company": "CloudData Solutions",
            "location": "New York, NY" if user_country == "United States" else "Manchester, UK" if user_country == "United Kingdom" else "Munich, Germany" if user_country == "Germany" else "Vancouver, Canada" if user_country == "Canada" else "Melbourne, Australia" if user_country == "Australia" else "Remote",
            "salary_range": "$160,000 - $200,000" if user_country == "United States" else "£90,000 - £130,000" if user_country == "United Kingdom" else "€80,000 - €110,000" if user_country == "Germany" else "CAD $140,000 - $180,000" if user_country == "Canada" else "AUD $150,000 - $190,000" if user_country == "Australia" else "$140,000 - $180,000",
            "description": f"Architect and implement enterprise data solutions in {user_country or 'a distributed team environment'}. Lead technical teams and drive innovation.",
            "required_skills": ["Scala", "Apache Spark", "Kafka", "Azure", "Data Architecture"],
            "experience_level": "Lead",
            "job_type": "Full-time",
            "remote": False,
            "keywords": ["lead", "architect", "solution", "data", "enterprise"]
        },
        {
            "title": "Principal Data Engineer",
            "company": "TechGiant Corp",
            "location": "Seattle, WA" if user_country == "United States" else "Edinburgh, UK" if user_country == "United Kingdom" else "Frankfurt, Germany" if user_country == "Germany" else "Montreal, Canada" if user_country == "Canada" else "Brisbane, Australia" if user_country == "Australia" else "Remote",
            "salary_range": "$180,000 - $220,000" if user_country == "United States" else "£100,000 - £140,000" if user_country == "United Kingdom" else "€90,000 - €120,000" if user_country == "Germany" else "CAD $160,000 - $200,000" if user_country == "Canada" else "AUD $170,000 - $210,000" if user_country == "Australia" else "$160,000 - $200,000",
            "description": f"Drive data engineering strategy and innovation in {user_country or 'a global technology company'}. Mentor teams and shape technical direction.",
            "required_skills": ["Python", "Scala", "Kafka", "Snowflake", "Machine Learning"],
            "experience_level": "Principal",
            "job_type": "Full-time",
            "remote": True,
            "keywords": ["principal", "strategy", "innovation", "data", "ml"]
        },
        
        # Software Engineering Jobs
        {
            "title": "Senior Software Engineer",
            "company": "InnovateTech",
            "location": "Austin, TX" if user_country == "United States" else "Cambridge, UK" if user_country == "United Kingdom" else "Hamburg, Germany" if user_country == "Germany" else "Calgary, Canada" if user_country == "Canada" else "Perth, Australia" if user_country == "Australia" else "Remote",
            "salary_range": "$130,000 - $170,000" if user_country == "United States" else "£75,000 - £110,000" if user_country == "United Kingdom" else "€65,000 - €95,000" if user_country == "Germany" else "CAD $110,000 - $150,000" if user_country == "Canada" else "AUD $120,000 - $160,000" if user_country == "Australia" else "$110,000 - $150,000",
            "description": f"Develop innovative software solutions in {user_country or 'a collaborative remote environment'}. Work with modern technologies and agile methodologies.",
            "required_skills": ["Java", "Spring Boot", "Microservices", "Kubernetes", "AWS"],
            "experience_level": "Senior",
            "job_type": "Full-time",
            "remote": True,
            "keywords": ["software", "engineer", "java", "spring", "microservices"]
        },
        
        # Cloud/DevOps Jobs
        {
            "title": "Cloud Solutions Architect",
            "company": "CloudFirst Technologies",
            "location": "Denver, CO" if user_country == "United States" else "Bristol, UK" if user_country == "United Kingdom" else "Stuttgart, Germany" if user_country == "Germany" else "Ottawa, Canada" if user_country == "Canada" else "Adelaide, Australia" if user_country == "Australia" else "Remote",
            "salary_range": "$150,000 - $190,000" if user_country == "United States" else "£85,000 - £125,000" if user_country == "United Kingdom" else "€75,000 - €105,000" if user_country == "Germany" else "CAD $130,000 - $170,000" if user_country == "Canada" else "AUD $140,000 - $180,000" if user_country == "Australia" else "$130,000 - $170,000",
            "description": f"Design and implement cloud infrastructure solutions in {user_country or 'a global cloud environment'}. Lead digital transformation initiatives.",
            "required_skills": ["AWS", "Azure", "Terraform", "Kubernetes", "DevOps"],
            "experience_level": "Senior",
            "job_type": "Full-time",
            "remote": False,
            "keywords": ["cloud", "architect", "aws", "azure", "devops"]
        }
    ]
    
    # Enhanced matching logic
    user_skills_lower = [skill.lower().strip() for skill in skills]
    last_jobs_lower = [job.lower().strip() for job in last_two_jobs]
    matched_jobs = []
    
    # Extract experience level from user's job titles
    user_level = "Mid-level"  # default
    for job in last_jobs_lower:
        if any(level in job for level in ["senior", "sr.", "lead", "principal", "staff"]):
            user_level = "Senior"
            break
        elif any(level in job for level in ["manager", "director", "head"]):
            user_level = "Leadership"
            break
    
    for template in job_templates:
        # Calculate skill match score
        required_skills_lower = [skill.lower() for skill in template["required_skills"]]
        skill_matches = sum(1 for skill in user_skills_lower 
                          if any(req_skill in skill or skill in req_skill 
                                for req_skill in required_skills_lower))
        skill_match_score = skill_matches / len(template["required_skills"]) if template["required_skills"] else 0
        
        # Enhanced job title matching
        title_match_score = 0
        template_keywords = template.get("keywords", [])
        template_title_lower = template["title"].lower()
        
        for user_job in last_jobs_lower:
            # Direct title matching
            if user_job in template_title_lower or template_title_lower in user_job:
                title_match_score = max(title_match_score, 0.9)
            
            # Keyword matching
            for keyword in template_keywords:
                if keyword in user_job or any(word in user_job for word in keyword.split()):
                    title_match_score = max(title_match_score, 0.7)
            
            # Role type matching (engineer, architect, etc.)
            user_job_words = user_job.split()
            template_words = template_title_lower.split()
            common_role_words = set(user_job_words) & set(template_words)
            if common_role_words:
                title_match_score = max(title_match_score, 0.5)
        
        # Location matching bonus
        location_match_score = 0
        if location:
            location_lower = location.lower()
            template_location_lower = template["location"].lower()
            
            if location_lower in template_location_lower or template_location_lower in location_lower:
                location_match_score = 0.3
            elif template.get("remote", False):
                location_match_score = 0.2  # Remote jobs get some location bonus
            elif "remote" in template_location_lower or "global" in template_location_lower:
                location_match_score = 0.2
        else:
            # If no location specified, prefer remote jobs
            if template.get("remote", False):
                location_match_score = 0.1
        
        # Experience level matching
        experience_match_score = 0
        template_level = template.get("experience_level", "Mid-level")
        if user_level == template_level:
            experience_match_score = 0.2
        elif (user_level == "Senior" and template_level in ["Lead", "Principal"]) or \
             (user_level == "Leadership" and template_level in ["Senior", "Lead", "Principal"]):
            experience_match_score = 0.1
        
        # Calculate total match score
        total_match_score = (
            skill_match_score * 0.4 +           # 40% weight on skills
            title_match_score * 0.3 +           # 30% weight on job title
            location_match_score * 0.2 +        # 20% weight on location
            experience_match_score * 0.1         # 10% weight on experience level
        )
        
        # Include jobs with reasonable match scores or strong title matches
        if total_match_score > 0.25 or title_match_score > 0.6:
            # Extract country from location
            location_parts = template["location"].split(", ")
            country = location_parts[-1] if len(location_parts) > 1 else "USA"
            
            job = {
                "id": f"mock_job_{len(matched_jobs) + 1}",
                "title": template["title"],
                "company": template["company"],
                "location": template["location"],
                "country": country,
                "salary": template["salary_range"],
                "description": template["description"],
                "required_skills": template["required_skills"],
                "experience_level": template["experience_level"],
                "job_type": template["job_type"],
                "remote": template["remote"],
                "match_score": round(total_match_score * 100),
                "skill_matches": skill_matches,
                "title_match": round(title_match_score * 100),
                "location_match": round(location_match_score * 100),
                "source": "CareerCompass AI (Demo)",
                "postedDate": (datetime.now() - timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                "daysAgo": random.randint(1, 30),
                "applyUrl": f"https://www.linkedin.com/jobs/search/?keywords={template['title'].replace(' ', '%20')}&location={template['location'].replace(' ', '%20').replace(',', '%2C')}",
                "company_logo": f"https://logo.clearbit.com/{template['company'].lower().replace(' ', '').replace(',', '')}.com",
                "is_real_job": False  # Mark as mock data
            }
            matched_jobs.append(job)
    
    # Sort by total match score, then by title match, then by skill match
    matched_jobs.sort(key=lambda x: (x["match_score"], x["title_match"], x["skill_matches"]), reverse=True)
    
    # Add location-specific jobs if user provided location
    if location and len(matched_jobs) < 10:
        location_jobs = _generate_location_specific_jobs(location, skills, last_two_jobs, len(matched_jobs))
        matched_jobs.extend(location_jobs)
    
    # Add additional variety if still not enough jobs
    if len(matched_jobs) < 15:
        additional_jobs = _generate_additional_jobs(skills, last_two_jobs, user_level, len(matched_jobs))
        matched_jobs.extend(additional_jobs)
    
    return matched_jobs[:15]  # Return top 15 matches

def _generate_location_specific_jobs(location: str, skills: List[str], last_jobs: List[str], start_id: int) -> List[Dict[str, Any]]:
    """Generate jobs specific to the user's location"""
    location_jobs = []
    
    # Common job titles based on user's background
    base_titles = []
    for job in last_jobs:
        if "data engineer" in job.lower():
            base_titles.extend(["Data Engineer", "Senior Data Engineer", "Data Platform Engineer"])
        elif "software engineer" in job.lower():
            base_titles.extend(["Software Engineer", "Senior Software Engineer", "Full Stack Engineer"])
        elif "architect" in job.lower():
            base_titles.extend(["Solutions Architect", "Technical Architect", "System Architect"])
    
    if not base_titles:
        base_titles = ["Software Engineer", "Data Engineer", "DevOps Engineer"]
    
    # Generate location-specific companies and jobs
    for i, title in enumerate(base_titles[:5]):
        # Extract country from location
        location_parts = location.split(", ")
        country = location_parts[-1] if len(location_parts) > 1 else "USA"
        
        job = {
            "id": f"mock_location_job_{start_id + i + 1}",
            "title": title,
            "company": f"Local Tech Solutions {i+1}",
            "location": location,
            "country": country,
            "salary": "$90,000 - $130,000",
            "description": f"Join our {location}-based team to work on innovative technology solutions.",
            "required_skills": skills[:4] if skills else ["Programming", "Problem Solving"],
            "experience_level": "Mid-Senior",
            "job_type": "Full-time",
            "remote": False,
            "match_score": random.randint(70, 85),
            "skill_matches": min(len(skills), 4),
            "title_match": 80 if any(job_word in title.lower() for job in last_jobs for job_word in job.lower().split()) else 60,
            "location_match": 100,  # Perfect location match
            "source": "CareerCompass AI (Demo)",
            "postedDate": (datetime.now() - timedelta(days=random.randint(1, 15))).strftime("%Y-%m-%d"),
            "daysAgo": random.randint(1, 15),
            "applyUrl": f"https://www.indeed.com/jobs?q={title.replace(' ', '+')}&l={location.replace(' ', '+').replace(',', '%2C')}",
            "company_logo": f"https://via.placeholder.com/100x100?text=Local{i+1}",
            "is_real_job": False
        }
        location_jobs.append(job)
    
    return location_jobs

def _generate_additional_jobs(skills: List[str], last_jobs: List[str], user_level: str, start_id: int) -> List[Dict[str, Any]]:
    """Generate additional job variety to reach target count"""
    additional_jobs = []
    
    # Job title variations based on skills and experience
    job_variations = [
        "Software Developer", "Full Stack Developer", "Backend Engineer", 
        "Frontend Engineer", "DevOps Engineer", "Cloud Engineer",
        "Data Analyst", "Machine Learning Engineer", "Product Manager",
        "Technical Lead", "Engineering Manager", "Solutions Engineer"
    ]
    
    # Salary ranges based on user level
    salary_ranges = [
        "$80,000 - $120,000", "$90,000 - $130,000", "$100,000 - $140,000",
        "$110,000 - $150,000", "$120,000 - $160,000", "$130,000 - $170,000"
    ]
    
    for i in range(min(10, 15 - start_id)):
        title = job_variations[i % len(job_variations)]
        location = "Remote" if i % 3 == 0 else f"Tech Hub {i+1}"
        country = "Global" if i % 3 == 0 else "USA"
        
        job = {
            "id": f"mock_additional_job_{start_id + i + 1}",
            "title": title,
            "company": f"TechCompany {i+1}",
            "location": location,
            "country": country,
            "salary": salary_ranges[i % len(salary_ranges)],
            "description": f"Exciting opportunity to work with cutting-edge technologies in a {user_level.lower()} role.",
            "required_skills": skills[:3] if skills else ["Programming"],
            "experience_level": user_level,
            "job_type": "Full-time",
            "remote": i % 3 == 0,
            "match_score": random.randint(60, 80),
            "skill_matches": min(len(skills), 3),
            "title_match": 70 if any(job_word in title.lower() for job in last_jobs for job_word in job.lower().split()) else 50,
            "location_match": 20,
            "source": "CareerCompass AI (Demo)",
            "postedDate": (datetime.now() - timedelta(days=random.randint(1, 20))).strftime("%Y-%m-%d"),
            "daysAgo": random.randint(1, 20),
            "applyUrl": f"https://www.glassdoor.com/Job/jobs.htm?suggestCount=0&suggestChosen=false&clickSource=searchBtn&typedKeyword={title.replace(' ', '+')}&sc.keyword={title.replace(' ', '+')}&locT=&locId=",
            "company_logo": f"https://via.placeholder.com/100x100?text=Company{i+1}",
            "is_real_job": False
        }
        additional_jobs.append(job)
    
    return additional_jobs

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
        print(f"🔍 Generating job recommendations for:")
        print(f"   Skills: {skills}")
        print(f"   Experience: {experience}")
        print(f"   Last jobs: {last_two_jobs}")
        print(f"   Location: {location}")
        
        # Extract country from location for better job matching
        user_country = _extract_country_from_location(location) if location else None
        print(f"   Detected Country: {user_country}")
        
        # Try to get real job recommendations first
        real_jobs = []
        if REAL_APIS_AVAILABLE and os.getenv('USE_REAL_JOBS', 'false').lower() == 'true':
            print("🌐 Attempting to fetch real job recommendations...")
            real_jobs = await get_real_job_recommendations(skills, experience, last_two_jobs, location)
        
        # If we have real jobs, use them; otherwise fall back to mock data
        if real_jobs:
            print(f"✅ Using {len(real_jobs)} real job recommendations")
            return real_jobs
        else:
            print("⚠️  No real jobs found, using mock data for demonstration")
            # Simulate API call delay for realistic experience
            await asyncio.sleep(0.5)
            
            # Generate mock recommendations
            recommendations = _get_mock_job_recommendations(skills, experience, last_two_jobs, location)
            
            print(f"✅ Generated {len(recommendations)} mock job recommendations")
            
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
                "country": "Global",
                "salary": "$70,000 - $100,000",
                "description": "Join our team to build innovative software solutions.",
                "required_skills": skills[:3] if skills else ["Programming"],
                "experience_level": "Mid-level",
                "job_type": "Full-time",
                "remote": True,
                "match_score": 75,
                "skill_matches": min(len(skills), 3),
                "source": "CareerCompass AI (Fallback)",
                "postedDate": datetime.now().strftime("%Y-%m-%d"),
                "daysAgo": 5,
                "applyUrl": "https://www.linkedin.com/jobs/search/?keywords=Software%20Developer",
                "company_logo": "https://via.placeholder.com/100x100?text=Company",
                "is_real_job": False
            }
        ]

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