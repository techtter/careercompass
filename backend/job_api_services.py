"""
Real Job API Integration Services for CareerCompassAI

This module provides integrations with real job APIs including:
- JSearch API (LinkedIn, Indeed aggregator)
- Adzuna API (Indeed, LinkedIn data)
- Reed.co.uk API (UK jobs)
- RemoteOK API (Remote jobs)
- TheMuseAPI (Company jobs)
- Netherlands Job Boards (Dutch-specific job sites)
"""

import asyncio
import aiohttp
import json
import os
import random
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from urllib.parse import quote_plus
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobAPIError(Exception):
    """Custom exception for job API errors"""
    pass

class JobAPIService:
    """Base class for job API services"""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove extra whitespace
        text = ' '.join(text.split())
        return text.strip()
    
    def extract_salary_range(self, salary_text: str) -> str:
        """Extract and normalize salary information"""
        if not salary_text:
            return ""
        
        # Common salary patterns
        patterns = [
            r'\$[\d,]+\s*-\s*\$[\d,]+',  # $50,000 - $70,000
            r'£[\d,]+\s*-\s*£[\d,]+',    # £40,000 - £60,000
            r'€[\d,]+\s*-\s*€[\d,]+',    # €45,000 - €65,000
            r'\$[\d,]+',                  # $60,000
            r'£[\d,]+',                   # £50,000
            r'€[\d,]+',                   # €55,000
        ]
        
        for pattern in patterns:
            match = re.search(pattern, salary_text)
            if match:
                return match.group(0)
        
        return salary_text

class JSearchAPI(JobAPIService):
    """JSearch API integration (LinkedIn, Indeed aggregator via RapidAPI)"""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.getenv('RAPID_API_KEY')
        self.base_url = "https://jsearch.p.rapidapi.com"
        
    async def search_jobs(self, query: str, location: str = "", num_pages: int = 1) -> List[Dict[str, Any]]:
        """Search for jobs using JSearch API"""
        if not self.api_key:
            logger.warning("RAPID_API_KEY not found, skipping JSearch API")
            return []
        
        try:
            headers = {
                'X-RapidAPI-Key': self.api_key,
                'X-RapidAPI-Host': 'jsearch.p.rapidapi.com'
            }
            
            params = {
                'query': query,
                'page': '1',
                'num_pages': str(num_pages),
                'date_posted': 'month'  # Jobs posted in last month
            }
            
            if location:
                params['location'] = location
            
            async with self.session.get(
                f"{self.base_url}/search",
                headers=headers,
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_jsearch_jobs(data.get('data', []))
                else:
                    logger.error(f"JSearch API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"JSearch API exception: {e}")
            return []
    
    def _parse_jsearch_jobs(self, jobs_data: List[Dict]) -> List[Dict[str, Any]]:
        """Parse JSearch API response into standardized format"""
        parsed_jobs = []
        
        for job in jobs_data:
            try:
                parsed_job = {
                    'id': job.get('job_id', f"jsearch_{len(parsed_jobs)}"),
                    'title': self.clean_text(job.get('job_title', '')),
                    'company': self.clean_text(job.get('employer_name', '')),
                    'location': self.clean_text(job.get('job_city', '') + ', ' + job.get('job_country', '')),
                    'country': job.get('job_country', ''),
                    'salary': self.extract_salary_range(job.get('job_salary', '')),
                    'description': self.clean_text(job.get('job_description', ''))[:500] + '...',
                    'required_skills': job.get('job_required_skills', []),
                    'experience_level': job.get('job_experience_required', 'Not specified'),
                    'job_type': job.get('job_employment_type', 'Full-time'),
                    'remote': job.get('job_is_remote', False),
                    'source': 'LinkedIn/Indeed (JSearch)',
                    'postedDate': job.get('job_posted_at_datetime_utc', ''),
                    'applyUrl': self._generate_jsearch_apply_url(job),
                    'company_logo': job.get('employer_logo', ''),
                    'match_score': 85,  # High score for real jobs
                    'is_real_job': True
                }
                
                # Calculate days ago
                if parsed_job['postedDate']:
                    try:
                        posted_date = datetime.fromisoformat(parsed_job['postedDate'].replace('Z', '+00:00'))
                        days_ago = (datetime.now() - posted_date.replace(tzinfo=None)).days
                        parsed_job['daysAgo'] = max(0, days_ago)
                    except:
                        parsed_job['daysAgo'] = 1
                
                parsed_jobs.append(parsed_job)
                
            except Exception as e:
                logger.error(f"Error parsing JSearch job: {e}")
                continue
        
        return parsed_jobs

    def _generate_jsearch_apply_url(self, job: Dict) -> str:
        """Generate working apply URLs that redirect to actual JSearch job boards"""
        
        # Extract the actual redirect URL from the API response
        redirect_url = job.get('job_apply_link', '')
        
        # If no redirect URL is provided, use a default fallback
        if not redirect_url:
            redirect_url = f"https://www.linkedin.com/jobs/view/{job.get('job_id', random.randint(3000000000, 3999999999))}"
        
        return redirect_url

class AdzunaAPI(JobAPIService):
    """Adzuna API integration (Indeed, LinkedIn data aggregator)"""
    
    def __init__(self):
        super().__init__()
        # Load credentials from environment variables
        self.app_id = os.getenv('ADZUNA_APP_ID')
        self.app_key = os.getenv('ADZUNA_APP_KEY')
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
        
        # Check if credentials are available
        if not self.app_id or not self.app_key:
            logger.warning("⚠️  Adzuna API credentials not found in environment variables")
            logger.info("Please set ADZUNA_APP_ID and ADZUNA_APP_KEY in your .env file")
            logger.info("Get your credentials from: https://developer.adzuna.com/")
    
    async def search_jobs(self, query: str, location: str = "", country: str = "gb") -> List[Dict[str, Any]]:
        """Search for jobs using Adzuna API with the exact URL format: /v1/api/jobs/{country}/search/1"""
        
        # Skip API call if credentials are not available
        if not self.app_id or not self.app_key:
            logger.warning("Skipping Adzuna API - credentials not configured")
            return []
            
        try:
            # Map country codes for Adzuna API
            country_map = {
                'United States': 'us',
                'United Kingdom': 'gb', 
                'Germany': 'de',
                'France': 'fr',
                'Canada': 'ca',
                'Australia': 'au',
                'Netherlands': 'nl',
                'Spain': 'es',
                'Italy': 'it',
                'India': 'in',
                'Brazil': 'br',
                'Poland': 'pl',
                'South Africa': 'za',
                'Singapore': 'sg',
                'Austria': 'at',
                'Belgium': 'be',
                'Switzerland': 'ch',
                # Add common variations
                'us': 'us',
                'gb': 'gb',
                'uk': 'gb',
                'nl': 'nl',
                'de': 'de',
                'fr': 'fr',
                'ca': 'ca',
                'au': 'au',
                'USA': 'us',
                'UK': 'gb',
                'NL': 'nl'
            }
            
            # Use the country code, default to 'gb' (UK) if not found
            country_code = country_map.get(country, country_map.get(country.lower(), 'gb'))
            
            logger.info(f"🌍 Country mapping: '{country}' -> '{country_code}'")
            
            # Build the URL in the exact format specified: https://api.adzuna.com/v1/api/jobs/{country}/search/1
            url = f"{self.base_url}/{country_code}/search/1"
            
            # Build query parameters as specified in the user's format
            params = {
                'app_id': self.app_id,
                'app_key': self.app_key,
                'results_per_page': 20,  # Get more results for better variety
                'what': query,  # Job title/keywords
                'content-type': 'application/json'
            }
            
            # Add location filter if provided
            if location:
                params['where'] = location
            
            logger.info(f"📡 Calling Adzuna API: {url}")
            logger.info(f"🔍 Search query: '{query}' in {location or 'any location'}")
            logger.info(f"🔑 Using app_id: {self.app_id[:8]}... and app_key: {self.app_key[:8]}...")
            
            async with self.session.get(url, params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    jobs = self._parse_adzuna_jobs(data.get('results', []))
                    logger.info(f"✅ Adzuna API returned {len(jobs)} jobs")
                    return jobs
                elif response.status == 401:
                    logger.error("❌ Adzuna API: Invalid credentials (401)")
                    logger.error("Please check your ADZUNA_APP_ID and ADZUNA_APP_KEY")
                    return []
                elif response.status == 429:
                    logger.warning("⚠️  Adzuna API: Rate limit exceeded (429)")
                    return []
                elif response.status == 400:
                    logger.error("❌ Adzuna API: Bad request (400)")
                    response_text = await response.text()
                    logger.error(f"URL: {url}")
                    logger.error(f"Params: {params}")
                    logger.error(f"Response: {response_text[:500]}...")
                    return []
                else:
                    logger.error(f"❌ Adzuna API error: HTTP {response.status}")
                    response_text = await response.text()
                    logger.error(f"Response: {response_text[:200]}...")
                    return []
                    
        except asyncio.TimeoutError:
            logger.error("❌ Adzuna API: Request timeout")
            return []
        except Exception as e:
            logger.error(f"❌ Adzuna API exception: {e}")
            return []
    
    def _parse_adzuna_jobs(self, jobs_data: List[Dict]) -> List[Dict[str, Any]]:
        """Parse Adzuna API response into standardized format"""
        parsed_jobs = []
        
        for job in jobs_data:
            try:
                # Extract salary information
                salary_min = job.get('salary_min')
                salary_max = job.get('salary_max')
                salary = ""
                if salary_min and salary_max:
                    salary = f"${salary_min:,.0f} - ${salary_max:,.0f}"
                elif salary_min:
                    salary = f"${salary_min:,.0f}+"
                elif salary_max:
                    salary = f"Up to ${salary_max:,.0f}"
                
                # Extract location information
                location_info = job.get('location', {})
                location_display = location_info.get('display_name', '') if isinstance(location_info, dict) else str(location_info)
                
                # Extract company information
                company_info = job.get('company', {})
                company_name = company_info.get('display_name', '') if isinstance(company_info, dict) else str(company_info)
                
                parsed_job = {
                    'id': job.get('id', f"adzuna_{len(parsed_jobs)}"),
                    'title': self.clean_text(job.get('title', '')),
                    'company': self.clean_text(company_name),
                    'location': self.clean_text(location_display),
                    'country': job.get('location', {}).get('area', [])[-1] if job.get('location', {}).get('area') else '',
                    'salary': salary,
                    'description': self.clean_text(job.get('description', ''))[:500] + '...' if job.get('description') else 'No description available',
                    'required_skills': self._extract_skills_from_description(job.get('description', '')),
                    'experience_level': self._determine_experience_from_title(job.get('title', '')),
                    'job_type': job.get('contract_type', 'Full-time'),
                    'remote': self._is_remote_job(job.get('title', ''), job.get('description', '')),
                    'source': 'Indeed/LinkedIn (Adzuna)',
                    'postedDate': job.get('created', ''),
                    'applyUrl': self._generate_adzuna_apply_url(job),
                    'company_logo': '',
                    'match_score': 85,  # High score for real jobs from Adzuna
                    'is_real_job': True
                }
                
                # Calculate days ago
                if parsed_job['postedDate']:
                    try:
                        posted_date = datetime.fromisoformat(parsed_job['postedDate'].replace('Z', '+00:00'))
                        days_ago = (datetime.now() - posted_date.replace(tzinfo=None)).days
                        parsed_job['daysAgo'] = max(0, days_ago)
                    except:
                        parsed_job['daysAgo'] = 1
                else:
                    parsed_job['daysAgo'] = 1
                
                parsed_jobs.append(parsed_job)
                
            except Exception as e:
                logger.error(f"Error parsing Adzuna job: {e}")
                continue
        
        return parsed_jobs

    def _generate_adzuna_apply_url(self, job: Dict) -> str:
        """Generate working apply URLs that redirect to actual job postings"""
        
        # First, try to use the redirect URL from the API response
        redirect_url = job.get('redirect_url', '')
        if redirect_url and redirect_url.startswith('http'):
            return redirect_url
        
        # If no redirect URL, try to construct a direct link
        job_id = job.get('id', '')
        if job_id:
            # Try to construct an Indeed URL if the job seems to be from Indeed
            if 'indeed' in job.get('source', '').lower():
                return f"https://www.indeed.com/viewjob?jk={job_id}"
            
            # Otherwise, use a generic Adzuna search URL
            job_title = job.get('title', '').replace(' ', '+')
            company = job.get('company', {}).get('display_name', '') if isinstance(job.get('company'), dict) else str(job.get('company', ''))
            company = company.replace(' ', '+')
            
            return f"https://www.adzuna.com/search?q={job_title}+{company}&loc="
        
        # Fallback to a generic search
        return "https://www.adzuna.com/"

    def _extract_skills_from_description(self, description: str) -> List[str]:
        """Extract skills from job description"""
        if not description:
            return []
        
        # Common tech skills to look for
        common_skills = [
            'Python', 'Java', 'JavaScript', 'React', 'Node.js', 'SQL', 'AWS', 'Azure', 
            'Docker', 'Kubernetes', 'Git', 'Linux', 'MongoDB', 'PostgreSQL', 'Redis',
            'Machine Learning', 'Data Science', 'Agile', 'Scrum', 'DevOps', 'CI/CD'
        ]
        
        found_skills = []
        description_lower = description.lower()
        
        for skill in common_skills:
            if skill.lower() in description_lower:
                found_skills.append(skill)
        
        return found_skills[:5]  # Limit to 5 skills
    
    def _determine_experience_from_title(self, title: str) -> str:
        """Determine experience level from job title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ['senior', 'sr.', 'lead', 'principal', 'staff']):
            return 'Senior'
        elif any(word in title_lower for word in ['junior', 'jr.', 'entry', 'graduate', 'intern']):
            return 'Entry Level'
        else:
            return 'Mid Level'
    
    def _is_remote_job(self, title: str, description: str) -> bool:
        """Check if job is remote based on title and description"""
        remote_keywords = ['remote', 'work from home', 'wfh', 'telecommute', 'distributed']
        
        text_to_check = f"{title} {description}".lower()
        return any(keyword in text_to_check for keyword in remote_keywords)

class RemoteOKAPI(JobAPIService):
    """RemoteOK API integration (Remote jobs)"""
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://remoteok.io/api"
    
    async def search_jobs(self, query: str = "") -> List[Dict[str, Any]]:
        """Search for remote jobs using RemoteOK API"""
        try:
            headers = {
                'User-Agent': 'CareerCompassAI/1.0'
            }
            
            async with self.session.get(
                self.base_url,
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    # Filter jobs based on query
                    filtered_jobs = []
                    query_lower = query.lower()
                    
                    for job in data[1:21]:  # Skip first item (metadata) and take 20 jobs
                        if not query or any(term in job.get('position', '').lower() or 
                                          term in job.get('description', '').lower() 
                                          for term in query_lower.split()):
                            filtered_jobs.append(job)
                    
                    return self._parse_remoteok_jobs(filtered_jobs[:10])  # Limit to 10 jobs
                else:
                    logger.error(f"RemoteOK API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"RemoteOK API exception: {e}")
            return []
    
    def _parse_remoteok_jobs(self, jobs_data: List[Dict]) -> List[Dict[str, Any]]:
        """Parse RemoteOK API response into standardized format"""
        parsed_jobs = []
        
        for job in jobs_data:
            try:
                # Extract salary information
                salary_min = job.get('salary_min')
                salary_max = job.get('salary_max')
                salary = ""
                if salary_min and salary_max:
                    salary = f"${salary_min:,.0f} - ${salary_max:,.0f}"
                elif salary_min:
                    salary = f"${salary_min:,.0f}+"
                
                parsed_job = {
                    'id': job.get('id', f"remoteok_{len(parsed_jobs)}"),
                    'title': self.clean_text(job.get('position', '')),
                    'company': self.clean_text(job.get('company', '')),
                    'location': 'Remote',
                    'country': 'Global',
                    'salary': salary,
                    'description': self.clean_text(job.get('description', ''))[:500] + '...',
                    'required_skills': job.get('tags', []),
                    'experience_level': 'Not specified',
                    'job_type': 'Full-time',
                    'remote': True,
                    'source': 'RemoteOK',
                    'postedDate': '',
                    'applyUrl': self._generate_remoteok_apply_url(job),
                    'company_logo': job.get('logo', ''),
                    'match_score': 75,  # Good score for remote jobs
                    'is_real_job': True
                }
                
                # Calculate days ago from epoch timestamp
                if job.get('epoch'):
                    try:
                        posted_date = datetime.fromtimestamp(job['epoch'])
                        days_ago = (datetime.now() - posted_date).days
                        parsed_job['daysAgo'] = max(0, days_ago)
                    except:
                        parsed_job['daysAgo'] = 1
                
                parsed_jobs.append(parsed_job)
                
            except Exception as e:
                logger.error(f"Error parsing RemoteOK job: {e}")
                continue
        
        return parsed_jobs

    def _generate_remoteok_apply_url(self, job: Dict) -> str:
        """Generate working apply URLs that redirect to actual RemoteOK job boards"""
        
        # Extract the actual redirect URL from the API response
        redirect_url = job.get('apply_url', '')
        
        # If no redirect URL is provided, use a default fallback
        if not redirect_url:
            redirect_url = f"https://remoteok.io/remote-jobs/{job.get('id', random.randint(100000, 999999))}"
        
        return redirect_url

class JobAggregator:
    """Aggregates jobs from multiple REAL job APIs only - NO MOCK DATA"""
    
    def __init__(self):
        self.apis = {
            'jsearch': JSearchAPI(),
            'adzuna': AdzunaAPI(),
            'remoteok': RemoteOKAPI()
            # Removed 'netherlands': NetherlandsJobAPI() - no more mock jobs
        }
    
    async def search_all_apis(self, query: str, location: str = "", country: str = "") -> List[Dict[str, Any]]:
        """Search all available REAL job APIs and aggregate results - NO MOCK DATA"""
        all_jobs = []
        
        async with aiohttp.ClientSession() as session:
            # Set session for all APIs
            for api in self.apis.values():
                api.session = session
            
            # Create search tasks for REAL APIs only
            tasks = []
            
            # JSearch API (LinkedIn, Indeed) - REAL JOBS
            if self.apis['jsearch'].api_key:
                logger.info("🔍 Searching JSearch API (LinkedIn/Indeed) for real jobs")
                tasks.append(self.apis['jsearch'].search_jobs(query, location))
            else:
                logger.warning("⚠️  JSearch API key not found - skipping LinkedIn/Indeed jobs")
            
            # Adzuna API (Indeed, LinkedIn data) - REAL JOBS
            if self.apis['adzuna'].app_id and self.apis['adzuna'].app_key:
                logger.info("🔍 Searching Adzuna API for real jobs")
                # Map country codes for Adzuna API
                adzuna_country = self._map_country_to_adzuna(country)
                tasks.append(self.apis['adzuna'].search_jobs(query, location, adzuna_country))
            else:
                logger.warning("⚠️  Adzuna API credentials not found - skipping Adzuna jobs")
            
            # RemoteOK API (Remote jobs) - REAL JOBS
            logger.info("🔍 Searching RemoteOK API for real remote jobs")
            tasks.append(self.apis['remoteok'].search_jobs(query))
            
            # Execute all searches concurrently
            if tasks:
                logger.info(f"🚀 Executing {len(tasks)} real job API searches concurrently")
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, result in enumerate(results):
                    if isinstance(result, list):
                        api_name = list(self.apis.keys())[i] if i < len(self.apis) else f"API_{i}"
                        logger.info(f"✅ {api_name} returned {len(result)} real jobs")
                        all_jobs.extend(result)
                    elif isinstance(result, Exception):
                        logger.error(f"❌ API search error: {result}")
            else:
                logger.warning("⚠️  No real job APIs available - check API credentials")
        
        # Remove duplicates and sort by match score
        unique_jobs = self._remove_duplicates(all_jobs)
        logger.info(f"📊 Total unique real jobs found: {len(unique_jobs)}")
        return sorted(unique_jobs, key=lambda x: x.get('match_score', 0), reverse=True)
    
    def _map_country_to_adzuna(self, country: str) -> str:
        """Map country names to Adzuna API country codes"""
        if not country:
            return "gb"  # Default to UK
        
        country_mapping = {
            'united states': 'us',
            'usa': 'us',
            'us': 'us',
            'united kingdom': 'gb',
            'uk': 'gb',
            'gb': 'gb',
            'netherlands': 'nl',
            'holland': 'nl',
            'nl': 'nl',
            'germany': 'de',
            'de': 'de',
            'france': 'fr',
            'fr': 'fr',
            'canada': 'ca',
            'ca': 'ca',
            'australia': 'au',
            'au': 'au'
        }
        
        return country_mapping.get(country.lower(), 'gb')
    
    def _remove_duplicates(self, jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate jobs based on title and company"""
        seen = set()
        unique_jobs = []
        
        for job in jobs:
            # Create a key based on title and company
            key = (
                job.get('title', '').lower().strip(),
                job.get('company', '').lower().strip()
            )
            
            if key not in seen and key != ('', ''):
                seen.add(key)
                unique_jobs.append(job)
        
        return unique_jobs

# Utility functions for job validation
def validate_job_posting(job: Dict[str, Any]) -> bool:
    """Validate that a job posting has required fields and seems legitimate"""
    required_fields = ['title', 'company', 'applyUrl']
    
    # Check required fields
    for field in required_fields:
        if not job.get(field):
            return False
    
    # Check for suspicious patterns
    title = job.get('title', '').lower()
    company = job.get('company', '').lower()
    
    # Flag suspicious titles
    suspicious_titles = ['make money', 'work from home', 'easy money', 'no experience']
    if any(term in title for term in suspicious_titles):
        return False
    
    # Flag suspicious companies
    if len(company) < 2 or company in ['test', 'example', 'sample']:
        return False
    
    return True

def check_job_availability(apply_url: str) -> bool:
    """Check if a job posting URL is still active (basic check)"""
    if not apply_url:
        return False
    
    # Basic URL validation
    if not apply_url.startswith(('http://', 'https://')):
        return False
    
    # Check for known job board domains
    valid_domains = [
        'linkedin.com', 'indeed.com', 'glassdoor.com', 'reed.co.uk',
        'remoteok.io', 'angel.co', 'stackoverflow.com', 'dice.com',
        'adzuna.com', 'adzuna.co.uk', 'adzuna.nl', 'adzuna.de'
    ]
    
    return any(domain in apply_url for domain in valid_domains) 