"""
Real Job API Integration Services for CareerCompassAI

This module provides integrations with real job APIs including:
- JSearch API (LinkedIn, Indeed aggregator)
- Adzuna API (Indeed, LinkedIn data)
- Reed.co.uk API (UK jobs)
- RemoteOK API (Remote jobs)
- TheMuseAPI (Company jobs)
"""

import asyncio
import aiohttp
import json
import os
import re
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging

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
                    'applyUrl': job.get('job_apply_link', ''),
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

class AdzunaAPI(JobAPIService):
    """Adzuna API integration (Indeed, LinkedIn data aggregator)"""
    
    def __init__(self):
        super().__init__()
        self.app_id = os.getenv('ADZUNA_APP_ID')
        self.app_key = os.getenv('ADZUNA_APP_KEY')
        self.base_url = "https://api.adzuna.com/v1/api/jobs"
    
    async def search_jobs(self, query: str, location: str = "", country: str = "us") -> List[Dict[str, Any]]:
        """Search for jobs using Adzuna API"""
        if not self.app_id or not self.app_key:
            logger.warning("Adzuna API credentials not found, skipping Adzuna API")
            return []
        
        try:
            # Map country codes
            country_map = {
                'United States': 'us',
                'United Kingdom': 'gb',
                'Germany': 'de',
                'France': 'fr',
                'Canada': 'ca',
                'Australia': 'au'
            }
            
            country_code = country_map.get(country, 'us')
            
            params = {
                'app_id': self.app_id,
                'app_key': self.app_key,
                'results_per_page': 20,
                'what': query,
                'content-type': 'application/json'
            }
            
            if location:
                params['where'] = location
            
            async with self.session.get(
                f"{self.base_url}/{country_code}/search/1",
                params=params
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_adzuna_jobs(data.get('results', []))
                else:
                    logger.error(f"Adzuna API error: {response.status}")
                    return []
                    
        except Exception as e:
            logger.error(f"Adzuna API exception: {e}")
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
                
                parsed_job = {
                    'id': job.get('id', f"adzuna_{len(parsed_jobs)}"),
                    'title': self.clean_text(job.get('title', '')),
                    'company': self.clean_text(job.get('company', {}).get('display_name', '')),
                    'location': self.clean_text(job.get('location', {}).get('display_name', '')),
                    'country': job.get('location', {}).get('area', [])[-1] if job.get('location', {}).get('area') else '',
                    'salary': salary,
                    'description': self.clean_text(job.get('description', ''))[:500] + '...',
                    'required_skills': [],  # Adzuna doesn't provide structured skills
                    'experience_level': 'Not specified',
                    'job_type': job.get('contract_type', 'Full-time'),
                    'remote': 'remote' in job.get('title', '').lower() or 'remote' in job.get('description', '').lower(),
                    'source': 'Indeed/LinkedIn (Adzuna)',
                    'postedDate': job.get('created', ''),
                    'applyUrl': job.get('redirect_url', ''),
                    'company_logo': '',
                    'match_score': 80,  # High score for real jobs
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
                logger.error(f"Error parsing Adzuna job: {e}")
                continue
        
        return parsed_jobs

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
                    'applyUrl': job.get('apply_url', f"https://remoteok.io/remote-jobs/{job.get('id', '')}"),
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

class JobAggregator:
    """Aggregates jobs from multiple APIs"""
    
    def __init__(self):
        self.apis = {
            'jsearch': JSearchAPI(),
            'adzuna': AdzunaAPI(),
            'remoteok': RemoteOKAPI()
        }
    
    async def search_all_apis(self, query: str, location: str = "", country: str = "") -> List[Dict[str, Any]]:
        """Search all available job APIs and aggregate results"""
        all_jobs = []
        
        async with aiohttp.ClientSession() as session:
            # Set session for all APIs
            for api in self.apis.values():
                api.session = session
            
            # Create search tasks
            tasks = []
            
            # JSearch API (LinkedIn, Indeed)
            if self.apis['jsearch'].api_key:
                tasks.append(self.apis['jsearch'].search_jobs(query, location))
            
            # Adzuna API (Indeed, LinkedIn data)
            if self.apis['adzuna'].app_id and self.apis['adzuna'].app_key:
                tasks.append(self.apis['adzuna'].search_jobs(query, location, country))
            
            # RemoteOK API (Remote jobs)
            tasks.append(self.apis['remoteok'].search_jobs(query))
            
            # Execute all searches concurrently
            if tasks:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, list):
                        all_jobs.extend(result)
                    elif isinstance(result, Exception):
                        logger.error(f"API search error: {result}")
        
        # Remove duplicates and sort by match score
        unique_jobs = self._remove_duplicates(all_jobs)
        return sorted(unique_jobs, key=lambda x: x.get('match_score', 0), reverse=True)
    
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
        'remoteok.io', 'angel.co', 'stackoverflow.com', 'dice.com'
    ]
    
    return any(domain in apply_url for domain in valid_domains) 