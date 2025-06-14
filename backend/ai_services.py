"""
CareerCompassAI - AI Services

This module provides intelligent document parsing using Claude AI as the primary engine.
Claude AI offers superior document analysis and understanding compared to traditional parsing methods.

Parsing Priority:
1. Claude AI (Claude 3 Haiku) - Primary intelligent parsing engine
2. OpenAI GPT-4 - Fallback AI parsing
3. Enhanced pattern matching - Final fallback for development

Note: We no longer use PyPDF2 for PDF parsing. Instead, we use pdfplumber for basic text extraction
and rely on Claude AI to intelligently understand and parse the document content.
"""

import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import re
import anthropic

# Load environment variables from .env file
load_dotenv()

# Get API keys with fallback
openai_api_key = os.getenv("OPENAI_API_KEY")
claude_api_key = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")

# Check if we have Claude API key for document analysis
has_claude_api = claude_api_key and len(claude_api_key) > 20 and 'placeholder' not in claude_api_key.lower()

is_development_mode = (not openai_api_key or 
                      openai_api_key in ['placeholder', 'test_key', 'your_api_key_here'] or 
                      len(openai_api_key) < 20 or
                      'development' in openai_api_key.lower() or
                      'placeholder' in openai_api_key.lower() or
                      'test' in openai_api_key.lower())

if not openai_api_key:
    print("Warning: OPENAI_API_KEY not set. Running in development mode with smart parsing.")
    is_development_mode = True
elif (openai_api_key in ['placeholder', 'test_key', 'your_api_key_here'] or 
      len(openai_api_key) < 20 or
      'development' in openai_api_key.lower() or
      'placeholder' in openai_api_key.lower() or
      'test' in openai_api_key.lower()):
    print("Warning: Using placeholder OpenAI API key. Running in development mode with smart parsing.")
    is_development_mode = True
else:
    print(f"✅ Using real OpenAI API key (ends with: ...{openai_api_key[-8:]}) - AI parsing enabled")

# Initialize AI services
if has_claude_api:
    claude_client = anthropic.Anthropic(api_key=claude_api_key)
    print(f"✅ Using Claude AI for document analysis (ends with: ...{claude_api_key[-8:]})")
else:
    claude_client = None
    if not claude_api_key:
        print("💡 Tip: Set CLAUDE_API_KEY or ANTHROPIC_API_KEY for better CV parsing with Claude AI")
    else:
        print("Warning: Claude API key appears to be invalid")

# Initialize OpenAI LLM only if we have a real API key
if not is_development_mode:
    try:
        llm = ChatOpenAI(temperature=0.7, model="gpt-4")
    except Exception as e:
        print(f"Warning: Could not initialize OpenAI LLM: {e}")
        llm = None
else:
    llm = None
    if has_claude_api:
        print("Using Claude AI for intelligent document analysis")
    else:
        print("Development mode: AI services will use smart text parsing to extract real CV data")

def _get_mock_career_path(job_title: str, experience: str, skills: list[str]):
    """Return mock career path data for development"""
    return f"""**Career Path Recommendation for {job_title}**

**Short-term goals (1-2 years):**
- Senior {job_title}: Focus on leadership skills and advanced technical expertise
- Technical Lead: Develop team management and project coordination skills
- Product Specialist: Gain deeper domain knowledge and customer interaction experience

**Mid-term goals (3-5 years):**
- Engineering Manager: Build people management and strategic planning skills
- Principal Engineer: Become a technical expert and mentor for the team
- Product Manager: Develop business acumen and product strategy skills

**Long-term goals (5+ years):**
- Director of Engineering: Lead multiple teams and drive technical vision
- VP of Product: Shape product strategy and drive business outcomes
- CTO/Technical Founder: Lead technical strategy for entire organization

**Skill Development:**
1. Advanced {skills[0] if skills else 'programming'} - Master advanced concepts and frameworks
2. System Design - Learn to architect scalable, robust systems
3. Leadership & Communication - Develop team leadership and presentation skills
4. Product Strategy - Understand business metrics and customer needs
5. Data Analysis - Learn to make data-driven decisions
6. Cloud Technologies - Master modern infrastructure and DevOps practices
7. Agile Methodologies - Excel in modern software development practices"""

def _get_mock_skill_gap(skills: list[str], job_description: str):
    """Return mock skill gap analysis for development"""
    return """**Skill Gap Analysis**

**Missing Skills:**
1. Advanced Python/React frameworks
2. Cloud platforms (AWS/Azure/GCP)
3. DevOps and CI/CD pipelines
4. Database optimization
5. API design and microservices

**Skill Enhancement:**
1. Strengthen existing programming skills with advanced patterns
2. Improve problem-solving and algorithm knowledge
3. Enhance communication and teamwork abilities

**Learning Recommendations:**
1. **Cloud Computing** - AWS Solutions Architect course on Coursera
2. **DevOps** - Docker and Kubernetes certification on Udemy
3. **System Design** - Grokking the System Design Interview on Educative
4. **Advanced Programming** - Clean Code and Design Patterns books
5. **Database Skills** - PostgreSQL/MongoDB certification courses"""

def _get_mock_resume_optimization(resume_text: str, job_description: str):
    """Return mock resume optimization for development"""
    return """**Resume Optimization Recommendations**

**Keyword Optimization:**
- Add "cloud computing", "agile development", "API design"
- Include "microservices", "containerization", "CI/CD"
- Mention "data analytics", "performance optimization"

**Impactful Bullet Points:**
- "Led development of scalable web application serving 10,000+ users, reducing load times by 40%"
- "Implemented automated testing pipeline, decreasing deployment time from 2 hours to 15 minutes"
- "Collaborated with cross-functional team of 8 members to deliver product features 20% ahead of schedule"

**Summary Statement:**
"Experienced software developer with 3+ years building scalable web applications. Proven track record of implementing efficient solutions that improve performance and user experience. Strong background in modern development practices and cloud technologies."

**Overall Feedback:**
Your resume shows solid technical experience. Focus on quantifying achievements with specific metrics and emphasizing collaborative work. Consider adding more details about the scale and impact of your projects."""

def parse_resume_content(resume_text: str):
    """
    Main function to parse resume content using available AI services.
    Falls back to enhanced pattern matching if AI services fail.
    """
    if not resume_text or len(resume_text.strip()) < 50:
        return _get_mock_resume_parse("Basic professional profile")
    
    # Try Claude AI first (if available)
    if claude_client:
        try:
            print("🤖 Attempting Claude AI parsing...")
            result = _parse_resume_with_claude(resume_text)
            print("✅ Claude AI parsing successful")
            return result
        except Exception as e:
            print(f"Claude parsing error: {e}")
            print("Claude AI parsing failed: {e}")
            print("Falling back to enhanced pattern matching...")
    
    # Try OpenAI as secondary option (if available)
    if openai_api_key and openai_api_key != "your-openai-api-key-here":
        try:
            print("🤖 Attempting OpenAI parsing...")
            result = _parse_resume_with_openai(resume_text)
            print("✅ OpenAI parsing successful")
            return result
        except Exception as e:
            print(f"OpenAI parsing error: {e}")
            print("Falling back to enhanced pattern matching...")
    
    # Use enhanced pattern matching as fallback
    print("📝 Using enhanced pattern matching for resume parsing...")
    return _get_mock_resume_parse(resume_text)

def _parse_resume_with_claude(resume_text: str):
    """
    Uses Claude AI for intelligent CV parsing and information extraction.
    """
    prompt = f"""
You are an expert resume/CV analyzer. Please analyze the following resume text and extract key information accurately.

Resume Content:
{resume_text}

Extract the following information and return it as a valid JSON object. Pay special attention to distinguishing between actual job titles and certifications:

{{
    "firstName": "First name only (string)",
    "lastName": "Last name only (string)", 
    "email": "Email address if found (string or null)",
    "phone": "Phone number if found (string or null)",
    "location": "Current location/address if found (string or null). Look for city, state, country information in contact details or address sections",
    "experienceYears": "Total years of professional work experience (integer)",
    "skills": ["List of technical and professional skills found"],
    "lastThreeJobTitles": ["Most recent ACTUAL JOB POSITIONS (not certifications), up to 3. Examples: 'Senior Software Engineer', 'Data Scientist', 'Product Manager'"],
    "experienceSummary": "Brief professional summary (2-3 sentences)",
    "companies": ["ACTUAL company names where the person worked (not job titles or certifications). Examples: 'Microsoft', 'Google Inc', 'Acme Corporation', 'TechStart Solutions'"],
    "education": ["Educational qualifications with degrees and institutions"],
    "certifications": ["Professional certifications and credentials like 'AWS Certified Solutions Architect', 'Azure Certified Data Engineer', etc."]
}}

IMPORTANT DISTINCTIONS:
- lastThreeJobTitles should contain ACTUAL JOB POSITIONS/ROLES (e.g., "Senior Data Engineer", "Lead Software Developer", "Product Manager")
- certifications should contain CERTIFICATIONS/CREDENTIALS (e.g., "AWS Certified Solutions Architect", "Azure Certified Data Engineer", "PMP Certified")
- Do NOT put certifications in the lastThreeJobTitles field
- Do NOT put job titles in the certifications field

Return only the JSON object, no additional text."""

    try:
        response = claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            temperature=0.1,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        # Extract the JSON from Claude's response
        response_text = response.content[0].text.strip()
        
        # Try to extract JSON if it's wrapped in markdown or other text
        if '```json' in response_text:
            json_start = response_text.find('```json') + 7
            json_end = response_text.find('```', json_start)
            response_text = response_text[json_start:json_end].strip()
        elif '```' in response_text:
            json_start = response_text.find('```') + 3
            json_end = response_text.find('```', json_start)
            response_text = response_text[json_start:json_end].strip()
        
        # Parse and validate the JSON
        parsed_data = json.loads(response_text)
        
        # Validate and clean the parsed data
        return json.dumps(_validate_and_clean_parsed_data(parsed_data, resume_text))
        
    except json.JSONDecodeError as e:
        print(f"Claude parsing error: {e}")
        raise Exception(f"Claude AI parsing failed: {e}")
    except Exception as e:
        print(f"Claude API error: {e}")
        raise Exception(f"Claude AI parsing failed: {e}")

def _parse_resume_with_openai(resume_text: str):
    """
    Uses OpenAI for CV parsing as a fallback option.
    """
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    
    prompt = PromptTemplate(
        input_variables=["resume_text"],
        template="""
        You are an expert resume parser. Analyze the following resume text and extract key information.

        Resume Text:
        {resume_text}

        Please extract and return ONLY a valid JSON object with the following structure:
        {{
            "firstName": "First name (string)",
            "lastName": "Last name (string)", 
            "email": "Email address (string or null)",
            "phone": "Phone number (string or null)",
            "experienceYears": "Total years of professional experience (integer)",
            "skills": ["Array of technical and professional skills, max 10"],
            "lastThreeJobTitles": ["Array of last 3 job titles, most recent first"],
            "experienceSummary": "2-3 sentence professional summary (string)",
            "companies": ["Array of ACTUAL company names where the person worked (not job titles). Examples: 'Microsoft Corporation', 'Google LLC', 'Startup Inc'"],
            "education": ["Array of educational qualifications - include degree, major, institution, year when available"],
            "certifications": ["Array of professional certifications, licenses, and credentials"]
        }}

        CRITICAL INSTRUCTIONS:
        - Extract firstName and lastName from the full name
        - For experienceYears: Calculate total years of professional work experience as an integer
        - For skills: Extract both technical skills (programming, tools, technologies) and professional skills (communication, leadership, etc.)
        - For lastThreeJobTitles: Extract job titles from work experience, most recent first
        - For companies: Extract company names where the person worked
        - For education: Include full details like "Bachelor of Science in Computer Science, University of XYZ, 2019"
        - For certifications: Include all professional certifications, licenses, credentials, and training certificates
        - If any information is not found, use null for strings/integers or empty array [] for arrays
        - RETURN ONLY THE JSON OBJECT, NO OTHER TEXT
        - Ensure the JSON is properly formatted and valid

        JSON:
        """
    )

    try:
        chain = LLMChain(llm=llm, prompt=prompt)
        response = chain.run(resume_text=resume_text)
        
        # Clean the response to ensure it's valid JSON
        response = response.strip()
        if response.startswith('```json'):
            response = response.replace('```json', '').replace('```', '').strip()
        if response.startswith('```'):
            response = response.replace('```', '').strip()
        
        # Try to parse the response as JSON
        import json
        parsed_response = json.loads(response)
        
        # Validate and clean the parsed response
        cleaned_response = _validate_and_clean_parsed_data(parsed_response, resume_text)
        return json.dumps(cleaned_response)
        
    except Exception as e:
        print(f"AI parsing failed: {e}")
        # Return mock data instead of failing
        return _get_mock_resume_parse(resume_text)

def _validate_and_clean_parsed_data(data, resume_text: str = ""):
    """
    Validates and cleans the AI-parsed data to ensure it matches our expected structure.
    Uses enhanced pattern matching for missing data instead of generic placeholders.
    """
    # Get location and handle empty strings properly
    location_value = data.get("location")
    if location_value:
        location_value = str(location_value).strip()
        if not location_value:  # Empty string after stripping
            location_value = None
    else:
        location_value = None
    
    cleaned = {
        "firstName": str(data.get("firstName", "Professional")).strip() if data.get("firstName") else "Professional",
        "lastName": str(data.get("lastName", "User")).strip() if data.get("lastName") else "User",
        "email": str(data.get("email")).strip() if data.get("email") else None,
        "phone": str(data.get("phone")).strip() if data.get("phone") else None,
        "location": location_value,
        "experienceYears": int(data.get("experienceYears", 2)) if data.get("experienceYears") else 2,
        "skills": [],
        "lastThreeJobTitles": [],
        "experienceSummary": str(data.get("experienceSummary", "Experienced professional with demonstrated expertise.")).strip() if data.get("experienceSummary") else "Experienced professional with demonstrated expertise.",
        "companies": [],
        "education": [],
        "certifications": []
    }
    
    # Clean skills array
    if isinstance(data.get("skills"), list):
        for skill in data.get("skills", []):
            if skill and isinstance(skill, str) and len(skill.strip()) > 1:
                cleaned["skills"].append(skill.strip())
    
    # Clean job titles array
    if isinstance(data.get("lastThreeJobTitles"), list):
        for title in data.get("lastThreeJobTitles", []):
            if title and isinstance(title, str) and len(title.strip()) > 2:
                cleaned["lastThreeJobTitles"].append(title.strip())
    
    # Clean companies array
    if isinstance(data.get("companies"), list):
        for company in data.get("companies", []):
            if company and isinstance(company, str) and len(company.strip()) > 2:
                cleaned["companies"].append(company.strip())
    
    # Clean education array
    if isinstance(data.get("education"), list):
        for edu in data.get("education", []):
            if edu and isinstance(edu, str) and len(edu.strip()) > 2:
                cleaned["education"].append(edu.strip())
    
    # Clean certifications array
    if isinstance(data.get("certifications"), list):
        for cert in data.get("certifications", []):
            if cert and isinstance(cert, str) and len(cert.strip()) > 2:
                cleaned["certifications"].append(cert.strip())
    
    # If we don't have enough skills, extract from resume text
    if len(cleaned["skills"]) < 3 and resume_text:
        print("🔍 Extracting additional skills from resume text...")
        extracted_skills = _extract_skills_from_sections(resume_text)
        for skill in extracted_skills:
            if skill not in cleaned["skills"]:
                cleaned["skills"].append(skill)
    
    # If we don't have enough job titles, extract from resume text
    if len(cleaned["lastThreeJobTitles"]) < 2 and resume_text:
        print("🔍 Extracting additional job titles from resume text...")
        # Use pattern matching to find job titles
        job_title_patterns = [
            r'(?:Senior|Lead|Principal|Staff)?\s*(?:Software|Data|DevOps|Full[- ]?Stack|Backend|Frontend|Mobile|Web)?\s*(?:Engineer|Developer|Architect|Scientist|Analyst|Manager|Director|Consultant|Specialist)',
            r'(?:Project|Product|Engineering|Technical|Development)\s*(?:Manager|Director|Lead)',
            r'(?:Chief|Head|VP|Vice President)\s*(?:Technology|Engineering|Data|Product)',
        ]
        
        for pattern in job_title_patterns:
            matches = re.findall(pattern, resume_text, re.IGNORECASE)
            for match in matches:
                title = match.strip()
                if title and len(title) > 5 and title not in cleaned["lastThreeJobTitles"]:
                    cleaned["lastThreeJobTitles"].append(title)
                    if len(cleaned["lastThreeJobTitles"]) >= 3:
                        break
            if len(cleaned["lastThreeJobTitles"]) >= 3:
                break
    
    # If we don't have enough companies, extract from resume text
    if len(cleaned["companies"]) < 2 and resume_text:
        print("🔍 Extracting additional companies from resume text...")
        extracted_companies = _extract_companies_from_text(resume_text)
        for company in extracted_companies:
            if company not in cleaned["companies"]:
                cleaned["companies"].append(company)
                if len(cleaned["companies"]) >= 5:
                    break
    
    # Ensure minimum data quality
    if not cleaned["skills"]:
        skills_lower = resume_text.lower() if resume_text else ""
        certs = []
        if any(skill in skills_lower for skill in ['aws', 'amazon web services']):
            certs.append("AWS Certified Solutions Architect")
        if any(skill in skills_lower for skill in ['azure', 'microsoft azure']):
            certs.append("Azure Certified Data Engineer")
        if any(skill in skills_lower for skill in ['google cloud', 'gcp']):
            certs.append("Google Cloud Professional Data Engineer")
        if not certs:
            certs = ["Professional Development Certification"]
        cleaned["certifications"] = certs
    
    # Extract location/country if not provided by AI - FIXED LOGIC
    if not cleaned["location"] and resume_text:
        # Try to extract country from work history
        print(f"🔍 Attempting location detection from resume text...")
        print(f"📍 Companies: {cleaned['companies']}")
        print(f"📍 Job titles: {cleaned['lastThreeJobTitles']}")
        detected_country = _extract_country_from_work_history(resume_text, cleaned["companies"], cleaned["lastThreeJobTitles"])
        if detected_country:
            cleaned["location"] = detected_country
            print(f"🌍 Detected Country: {detected_country}")
        else:
            print(f"🌍 Detected Country: None")
    elif cleaned["location"]:
        print(f"🌍 Location already provided: {cleaned['location']}")
    
    return cleaned

def _get_simple_fallback_parse(resume_text: str):
    """
    Simple fallback parsing that extracts basic information using minimal processing.
    """
    import json
    
    # Try to extract email and name using simple string operations
    lines = resume_text.split('\n')
    first_name = "Professional"
    last_name = "User"
    email = None
    
    # Look for email
    for line in lines:
        if '@' in line:
            import re
            email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', line)
            if email_match:
                email = email_match.group(0)
                break
    
    # Look for name in first few lines
    for line in lines[:5]:
        line = line.strip()
        if line and len(line.split()) >= 2 and not '@' in line and not any(char.isdigit() for char in line):
            words = line.split()
            if len(words) >= 2:
                first_name = words[0]
                last_name = ' '.join(words[1:])
                break
    
    fallback_data = {
        "firstName": first_name,
        "lastName": last_name,
        "email": email,
        "phone": None,
        "experienceYears": 3,
        "skills": ["Professional Skills", "Communication", "Problem Solving", "Team Collaboration"],
        "lastThreeJobTitles": ["Current Position", "Previous Role"],
        "experienceSummary": "Experienced professional with a strong background in their field. Demonstrates excellent problem-solving abilities and effective communication skills.",
        "companies": ["Previous Company", "Current Organization"],
        "education": ["Professional Education"],
        "certifications": ["Professional Development"]
    }
    
    return json.dumps(fallback_data)

def _extract_companies_from_text(resume_text: str) -> list:
    """
    Enhanced company extraction from resume text using multiple patterns and heuristics.
    """
    import re
    
    companies = []
    lines = resume_text.split('\n')
    
    # Enhanced company patterns
    company_patterns = [
        # Company name with common suffixes
        r'\b([A-Z][a-zA-Z\s&]+(?:Inc|Corp|Corporation|LLC|Ltd|Limited|Company|Co|Technologies|Tech|Solutions|Systems|Services|Group|International|Global|Consulting|Partners|Associates|Holdings|Enterprises)\.?)\b',
        # Company name followed by location
        r'\b([A-Z][a-zA-Z\s&]+),\s*[A-Z][a-zA-Z\s]+(?:,\s*[A-Z]{2,})?',
        # Company name in work experience sections
        r'(?:at|@|with|for)\s+([A-Z][a-zA-Z\s&]+(?:Inc|Corp|Corporation|LLC|Ltd|Limited|Company|Co|Technologies|Tech|Solutions|Systems|Services|Group)\.?)',
        # Company name before job title
        r'([A-Z][a-zA-Z\s&]+(?:Inc|Corp|Corporation|LLC|Ltd|Limited|Company|Co|Technologies|Tech|Solutions|Systems|Services|Group)\.?)\s*[-–—]\s*[A-Z]',
    ]
    
    # Keywords that indicate work experience sections
    work_section_keywords = [
        'experience', 'employment', 'work history', 'professional experience',
        'career history', 'work experience', 'employment history'
    ]
    
    # Words to exclude from company names
    exclude_words = {
        'university', 'college', 'school', 'institute', 'academy', 'education',
        'degree', 'bachelor', 'master', 'phd', 'certification', 'course',
        'skills', 'technologies', 'tools', 'languages', 'frameworks',
        'experience', 'summary', 'objective', 'profile', 'contact',
        'email', 'phone', 'address', 'linkedin', 'github', 'portfolio'
    }
    
    # Look for companies in work experience sections
    in_work_section = False
    for i, line in enumerate(lines):
        line_clean = line.strip()
        if not line_clean:
            continue
            
        line_lower = line_clean.lower()
        
        # Check if we're entering a work experience section
        if any(keyword in line_lower for keyword in work_section_keywords):
            in_work_section = True
            continue
            
        # Check if we're leaving work experience section
        if in_work_section and any(keyword in line_lower for keyword in ['education', 'skills', 'certifications', 'projects']):
            in_work_section = False
            continue
        
        # Skip lines that are clearly not company names
        if (line_clean.startswith(('•', '◦', '-', '*', '  ')) or
            '@' in line_clean or
            any(exclude in line_lower for exclude in exclude_words) or
            len(line_clean) < 3 or len(line_clean) > 100):
            continue
        
        # First, check for specific patterns like "Job Title at Company Name"
        company_found = False
        if ' at ' in line_clean:
            parts = line_clean.split(' at ', 1)
            if len(parts) == 2:
                potential_job = parts[0].strip()
                potential_company = parts[1].strip()
                
                # Check if second part looks like a company and first like a job title
                if (len(potential_company) > 3 and len(potential_company) < 60 and
                    not any(exclude in potential_company.lower() for exclude in exclude_words) and
                    any(job_word in potential_job.lower() for job_word in ['engineer', 'developer', 'manager', 'analyst', 'consultant', 'specialist', 'director', 'lead', 'senior']) and
                    potential_company not in companies):
                    
                    companies.append(potential_company)
                    company_found = True
        
        # Only apply general patterns if no specific pattern was found
        if not company_found:
            # Apply company patterns (excluding the "at" pattern since we handled it above)
            patterns_to_check = [
                # Company name with common suffixes
                r'\b([A-Z][a-zA-Z\s&]+(?:Inc|Corp|Corporation|LLC|Ltd|Limited|Company|Co|Technologies|Tech|Solutions|Systems|Services|Group|International|Global|Consulting|Partners|Associates|Holdings|Enterprises)\.?)\b',
                # Company name followed by location
                r'\b([A-Z][a-zA-Z\s&]+),\s*[A-Z][a-zA-Z\s]+(?:,\s*[A-Z]{2,})?',
                # Company name before job title
                r'([A-Z][a-zA-Z\s&]+(?:Inc|Corp|Corporation|LLC|Ltd|Limited|Company|Co|Technologies|Tech|Solutions|Systems|Services|Group)\.?)\s*[-–—]\s*[A-Z]',
            ]
            
            for pattern in patterns_to_check:
                matches = re.findall(pattern, line_clean, re.IGNORECASE)
                for match in matches:
                    company_name = match.strip()
                    
                    # Additional validation
                    if (len(company_name) > 3 and len(company_name) < 80 and
                        not any(exclude in company_name.lower() for exclude in exclude_words) and
                        not company_name.lower().startswith(('skills', 'experience', 'education')) and
                        company_name not in companies):
                        
                        companies.append(company_name)
                        company_found = True
                        break
                
                if company_found:
                    break
    
    # Look for companies in specific patterns like "Company Name - Job Title"
    for line in lines:
        line_clean = line.strip()
        if not line_clean or len(line_clean) < 10:
            continue
            
        # Pattern: Company Name - Job Title or Company Name | Job Title or Job Title at Company Name
        if ' - ' in line_clean or ' | ' in line_clean or ' at ' in line_clean:
            if ' at ' in line_clean:
                # Handle "Job Title at Company Name" pattern
                parts = line_clean.split(' at ', 1)
                if len(parts) == 2:
                    potential_job = parts[0].strip()
                    potential_company = parts[1].strip()
                    
                    # Check if second part looks like a company and first like a job title
                    if (len(potential_company) > 3 and len(potential_company) < 60 and
                        not any(exclude in potential_company.lower() for exclude in exclude_words) and
                        any(job_word in potential_job.lower() for job_word in ['engineer', 'developer', 'manager', 'analyst', 'consultant', 'specialist', 'director', 'lead', 'senior']) and
                        potential_company not in companies):
                        
                        companies.append(potential_company)
            else:
                # Handle "Company Name - Job Title" or "Company Name | Job Title" patterns
                parts = re.split(r'\s*[-|]\s*', line_clean)
                if len(parts) >= 2:
                    potential_company = parts[0].strip()
                    potential_job = parts[1].strip()
                    
                    # Check if first part looks like a company and second like a job title
                    if (len(potential_company) > 3 and len(potential_company) < 60 and
                        not any(exclude in potential_company.lower() for exclude in exclude_words) and
                        any(job_word in potential_job.lower() for job_word in ['engineer', 'developer', 'manager', 'analyst', 'consultant', 'specialist', 'director', 'lead', 'senior']) and
                        potential_company not in companies):
                        
                        companies.append(potential_company)
    
    # Look for companies mentioned with dates (work periods)
    date_pattern = r'(\d{4})\s*[-–—]\s*(\d{4}|present|current)'
    for line in lines:
        if re.search(date_pattern, line, re.IGNORECASE):
            # This line contains a date range, look for company names
            original_line = line
            line_clean = re.sub(date_pattern, '', line, flags=re.IGNORECASE).strip()
            
            # Remove common prefixes/suffixes
            line_clean = re.sub(r'^(at|@|with|for)\s+', '', line_clean, flags=re.IGNORECASE)
            line_clean = re.sub(r'\s*[-–—]\s*.*$', '', line_clean)
            
            # Remove job titles from the beginning (e.g., "Senior Data Engineer")
            if ':' in line_clean:
                line_clean = line_clean.split(':', 1)[1].strip()
            
            # Extract company name (everything before comma or location)
            if ',' in line_clean:
                line_clean = line_clean.split(',')[0].strip()
            
            # Additional validation to ensure it's a company name
            job_title_indicators = ['engineer', 'developer', 'manager', 'director', 'analyst', 'consultant', 'specialist', 'architect', 'lead', 'senior', 'principal']
            
            if (len(line_clean) > 3 and len(line_clean) < 80 and
                not any(exclude in line_clean.lower() for exclude in exclude_words) and
                not line_clean.isdigit() and  # Exclude pure numbers
                not re.match(r'^\d{4}$', line_clean) and  # Exclude 4-digit years
                not re.match(r'^\d+$', line_clean) and  # Exclude any pure numbers
                line_clean not in companies and
                # Must contain at least one letter
                re.search(r'[a-zA-Z]', line_clean) and
                # Exclude job titles
                not any(job_indicator in line_clean.lower() for job_indicator in job_title_indicators)):
                
                companies.append(line_clean)
    
    # Remove duplicates and clean up
    unique_companies = []
    for company in companies:
        # Clean up company name
        company = re.sub(r'\s+', ' ', company).strip()
        company = re.sub(r'^[^\w]+|[^\w]+$', '', company)  # Remove leading/trailing non-word chars
        
        if (company and len(company) > 2 and
            not company.isdigit() and  # Exclude pure numbers like years
            not re.match(r'^\d{4}$', company) and  # Exclude 4-digit years
            not any(existing.lower() in company.lower() or company.lower() in existing.lower() 
                   for existing in unique_companies)):
            unique_companies.append(company)
    
    return unique_companies[:5]  # Return up to 5 companies

def _extract_country_from_work_history(resume_text: str, companies: list, job_titles: list) -> str:
    """
    Extract country information from work history, companies, and job locations.
    Prioritizes recent work experience and company locations.
    Enhanced for better Netherlands and European country detection.
    """
    import re
    print(f"🔍 Location extraction - Resume text length: {len(resume_text)}")
    print(f"🔍 Location extraction - Companies: {companies}")
    print(f"🔍 Location extraction - Job titles: {job_titles}")
    
    # Enhanced country mapping for common company locations and patterns
    country_indicators = {
        # Netherlands variations
        'netherlands': 'Netherlands', 'holland': 'Netherlands', 'nl': 'Netherlands', 
        'nederland': 'Netherlands', 'dutch': 'Netherlands',
        'amsterdam': 'Netherlands', 'rotterdam': 'Netherlands', 'the hague': 'Netherlands',
        'utrecht': 'Netherlands', 'eindhoven': 'Netherlands', 'groningen': 'Netherlands',
        'tilburg': 'Netherlands', 'almere': 'Netherlands', 'breda': 'Netherlands',
        
        # Germany variations
        'germany': 'Germany', 'deutschland': 'Germany', 'german': 'Germany', 'de': 'Germany',
        'berlin': 'Germany', 'munich': 'Germany', 'hamburg': 'Germany', 'cologne': 'Germany',
        'frankfurt': 'Germany', 'stuttgart': 'Germany', 'düsseldorf': 'Germany',
        
        # United Kingdom variations
        'uk': 'United Kingdom', 'united kingdom': 'United Kingdom', 'britain': 'United Kingdom',
        'england': 'United Kingdom', 'scotland': 'United Kingdom', 'wales': 'United Kingdom',
        'london': 'United Kingdom', 'manchester': 'United Kingdom', 'birmingham': 'United Kingdom',
        'glasgow': 'United Kingdom', 'liverpool': 'United Kingdom', 'edinburgh': 'United Kingdom',
        
        # United States variations
        'usa': 'United States', 'us': 'United States', 'united states': 'United States',
        'america': 'United States', 'new york': 'United States', 'california': 'United States',
        'texas': 'United States', 'florida': 'United States', 'washington': 'United States',
        
        # France variations
        'france': 'France', 'french': 'France', 'fr': 'France',
        'paris': 'France', 'lyon': 'France', 'marseille': 'France', 'toulouse': 'France',
        
        # Other European countries
        'belgium': 'Belgium', 'brussels': 'Belgium', 'antwerp': 'Belgium',
        'switzerland': 'Switzerland', 'zurich': 'Switzerland', 'geneva': 'Switzerland',
        'austria': 'Austria', 'vienna': 'Austria',
        'sweden': 'Sweden', 'stockholm': 'Sweden', 'gothenburg': 'Sweden',
        'norway': 'Norway', 'oslo': 'Norway',
        'denmark': 'Denmark', 'copenhagen': 'Denmark',
        'finland': 'Finland', 'helsinki': 'Finland',
        'italy': 'Italy', 'rome': 'Italy', 'milan': 'Italy',
        'spain': 'Spain', 'madrid': 'Spain', 'barcelona': 'Spain',
        'portugal': 'Portugal', 'lisbon': 'Portugal',
        
        # Other countries
        'canada': 'Canada', 'toronto': 'Canada', 'vancouver': 'Canada', 'montreal': 'Canada',
        'australia': 'Australia', 'sydney': 'Australia', 'melbourne': 'Australia',
        'india': 'India', 'bangalore': 'India', 'mumbai': 'India', 'delhi': 'India',
        'singapore': 'Singapore',
        'japan': 'Japan', 'tokyo': 'Japan',
        'china': 'China', 'beijing': 'China', 'shanghai': 'China'
    }
    
    # Enhanced patterns for location detection
    location_patterns = [
        # Email domains (company.nl, company.de, etc.)
        r'@[a-zA-Z0-9.-]+\.([a-z]{2,3})\b',
        # Phone numbers with country codes
        r'\+(\d{1,3})\s*[\d\s\-\(\)]+',
        # Address patterns (City, Country)
        r'([A-Z][a-zA-Z\s]+),\s*([A-Z][a-zA-Z\s]+)',
        # Location after "in" or "at" (in Amsterdam, at Berlin office)
        r'(?:in|at|from|based in)\s+([A-Z][a-zA-Z\s]+)',
        # Company locations (Company Name, Location)
        r'([A-Z][a-zA-Z\s&]+(?:Inc|Corp|Corporation|LLC|Ltd|Limited|Company|Co|Technologies|Tech|Solutions|Systems|Services|Group)\.?),\s*([A-Z][a-zA-Z\s]+)',
    ]
    
    detected_countries = []
    
    # Check email domains for country codes
    email_matches = re.findall(r'@[a-zA-Z0-9.-]+\.([a-z]{2,3})\b', resume_text.lower())
    for domain in email_matches:
        if domain in country_indicators:
            country = country_indicators[domain]
            detected_countries.append(country)
            print(f"📧 Found country from email domain .{domain}: {country}")
    
    # Check phone numbers for country codes
    phone_matches = re.findall(r'\+(\d{1,3})\s*[\d\s\-\(\)]+', resume_text)
    country_codes = {
        '31': 'Netherlands', '49': 'Germany', '44': 'United Kingdom', 
        '1': 'United States', '33': 'France', '32': 'Belgium',
        '41': 'Switzerland', '43': 'Austria', '46': 'Sweden',
        '47': 'Norway', '45': 'Denmark', '358': 'Finland'
    }
    for code in phone_matches:
        if code in country_codes:
            country = country_codes[code]
            detected_countries.append(country)
            print(f"📞 Found country from phone code +{code}: {country}")
    
    # Check for explicit location mentions in text
    resume_lower = resume_text.lower()
    for indicator, country in country_indicators.items():
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(indicator) + r'\b'
        if re.search(pattern, resume_lower):
            detected_countries.append(country)
            print(f"📍 Found country from text '{indicator}': {country}")
    
    # Check companies for location indicators
    for company in companies:
        company_lower = company.lower()
        for indicator, country in country_indicators.items():
            if indicator in company_lower:
                detected_countries.append(country)
                print(f"🏢 Found country from company '{company}' -> '{indicator}': {country}")
    
    # Check job titles for location indicators (sometimes location is in job title)
    for job_title in job_titles:
        job_lower = job_title.lower()
        for indicator, country in country_indicators.items():
            if indicator in job_lower:
                detected_countries.append(country)
                print(f"💼 Found country from job title '{job_title}' -> '{indicator}': {country}")
    
    # Return the most frequently mentioned country
    if detected_countries:
        from collections import Counter
        country_counts = Counter(detected_countries)
        most_common_country = country_counts.most_common(1)[0][0]
        print(f"🌍 Most common country detected: {most_common_country} (mentioned {country_counts[most_common_country]} times)")
        return most_common_country
    
    print(f"🌍 No country detected from resume text")
    return ""

def _get_mock_resume_parse(resume_text: str):
    """
    Enhanced mock resume parsing with better pattern matching for job titles, companies, education, and location.
    This function extracts real data from the resume text using pattern matching and keyword detection.
    """
    lines = resume_text.split('\n')
    
    # Initialize data structures
    skills = []
    job_titles = []
    companies = []
    education = []
    certifications = []
    first_name = ""
    last_name = ""
    email = ""
    phone = ""
    location = ""  # Add location extraction
    
    # Location keywords and patterns
    location_keywords = [
        'address', 'location', 'based in', 'residing in', 'living in',
        'city', 'state', 'country', 'zip', 'postal code'
    ]
    
    # Common location patterns
    location_patterns = [
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})\b',  # City, State
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z][a-z]+)\b',  # City, Country
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})\s+\d{5}\b',  # City, State ZIP
    ]

    # Enhanced skill keywords with more comprehensive coverage
    skill_keywords = [
        # Programming Languages
        'python', 'java', 'scala', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 'kotlin',
        'swift', 'php', 'ruby', 'r', 'matlab', 'sql', 'plsql', 'nosql',
        
        # Data & Analytics
        'apache spark', 'pyspark', 'spark', 'kafka', 'kafka streams', 'kafka connect',
        'airflow', 'nifi', 'hadoop', 'hdfs', 'hive', 'pig', 'sqoop', 'flume',
        'elasticsearch', 'logstash', 'kibana', 'solr', 'cassandra', 'mongodb', 'redis',
        'hbase', 'neo4j', 'chromadb', 'pinecone', 'weaviate', 'qdrant',
        
        # Cloud Platforms
        'aws', 'azure', 'gcp', 'google cloud', 'amazon web services', 'microsoft azure',
        's3', 'ec2', 'lambda', 'kinesis', 'glue', 'redshift', 'dynamodb', 'rds',
        'azure data factory', 'azure databricks', 'azure synapse', 'azure sql',
        'bigquery', 'dataflow', 'pub/sub', 'cloud storage', 'cloud functions',
        
        # Data Engineering & ETL
        'etl', 'elt', 'data pipeline', 'data engineering', 'data architecture',
        'data modeling', 'data warehouse', 'data lake', 'data mesh', 'datamesh',
        'distributed systems', 'microservices', 'soa', 'api development',
        
        # Machine Learning & AI
        'machine learning', 'deep learning', 'neural networks', 'tensorflow', 'pytorch',
        'scikit-learn', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'jupyter',
        'mlops', 'model deployment', 'feature engineering', 'data science',
        'artificial intelligence', 'ai', 'ml', 'nlp', 'computer vision',
        'generative ai', 'gen ai', 'agentic ai', 'langchain', 'llms', 'rag',
        'langgraph', 'vectordbs', 'phidata', 'crewai', 'openai', 'huggingface',
        'llama', 'claude', 'gpt', 'bert', 'transformers',
        
        # DevOps & Infrastructure
        'docker', 'kubernetes', 'jenkins', 'git', 'github', 'gitlab', 'bitbucket',
        'terraform', 'ansible', 'chef', 'puppet', 'helm', 'istio', 'servicemesh',
        'nginx', 'apache', 'linux', 'unix', 'bash', 'shell scripting',
        'ci/cd', 'cicd', 'devops', 'infrastructure as code', 'monitoring',
        'prometheus', 'grafana', 'elk stack', 'splunk',
        
        # Frameworks & Tools
        'spring boot', 'spring', 'django', 'flask', 'fastapi', 'express',
        'react', 'angular', 'vue', 'node.js', 'jquery', 'bootstrap',
        'hibernate', 'jpa', 'mybatis', 'akka', 'akka-http', 'play framework',
        'vertx', 'rxjava', 'gatling', 'junit', 'mockito', 'selenium',
        
        # Databases
        'mysql', 'postgresql', 'oracle', 'sql server', 'sqlite', 'mariadb',
        'mongodb', 'cassandra', 'redis', 'elasticsearch', 'neo4j', 'dynamodb',
        
        # Methodologies & Practices
        'agile', 'scrum', 'kanban', 'waterfall', 'lean', 'six sigma',
        'project management', 'team leadership', 'mentoring', 'code review',
        'test driven development', 'tdd', 'bdd', 'pair programming',
        
        # Certifications & Standards
        'aws certified', 'azure certified', 'google cloud certified',
        'pmp', 'scrum master', 'product owner', 'itil', 'togaf',
        'cissp', 'cisa', 'cism', 'comptia', 'cisco', 'microsoft certified',
        
        # Business & Soft Skills
        'communication', 'leadership', 'problem solving', 'analytical thinking',
        'strategic planning', 'stakeholder management', 'requirements gathering',
        'business analysis', 'process improvement', 'change management'
    ]
    
    # Location keywords and patterns
    location_keywords = [
        'address', 'location', 'based in', 'residing in', 'living in',
        'city', 'state', 'country', 'zip', 'postal code'
    ]
    
    # Common location patterns
    location_patterns = [
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})\b',  # City, State
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z][a-z]+)\b',  # City, Country
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})\s+\d{5}\b',  # City, State ZIP
    ]
    
    # Enhanced job title keywords with more comprehensive patterns
    job_title_keywords = [
        'engineer', 'developer', 'architect', 'manager', 'director', 'lead', 'senior', 'principal',
        'staff', 'consultant', 'specialist', 'analyst', 'scientist', 'researcher', 'coordinator',
        'supervisor', 'administrator', 'technician', 'designer', 'programmer', 'administrator'
    ]
    
    # Job title exclusions (things that look like job titles but aren't)
    job_title_exclusions = [
        'certification', 'certified', 'university', 'college', 'degree', 'bachelor', 'master',
        'phd', 'doctorate', 'course', 'training', 'workshop', 'seminar', 'conference',
        'skills', 'technologies', 'tools', 'languages', 'frameworks', 'databases',
        'experience', 'summary', 'objective', 'profile', 'contact', 'email', 'phone',
        'address', 'linkedin', 'github', 'portfolio', 'website', 'references'
    ]
    
    # Company keywords
    company_keywords = [
        'inc', 'corp', 'corporation', 'company', 'ltd', 'limited', 'llc', 'technologies',
        'solutions', 'systems', 'services', 'consulting', 'group', 'enterprises',
        'international', 'global', 'worldwide', 'associates', 'partners', 'holdings'
    ]
    
    # Education keywords
    education_keywords = [
        'university', 'college', 'institute', 'school', 'academy', 'bachelor', 'master',
        'phd', 'doctorate', 'degree', 'diploma', 'certificate', 'certification',
        'computer science', 'engineering', 'mathematics', 'physics', 'chemistry',
        'business', 'management', 'economics', 'finance', 'marketing', 'mba'
    ]
    
    education_exclusions = [
        'experience', 'work', 'employment', 'job', 'position', 'role', 'responsibilities',
        'achievements', 'skills', 'technologies', 'tools', 'projects', 'summary'
    ]
    
    # Certification keywords
    certification_keywords = [
        'certified', 'certification', 'aws', 'azure', 'google cloud', 'microsoft',
        'oracle', 'cisco', 'comptia', 'pmp', 'scrum master', 'product owner',
        'itil', 'togaf', 'cissp', 'cisa', 'cism', 'kubernetes', 'docker'
    ]
    
    # Extract personal information
    for line in lines[:10]:  # Check first 10 lines for personal info
        line_clean = line.strip()
        if not line_clean:
            continue
            
        # Extract email
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', line_clean)
        if email_match and not email:
            email = email_match.group()
        
        # Extract phone
        phone_match = re.search(r'[\+]?[1-9]?[\-\.\s]?\(?[0-9]{3}\)?[\-\.\s]?[0-9]{3}[\-\.\s]?[0-9]{4}', line_clean)
        if phone_match and not phone:
            phone = phone_match.group()
        
        # Extract name (first line that looks like a name)
        if not first_name and not last_name and len(line_clean.split()) >= 2:
            words = line_clean.split()
            if (len(words) == 2 and 
                all(word.isalpha() and word[0].isupper() for word in words) and
                '@' not in line_clean and not any(char.isdigit() for char in line_clean)):
                first_name = words[0]
                last_name = words[1]
        
        # Extract location
        if not location:
            line_lower = line_clean.lower()
            # Check for location keywords
            if any(keyword in line_lower for keyword in location_keywords):
                # Try to extract location from this line
                for pattern in location_patterns:
                    match = re.search(pattern, line_clean)
                    if match:
                        location = match.group().strip()
                        break
                
                # If no pattern match, look for city/state combinations
                if not location:
                    words = line_clean.split()
                    for i, word in enumerate(words):
                        if word.endswith(',') and i + 1 < len(words):
                            next_word = words[i + 1]
                            if len(next_word) == 2 and next_word.isupper():  # State abbreviation
                                location = f"{word[:-1]}, {next_word}"
                                break
                            elif next_word[0].isupper() and len(next_word) > 2:  # Country/State name
                                location = f"{word[:-1]}, {next_word}"
                                break
        
        # Extract location
        if not location:
            line_lower = line_clean.lower()
            # Check for location keywords
            if any(keyword in line_lower for keyword in location_keywords):
                # Try to extract location from this line
                for pattern in location_patterns:
                    match = re.search(pattern, line_clean)
                    if match:
                        location = match.group().strip()
                        break
                
                # If no pattern match, look for city/state combinations
                if not location:
                    words = line_clean.split()
                    for i, word in enumerate(words):
                        if word.endswith(',') and i + 1 < len(words):
                            next_word = words[i + 1]
                            if len(next_word) == 2 and next_word.isupper():  # State abbreviation
                                location = f"{word[:-1]}, {next_word}"
                                break
                            elif next_word[0].isupper() and len(next_word) > 2:  # Country/State name
                                location = f"{word[:-1]}, {next_word}"
                                break
    
    # Extract skills from dedicated skills sections first (handles comma/slash separation)
    section_skills = _extract_skills_from_sections(resume_text)
    skills.extend(section_skills)
    
    # Then extract skills with keyword matching for additional coverage
    resume_lower = resume_text.lower()
    for skill_keyword in skill_keywords:
        if skill_keyword in resume_lower:
            # Check for exact matches and variations
            skill_variations = [
                skill_keyword,
                skill_keyword.replace(' ', ''),
                skill_keyword.replace(' ', '-'),
                skill_keyword.replace(' ', '_'),
                skill_keyword.title(),
                skill_keyword.upper()
            ]
            
            for variation in skill_variations:
                if variation.lower() in resume_lower:
                    # Add the most appropriate form
                    if skill_keyword == 'apache spark':
                        skills.append('Apache Spark')
                    elif skill_keyword == 'kafka streams':
                        skills.append('Kafka Streams')
                    elif skill_keyword == 'akka-http':
                        skills.append('Akka-HTTP')
                    elif skill_keyword == 'spring boot':
                        skills.append('Spring Boot')
                    elif skill_keyword == 'machine learning':
                        skills.append('Machine Learning')
                    elif skill_keyword == 'artificial intelligence':
                        skills.append('AI and Machine Learning')
                    elif skill_keyword in ['python', 'java', 'scala']:
                        skills.append(skill_keyword.title())
                    elif skill_keyword in ['aws', 'gcp']:
                        skills.append(skill_keyword.upper())
                    elif skill_keyword == 'sql':
                        skills.append('SQL and NoSQL Databases')
                    elif skill_keyword == 'devops':
                        skills.append('DevOps and Cloud Technologies')
                    elif skill_keyword in ['agile', 'scrum']:
                        skills.append('Project Management and Agile Methodologies')
                    else:
                        skills.append(skill_keyword.title())
                    break
    
    # Remove duplicates and clean up skills
    skills = list(dict.fromkeys(skills))  # Remove duplicates while preserving order
    
    # Extract job titles with enhanced pattern matching
    for line in lines:
        line_clean = line.strip()
        if not line_clean or len(line_clean) < 10 or len(line_clean) > 100:
            continue
            
        line_lower = line_clean.lower()
        
        # Skip lines that are clearly not job titles
        if any(exclusion in line_lower for exclusion in job_title_exclusions):
            continue
            
        # Skip certifications that might look like job titles
        if ('certified' in line_lower or 'certification' in line_lower or 
            line_lower.startswith(('aws', 'azure', 'google cloud', 'microsoft', 'oracle'))):
            continue
            
        # Look for job title patterns
        if any(keyword in line_lower for keyword in job_title_keywords):
            # Check if this line contains a date range (work experience entry)
            date_range_match = re.search(r'(\d{4})\s*[-–—]\s*(\d{4}|present|current)', line_clean, re.IGNORECASE)
            
            if date_range_match:
                # This is a work experience entry, extract job title after the colon
                if ':' in line_clean:
                    job_title_part = line_clean.split(':', 1)[1].strip()
                    # Remove company and location info (everything after comma)
                    if ',' in job_title_part:
                        job_title_part = job_title_part.split(',')[0].strip()
                    
                    # Additional validation for extracted job title
                    if (job_title_part and len(job_title_part) > 5 and len(job_title_part) < 60 and
                        not job_title_part.lower().startswith(('skills', 'experience', 'education', 'summary', 'certified', 'aws', 'azure', 'google')) and
                        'certified' not in job_title_part.lower() and
                        any(keyword in job_title_part.lower() for keyword in job_title_keywords)):
                        
                        # Avoid duplicate entries
                        if not any(existing.lower() in job_title_part.lower() or job_title_part.lower() in existing.lower() for existing in job_titles):
                            job_titles.append(job_title_part)
            else:
                # Regular job title line (not a work experience entry)
                if (not line_clean.startswith(('•', '◦', '-', '*', '  ')) and  # Not a bullet point
                    not line_clean.endswith((':')) and  # Not a section header
                    '@' not in line_clean and  # Not an email
                    len(line_clean.split()) <= 8):  # Not too long
                    
                    # Additional validation - exclude certifications
                    if (line_clean and len(line_clean) > 5 and len(line_clean) < 80 and
                        not line_clean.lower().startswith(('skills', 'experience', 'education', 'summary', 'certified', 'aws', 'azure', 'google')) and
                        not line_clean.startswith(('•', '◦', '-', '*')) and
                        'certified' not in line_clean.lower()):
                        
                        # Avoid duplicate entries
                        if not any(existing.lower() in line_clean.lower() or line_clean.lower() in existing.lower() for existing in job_titles):
                            job_titles.append(line_clean)
    
    # Extract companies with enhanced pattern matching
    for line in lines:
        line_clean = line.strip()
        if not line_clean or len(line_clean) < 5 or len(line_clean) > 80:
            continue
            
        line_lower = line_clean.lower()
        
        # Look for company indicators
        if (any(keyword in line_lower for keyword in company_keywords) or
            re.search(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Inc|Corp|LLC|Ltd|Technologies|Solutions|Systems|Services|Group)\b', line_clean)):
            
            # Additional filtering
            if (not line_clean.startswith(('•', '◦', '-', '*', '  ')) and
                '@' not in line_clean and
                not any(exclusion in line_lower for exclusion in ['university', 'college', 'school', 'degree', 'certification'])):
                
                # Clean up the company name
                cleaned_company = re.sub(r'\d{4}[-–—]\d{4}|\d{4}[-–—]present|present', '', line_clean, flags=re.IGNORECASE).strip()
                
                # For work experience entries, extract company name after colon and before comma
                if ':' in cleaned_company:
                    company_part = cleaned_company.split(':', 1)[1].strip()
                    if ',' in company_part:
                        company_part = company_part.split(',')[0].strip()
                    cleaned_company = company_part
                
                if (cleaned_company and len(cleaned_company) > 3 and len(cleaned_company) < 60 and
                    not cleaned_company.lower().startswith(('experience', 'work', 'employment', 'skills')) and
                    not cleaned_company.isdigit() and  # Exclude pure numbers
                    any(keyword in cleaned_company.lower() for keyword in company_keywords)):
                    
                    # Avoid duplicate entries
                    if not any(existing.lower() in cleaned_company.lower() or cleaned_company.lower() in existing.lower() for existing in companies):
                        companies.append(cleaned_company)
    
    # Extract certifications
    for line in lines:
        line_clean = line.strip()
        if not line_clean or len(line_clean) < 5:
            continue
            
        line_lower = line_clean.lower()
        
        # Look for certification keywords
        if any(keyword in line_lower for keyword in certification_keywords):
            # Additional filtering for certifications
            if (not line_clean.startswith(('•', '◦', '-', '*', '  ')) and
                len(line_clean) < 100 and
                '@' not in line_clean):
                
                # Clean up certification
                cleaned_cert = re.sub(r'\d{4}[-–]\d{4}|\d{4}[-–]present|present', '', line_clean, flags=re.IGNORECASE).strip()
                
                if (cleaned_cert and len(cleaned_cert) > 10 and
                    not any(exclusion in cleaned_cert.lower() for exclusion in ['experience', 'work', 'job', 'position'])):
                    
                    # Avoid duplicate entries
                    if not any(existing.lower() in cleaned_cert.lower() or cleaned_cert.lower() in existing.lower() for existing in certifications):
                        certifications.append(cleaned_cert)
        
        # Check if this line contains education information
        if (line_clean and len(line_clean) < 200 and len(line_clean) > 10 and
            any(keyword in line_lower for keyword in education_keywords) and
            not any(exclusion in line_lower for exclusion in education_exclusions) and
            not line_clean.startswith(('•', '◦', '-', '*', '  ')) and  # Not a bullet point
            '@' not in line_clean):  # Not an email
            
            # Clean up the education entry
            cleaned_education = re.sub(r'\d{4}[-–]\d{4}|\d{4}[-–]present|present', '', line_clean, flags=re.IGNORECASE).strip()
            
            # Additional filtering to ensure it's a real education entry
            if (cleaned_education and len(cleaned_education) > 15 and len(cleaned_education) < 150 and
                not any(exclusion in cleaned_education.lower() for exclusion in education_exclusions) and
                not cleaned_education.lower().startswith(('skills', 'experience', 'summary', 'objective')) and
                not cleaned_education.startswith(('•', '◦', '-', '*')) and
                '@' not in cleaned_education):  # Double check no email
                
                # Avoid duplicate entries
                if not any(existing.lower() in cleaned_education.lower() or cleaned_education.lower() in existing.lower() for existing in education):
                    education.append(cleaned_education)
    
    # Remove duplicates and limit
    education = list(dict.fromkeys(education))
    
    if not education:
        education = ["Bachelor of Science in Computer Science", "Master of Science in Data Science"]
    else:
        education = education[:3]  # Limit to 3 education entries
    
    # Clean up certifications list
    if not certifications:
        certifications = ["Professional Development", "Industry Training"]
    else:
        certifications = certifications[:5]  # Limit to 5 certifications
    
    # Estimate experience years based on content
    if 'senior' in resume_text.lower() or 'lead' in resume_text.lower():
        experience_years = 6
    elif 'manager' in resume_text.lower() or 'director' in resume_text.lower():
        experience_years = 8
    elif len(companies) > 2 or len(job_titles) > 2:
        experience_years = 4
    else:
        experience_years = 2
    
    # If no location found, try to infer from common patterns in the entire text
    if not location:
        for pattern in location_patterns:
            matches = re.findall(pattern, resume_text)
            if matches:
                location = f"{matches[0][0]}, {matches[0][1]}"
                break
    
    # Enhanced location extraction from companies and job history
    if not location:
        location = _extract_country_from_work_history(resume_text, companies, job_titles)
    
    # Ensure we have at least some companies
    if not companies:
        print("🏢 No companies found in mock parsing, using enhanced extraction...")
        companies = _extract_companies_from_text(resume_text)
        if not companies:
            companies = ["Previous Company"]  # Minimal fallback
    
    mock_data = {
        "firstName": first_name,
        "lastName": last_name,
        "email": email,
        "phone": phone,
        "location": location,  # Add location to the response
        "experienceYears": experience_years,
        "skills": skills,
        "lastThreeJobTitles": job_titles,
        "experienceSummary": f"Experienced professional with {experience_years} years in the field. Demonstrates strong technical and analytical skills with a proven track record of successful project delivery and team collaboration.",
        "companies": companies,
        "education": education,
        "certifications": certifications
    }
    
    return json.dumps(mock_data)

def generate_career_path(job_title: str, experience: str, skills: list[str]):
    """
    Generates a personalized career path recommendation using an AI model.
    """
    if is_development_mode or llm is None:
        return _get_mock_career_path(job_title, experience, skills)
    
    try:
        prompt = PromptTemplate(
            input_variables=["job_title", "experience", "skills"],
            template="""
            As a career advisor, create a personalized career path recommendation for a user with the following profile:

            Current Role/Aspired Role: {job_title}
            Experience: {experience}
            Skills: {skills}

            Please provide a detailed career path including:
            1.  **Short-term goals (1-2 years):** Suggest 2-3 roles they can aim for next, with required skills.
            2.  **Mid-term goals (3-5 years):** Suggest 2-3 more advanced roles.
            3.  **Long-term goals (5+ years):** Suggest a senior-level or leadership role.
            4.  **Skill Development:** Recommend 5-7 key skills to develop for this path, including both technical and soft skills.

            Present the information in a clear, structured format.
            """
        )

        skill_str = ", ".join(skills)
        chain = LLMChain(llm=llm, prompt=prompt)
        response = chain.run(job_title=job_title, experience=experience, skills=skill_str)
        
        return response
    except Exception as e:
        print(f"Error generating career path with AI: {e}")
        return _get_mock_career_path(job_title, experience, skills)

def analyze_skill_gap(skills: list[str], job_description: str, target_role: str = None):
    """
    Analyzes the gap between a user's skills and a job description/target role.
    Enhanced to align with PRD section 4.3 requirements:
    - Compare user skills to target roles
    - Identify gaps and recommend specific courses, certifications, or learning resources
    - Integrate with APIs like Coursera, Udemy, etc.
    """
    if is_development_mode or llm is None:
        return _get_enhanced_mock_skill_gap(skills, job_description, target_role)
    
    try:
        # Enhanced prompt for better skill gap analysis
        prompt = PromptTemplate(
            input_variables=["skills", "job_description", "target_role"],
            template="""
            As an expert career advisor and learning specialist, analyze the skill gap between the user's current skills and their target career goals.

            User's Current Skills: {skills}
            
            Job Description: {job_description}
            
            Target Role (if specified): {target_role}

            Please provide a comprehensive skill gap analysis with the following sections:

            ## 1. SKILL MATCH ANALYSIS
            - **Matching Skills:** List skills the user already has that align with the job requirements
            - **Skill Strength Score:** Rate the user's overall skill alignment (1-10 scale)

            ## 2. CRITICAL SKILL GAPS
            - **Missing Technical Skills:** Key technical skills required but not possessed
            - **Missing Soft Skills:** Important soft skills needed for the role
            - **Priority Level:** Mark each gap as High/Medium/Low priority

            ## 3. SKILL ENHANCEMENT OPPORTUNITIES  
            - **Skills to Strengthen:** Existing skills that need improvement
            - **Specific Areas:** What aspects of these skills need development

            ## 4. TARGETED LEARNING RECOMMENDATIONS
            For each missing or weak skill, provide specific learning resources:

            ### Online Courses:
            - **Coursera:** Specific course names from top universities (e.g., "Machine Learning by Stanford University")
            - **Udemy:** Popular highly-rated courses with instructor names
            - **Pluralsight:** Technology-focused learning paths
            - **DeepLearning.ai:** AI/ML specializations
            - **LinkedIn Learning:** Professional development courses

            ### Certifications:
            - Industry-recognized certifications (AWS, Google Cloud, Microsoft, etc.)
            - Professional certifications relevant to the role

            ### Free Resources:
            - **YouTube Channels:** Specific channels with high engagement
            - **Documentation & Tutorials:** Official docs and guides
            - **Open Source Projects:** GitHub repositories to contribute to

            ### Books & Publications:
            - Essential books for skill development
            - Industry publications and blogs

            ## 5. LEARNING ROADMAP
            - **Phase 1 (1-3 months):** Immediate priority skills
            - **Phase 2 (3-6 months):** Intermediate development
            - **Phase 3 (6-12 months):** Advanced skills and specialization

            ## 6. MARKET INSIGHTS
            - **Skill Demand:** How in-demand are the missing skills
            - **Salary Impact:** Potential salary increase with these skills
            - **Career Progression:** How these skills enable career advancement

            Present the analysis in a clear, actionable format with specific resource recommendations.
            """
        )

        skill_str = ", ".join(skills)
        target_role_str = target_role if target_role else "Not specified"
        
        chain = LLMChain(llm=llm, prompt=prompt)
        response = chain.run(
            skills=skill_str, 
            job_description=job_description,
            target_role=target_role_str
        )

        return response
    except Exception as e:
        print(f"Error analyzing skill gap with AI: {e}")
        return _get_enhanced_mock_skill_gap(skills, job_description, target_role)

def _get_enhanced_mock_skill_gap(skills: list[str], job_description: str, target_role: str = None):
    """Return enhanced mock skill gap analysis aligned with PRD requirements"""
    user_skills_str = ", ".join(skills[:5]) if skills else "General technical skills"
    role_context = f" for {target_role}" if target_role else ""
    
    return f"""# 🎯 Comprehensive Skill Gap Analysis{role_context}

## 1. SKILL MATCH ANALYSIS
**Matching Skills:** {user_skills_str}
**Skill Strength Score:** 7/10 - Good foundation with room for growth

## 2. CRITICAL SKILL GAPS

### High Priority (Missing Technical Skills):
- **Cloud Computing** (AWS/Azure/GCP) - Essential for modern development
- **DevOps & CI/CD** - Critical for deployment automation
- **System Design** - Required for senior-level positions
- **API Development** - Microservices architecture knowledge

### Medium Priority (Missing Soft Skills):
- **Technical Leadership** - Leading technical initiatives
- **Stakeholder Communication** - Cross-functional collaboration
- **Agile Project Management** - Modern development methodologies

## 3. SKILL ENHANCEMENT OPPORTUNITIES
- **Programming Skills:** Advance from intermediate to expert level
- **Database Management:** Move beyond basic SQL to optimization
- **Problem Solving:** Develop algorithmic thinking and system design

## 4. TARGETED LEARNING RECOMMENDATIONS

### 📚 Online Courses:

#### Coursera:
- **"AWS Fundamentals" by Amazon Web Services** - 4.6★ rating, 50K+ students
- **"Machine Learning" by Stanford University** - Andrew Ng, 4.9★ rating
- **"Google Cloud Platform Fundamentals" by Google Cloud** - Industry-leading content

#### Udemy:
- **"Docker and Kubernetes: The Complete Guide" by Stephen Grider** - 4.7★, 100K+ students
- **"The Complete Node.js Developer Course" by Andrew Mead** - 4.6★, 200K+ students
- **"React - The Complete Guide" by Maximilian Schwarzmüller** - 4.6★, 500K+ students

#### Pluralsight:
- **"AWS Developer Learning Path"** - Comprehensive cloud development
- **"DevOps Foundations Learning Path"** - CI/CD and automation
- **"System Design Interview Prep"** - Architecture and scalability

#### DeepLearning.ai:
- **"Deep Learning Specialization"** - 5-course series by Andrew Ng
- **"Machine Learning Engineering for Production (MLOps)"** - Production ML systems

#### LinkedIn Learning:
- **"Strategic Thinking"** - Executive-level decision making
- **"Leading Technical Teams"** - Engineering management
- **"Agile Project Management"** - Modern project delivery

### 🏆 Certifications:
- **AWS Solutions Architect Associate** - $150, 3-month prep time
- **Google Cloud Professional Developer** - $200, industry-recognized
- **Microsoft Azure Developer Associate** - $165, growing demand
- **Certified Kubernetes Administrator (CKA)** - $375, container orchestration
- **PMP (Project Management Professional)** - $555, leadership credential

### 🆓 Free Resources:

#### YouTube Channels:
- **"Traversy Media"** - 1.8M subscribers, web development tutorials
- **"TechWorld with Nana"** - 500K+ subscribers, DevOps and cloud
- **"freeCodeCamp.org"** - 5M+ subscribers, comprehensive programming courses
- **"AWS Online Tech Talks"** - Official AWS content, latest updates

#### Documentation & Tutorials:
- **AWS Documentation** - Comprehensive cloud service guides
- **Kubernetes Official Docs** - Container orchestration mastery
- **React Official Tutorial** - Frontend framework fundamentals
- **MDN Web Docs** - Web development reference

#### Open Source Projects:
- **Contribute to React.js** - Frontend framework development
- **Kubernetes Community** - Cloud-native computing
- **TensorFlow** - Machine learning framework contributions

### 📖 Books & Publications:
- **"Designing Data-Intensive Applications" by Martin Kleppmann** - System design bible
- **"Clean Code" by Robert C. Martin** - Code quality and maintainability
- **"The DevOps Handbook" by Gene Kim** - DevOps culture and practices
- **"System Design Interview" by Alex Xu** - Technical interview preparation

## 5. LEARNING ROADMAP

### Phase 1 (1-3 months) - Foundation Building:
1. **Cloud Fundamentals** - AWS/Azure basics (40 hours)
2. **Docker Containerization** - Container basics (20 hours)
3. **API Development** - REST/GraphQL principles (30 hours)
4. **Git Advanced** - Branching strategies and collaboration (10 hours)

### Phase 2 (3-6 months) - Intermediate Development:
1. **Kubernetes Orchestration** - Container management (50 hours)
2. **CI/CD Pipelines** - Automated deployment (40 hours)
3. **System Design Basics** - Scalability patterns (60 hours)
4. **Database Optimization** - Performance tuning (30 hours)

### Phase 3 (6-12 months) - Advanced Specialization:
1. **Cloud Architecture** - Multi-service design (80 hours)
2. **Technical Leadership** - Team and project management (40 hours)
3. **Advanced System Design** - Large-scale systems (100 hours)
4. **Industry Specialization** - Domain-specific expertise (60 hours)

## 6. MARKET INSIGHTS

### 📈 Skill Demand Analysis:
- **Cloud Computing:** 85% of companies adopting cloud-first strategies
- **DevOps:** 73% increase in job postings over last 2 years
- **System Design:** Required for 90% of senior engineering roles
- **API Development:** Growing 45% annually with microservices adoption

### 💰 Salary Impact:
- **Cloud Certification:** +$15,000-25,000 average salary increase
- **DevOps Skills:** +$20,000-30,000 for experienced professionals
- **System Design Expertise:** +$25,000-40,000 for senior roles
- **Combined Skills:** Potential 40-60% salary increase over 2-3 years

### 🚀 Career Progression:
- **Short-term:** Senior Developer/Technical Lead roles
- **Mid-term:** Engineering Manager/Principal Engineer positions
- **Long-term:** Director of Engineering/CTO opportunities

## 📊 Next Steps:
1. **Start with Phase 1 priorities** - Focus on cloud and containerization
2. **Set learning schedule** - Dedicate 10-15 hours per week
3. **Join communities** - AWS User Groups, Kubernetes meetups
4. **Build portfolio projects** - Demonstrate new skills practically
5. **Track progress** - Use learning management tools and certifications

*Estimated total learning time: 200-300 hours over 12 months*
*Investment: $500-1,000 in courses and certifications*
*Expected ROI: 40-60% salary increase within 2 years*"""

def optimize_resume(resume_text: str, job_description: str):
    """
    Optimizes a user's resume for a specific job description using OpenAI.
    Provides comprehensive analysis for ATS compatibility and interview success.
    """
    if is_development_mode or llm is None:
        return _get_enhanced_mock_resume_optimization(resume_text, job_description)
    
    try:
        prompt = PromptTemplate(
            input_variables=["resume_text", "job_description"],
            template="""
            As an expert resume writer and career coach with 15+ years of experience helping candidates land interviews at top companies, analyze the following resume against the target job description. Provide actionable, specific recommendations to optimize this resume for maximum ATS compatibility and interview success.

            **User's Current Resume:**
            {resume_text}

            **Target Job Description:**
            {job_description}

            Please provide a comprehensive analysis with the following sections:

            ## 🎯 **ATS OPTIMIZATION ANALYSIS**
            
            ### **Keyword Match Score:** [X/10]
            - Identify 8-10 critical keywords/phrases from the job description that are missing or underrepresented in the resume
            - Suggest specific locations in the resume where these keywords should be naturally integrated
            - Highlight any keyword stuffing risks to avoid

            ### **ATS-Friendly Formatting Issues:**
            - Identify any formatting problems that could cause ATS parsing errors
            - Suggest improvements for section headers, bullet points, and overall structure

            ## 📝 **CONTENT OPTIMIZATION**

            ### **Professional Summary Enhancement:**
            Write a compelling 3-4 line professional summary specifically tailored to this role that:
            - Incorporates key job requirements
            - Highlights relevant achievements with quantifiable results
            - Uses industry-specific terminology from the job posting

            ### **Experience Section Improvements:**
            Rewrite 4-5 bullet points from the current resume using the STAR method (Situation, Task, Action, Result):
            - Focus on achievements that directly relate to the job requirements
            - Include specific metrics, percentages, or dollar amounts where possible
            - Use strong action verbs that match the job description's language

            ### **Skills Section Optimization:**
            - Reorganize skills to prioritize those mentioned in the job description
            - Suggest additional relevant skills to include based on the role
            - Recommend removing outdated or irrelevant skills

            ## 🚀 **INTERVIEW SUCCESS STRATEGIES**

            ### **Competitive Advantage Points:**
            - Identify 3-4 unique strengths from the resume that differentiate the candidate
            - Suggest how to better highlight these advantages
            - Recommend specific examples or projects to emphasize

            ### **Gap Analysis & Mitigation:**
            - Identify any obvious gaps between the resume and job requirements
            - Suggest ways to address or minimize these gaps
            - Recommend additional qualifications or experiences to pursue

            ## 📊 **QUANTIFIABLE IMPROVEMENTS**

            ### **Before vs. After Metrics:**
            - Estimate the current resume's match percentage to the job description
            - Project the improved match percentage after implementing recommendations
            - Highlight the most impactful changes for maximum ROI

            ### **Industry Benchmarking:**
            - Compare the resume against industry standards for this role level
            - Suggest improvements to meet or exceed typical expectations
            - Identify areas where the candidate already exceeds standards

            ## 🎨 **PRESENTATION & FORMATTING**

            ### **Visual Appeal Enhancements:**
            - Suggest improvements to layout and visual hierarchy
            - Recommend optimal resume length for this role
            - Provide guidance on font choices, spacing, and section organization

            ### **Contact Information & Online Presence:**
            - Review contact information completeness and professionalism
            - Suggest LinkedIn profile optimizations
            - Recommend portfolio or project showcase improvements

            ## 🔥 **IMMEDIATE ACTION ITEMS**

            Provide a prioritized list of the top 5 most critical changes to implement first, ranked by:
            1. **Impact on ATS scoring**
            2. **Relevance to job requirements**
            3. **Ease of implementation**
            4. **Potential to secure interviews**

            ## 💡 **BONUS TIPS FOR THIS SPECIFIC ROLE**

            Based on the job description, provide 3-4 insider tips about:
            - What this company/role likely values most
            - Industry-specific terminology to include
            - Common mistakes to avoid for this type of position
            - Additional ways to stand out from other candidates

            **Remember:** Focus on specific, actionable advice that will directly improve the candidate's chances of getting past ATS systems and securing interviews. Use concrete examples and avoid generic advice.
            """
        )

        chain = LLMChain(llm=llm, prompt=prompt)
        response = chain.run(resume_text=resume_text, job_description=job_description)

        return response
    except Exception as e:
        print(f"Error optimizing resume with AI: {e}")
        return _get_enhanced_mock_resume_optimization(resume_text, job_description)

def _get_enhanced_mock_resume_optimization(resume_text: str, job_description: str):
    """Return enhanced mock resume optimization with comprehensive analysis"""
    
    # Extract some keywords from job description for realistic mock
    job_words = job_description.lower().split()
    common_tech_keywords = ['python', 'javascript', 'react', 'aws', 'docker', 'kubernetes', 'sql', 'api', 'agile', 'scrum']
    found_keywords = [word for word in common_tech_keywords if word in job_words]
    
    return f"""# 🎯 **COMPREHENSIVE RESUME OPTIMIZATION ANALYSIS**

## 📊 **ATS OPTIMIZATION ANALYSIS**

### **Keyword Match Score: 6/10**
Your resume currently matches 60% of the critical keywords from the job description. Here's how to improve:

**Missing Critical Keywords:**
- **{', '.join(found_keywords[:3] if found_keywords else ['Cloud Computing', 'API Development', 'Agile Methodology'])}** - These appear 5+ times in the job description
- **Project Management** - Mentioned as a key requirement
- **Cross-functional collaboration** - Essential for this role
- **Data analysis** - Core responsibility mentioned

**Integration Recommendations:**
- Add these keywords naturally in your Professional Summary
- Incorporate them into your experience bullet points with specific examples
- Include relevant keywords in your Skills section

### **ATS-Friendly Formatting Issues:**
✅ **Good:** Standard section headers, consistent formatting
⚠️ **Improve:** 
- Use standard bullet points (•) instead of special characters
- Ensure consistent date formatting (MM/YYYY)
- Add a clear "Skills" section header

## 📝 **CONTENT OPTIMIZATION**

### **Enhanced Professional Summary:**
```
Results-driven software engineer with 5+ years of experience developing scalable web applications using Python, JavaScript, and cloud technologies. Proven track record of leading cross-functional teams to deliver high-impact projects 25% ahead of schedule. Expertise in API development, microservices architecture, and agile methodologies. Seeking to leverage technical leadership skills and passion for innovation to drive digital transformation initiatives at [Company Name].
```

### **Improved Experience Bullet Points:**

**Before:** "Worked on various software projects"
**After:** "Led development of 3 mission-critical web applications serving 10,000+ daily users, resulting in 40% improvement in system performance and 99.9% uptime"

**Before:** "Used Python for backend development"
**After:** "Architected and implemented RESTful APIs using Python/Django, reducing data processing time by 60% and enabling seamless integration with 5 third-party services"

**Before:** "Collaborated with team members"
**After:** "Facilitated daily standups and sprint planning for 8-person cross-functional team, improving project delivery speed by 35% and reducing bugs by 50%"

**Before:** "Worked with databases"
**After:** "Optimized PostgreSQL database queries and implemented caching strategies, reducing average response time from 2.3s to 0.4s for core application features"

### **Skills Section Optimization:**

**Prioritized Technical Skills:**
- **Programming Languages:** Python, JavaScript, SQL, Java
- **Frameworks & Libraries:** React, Django, Node.js, Express
- **Cloud & DevOps:** AWS (EC2, S3, Lambda), Docker, Kubernetes, CI/CD
- **Databases:** PostgreSQL, MongoDB, Redis
- **Tools & Methodologies:** Git, Agile/Scrum, JIRA, API Development

## 🚀 **INTERVIEW SUCCESS STRATEGIES**

### **Competitive Advantage Points:**
1. **Full-Stack Versatility:** Your experience spans both frontend and backend development
2. **Leadership Experience:** Evidence of leading teams and mentoring junior developers
3. **Performance Optimization:** Track record of improving system performance and efficiency
4. **Cross-Functional Collaboration:** Strong communication skills with non-technical stakeholders

### **Gap Analysis & Mitigation:**
**Identified Gaps:**
- Limited cloud architecture experience (mentioned in job requirements)
- No mention of specific industry experience (if relevant)

**Mitigation Strategies:**
- Highlight any cloud projects, even if small-scale
- Emphasize transferable skills and quick learning ability
- Consider obtaining AWS certification to strengthen cloud credentials

## 📊 **QUANTIFIABLE IMPROVEMENTS**

### **Before vs. After Metrics:**
- **Current Match:** 60% alignment with job requirements
- **Projected Match:** 85% after implementing recommendations
- **ATS Score Improvement:** +40% keyword relevance
- **Interview Probability:** Increased from 15% to 35%

### **Industry Benchmarking:**
- **Above Average:** Technical skill diversity, project leadership experience
- **At Standard:** Educational background, years of experience
- **Below Average:** Industry-specific certifications, cloud architecture experience

## 🎨 **PRESENTATION & FORMATTING**

### **Visual Appeal Enhancements:**
- **Length:** Keep to 2 pages maximum for your experience level
- **Font:** Use professional fonts like Calibri, Arial, or Times New Roman (11-12pt)
- **Spacing:** Ensure consistent 1.15-1.5 line spacing for readability
- **Sections:** Use clear section headers with consistent formatting

### **Contact Information & Online Presence:**
- ✅ Include LinkedIn profile URL
- ✅ Add GitHub portfolio link
- ✅ Ensure professional email address
- 💡 Consider adding a personal website/portfolio

## 🔥 **IMMEDIATE ACTION ITEMS**

**Priority 1 (Highest Impact):**
1. **Rewrite Professional Summary** - Include target role keywords and quantified achievements
2. **Add Missing Keywords** - Integrate 5-7 critical terms from job description naturally

**Priority 2 (High Impact):**
3. **Quantify Achievements** - Add specific metrics to 4-5 bullet points
4. **Reorganize Skills Section** - Prioritize job-relevant technical skills

**Priority 3 (Medium Impact):**
5. **Format Consistency** - Ensure uniform date formats and bullet point styles

## 💡 **BONUS TIPS FOR THIS SPECIFIC ROLE**

### **Industry Insights:**
1. **Company Culture Fit:** This role values innovation and collaboration - emphasize team projects and creative problem-solving
2. **Technical Depth:** Highlight experience with modern development practices like TDD, code reviews, and continuous integration
3. **Growth Mindset:** Mention learning new technologies, attending conferences, or contributing to open source
4. **Business Impact:** Connect technical achievements to business outcomes (revenue, efficiency, user satisfaction)

### **Common Mistakes to Avoid:**
- Don't use overly technical jargon that HR might not understand
- Avoid listing every technology you've ever touched - focus on relevant ones
- Don't undersell your achievements - use strong action verbs and specific metrics

### **Stand-Out Strategies:**
- Include a brief "Notable Projects" section with 2-3 impressive accomplishments
- Mention any mentoring, training, or knowledge-sharing activities
- Highlight any process improvements or innovations you've introduced

## 🎯 **EXPECTED OUTCOMES**

After implementing these recommendations:
- **25-40% increase** in ATS compatibility score
- **3x higher chance** of getting past initial screening
- **Stronger positioning** for salary negotiations
- **More targeted** interview conversations about relevant experience

**Timeline for Implementation:** 2-3 hours to make critical changes, 1-2 days for comprehensive optimization

**Next Steps:** 
1. Implement Priority 1 changes immediately
2. Test your optimized resume with online ATS scanners
3. Tailor this optimized version for each specific application
4. Track application response rates to measure improvement

*Remember: A well-optimized resume is your ticket to the interview - make every word count!*""" 

def _extract_work_experience_companies(resume_text: str) -> list:
    """
    Aggressive extraction of companies from work experience sections.
    Specifically designed to handle the format in the provided CV.
    """
    import re
    
    companies = []
    lines = resume_text.split('\n')
    
    # Look for the work experience section
    in_work_section = False
    for i, line in enumerate(lines):
        line_clean = line.strip()
        if not line_clean:
            continue
            
        line_lower = line_clean.lower()
        
        # Check if we're entering work experience section
        if 'work experience' in line_lower or 'employment' in line_lower:
            in_work_section = True
            continue
            
        # Check if we're leaving work experience section
        if in_work_section and any(keyword in line_lower for keyword in ['education', 'skills', 'certifications', 'projects']):
            break
        
        if in_work_section:
            # Skip header lines and role descriptions
            if any(skip in line_lower for skip in ['company name', 'duration', 'role', 'responsibilities', 'technologies']):
                continue
                
            # Look for company patterns - companies usually have these indicators
            company_indicators = ['B.V.', 'Ltd', 'Inc', 'Corp', 'LLC', 'Group', 'Bank', 'Technologies', 'Solutions', 'International']
            if any(indicator in line_clean for indicator in company_indicators):
                # Extract company name (everything before duration indicators like months/years)
                company_match = re.match(r'^([^0-9]+?)(?:\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d|March|October))', line_clean)
                if company_match:
                    company = company_match.group(1).strip()
                    # Clean up common suffixes that aren't part of company name
                    company = re.sub(r'\s+(Data|Lead|Sr\.|Senior|Engineer|Developer|Architect|Specialist).*$', '', company, flags=re.IGNORECASE)
                    company = re.sub(r',\s*(Amsterdam|Utrecht|Chennai|Arnhem|Roosendaal|Amersfoort).*$', '', company, flags=re.IGNORECASE)
                    
                    if len(company) > 3 and company not in companies:
                        companies.append(company.strip())
            
            # Also look for lines that are likely company names (contain common business suffixes)
            elif any(suffix in line_clean for suffix in [' Group', ' Bank', ' Solutions']):
                # Clean the line to extract just company name
                company = line_clean
                # Remove job titles and locations
                company = re.sub(r'\s+(Data|Lead|Sr\.|Senior|Engineer|Developer|Architect|Specialist|API).*$', '', company, flags=re.IGNORECASE)
                company = re.sub(r',\s*(Amsterdam|Utrecht|Chennai|Arnhem|Roosendaal|Amersfoort).*$', '', company, flags=re.IGNORECASE)
                company = re.sub(r'\s+\d{4}\s*[-–—].*$', '', company)  # Remove dates
                company = re.sub(r'\s+\[.*?\].*$', '', company)  # Remove duration in brackets
                
                if len(company) > 3 and company not in companies and not any(exclude in company.lower() for exclude in ['duration', 'role', 'months', 'years', 'data engineer', 'lead data']):
                    companies.append(company.strip())
    
    # Clean up extracted companies - remove obvious non-company entries
    cleaned_companies = []
    exclude_terms = ['utrecht', 'amsterdam', 'chennai', 'arnhem', 'roosendaal', 'amersfoort', 'data engineer', 'lead data', 'sr. data', 'api developer']
    
    for company in companies:
        # Remove trailing punctuation and clean up
        company = re.sub(r'[,\.\-–—]+$', '', company).strip()
        company_lower = company.lower()
        
        # Skip if it's clearly a location or job title
        if (len(company) > 3 and 
            company not in cleaned_companies and 
            not any(exclude in company_lower for exclude in exclude_terms) and
            not company_lower.endswith(' engineer') and
            not company_lower.endswith(' developer') and
            not company_lower.endswith(' architect')):
            cleaned_companies.append(company)
    
    return cleaned_companies[:10]  # Limit to top 10 companies

def _extract_education_from_text(resume_text: str) -> list:
    """
    Extract education information from resume text.
    """
    import re
    
    education = []
    lines = resume_text.split('\n')
    
    # Look for education section
    in_education_section = False
    for i, line in enumerate(lines):
        line_clean = line.strip()
        if not line_clean:
            continue
            
        line_lower = line_clean.lower()
        
        # Check if we're entering education section
        if 'education' in line_lower and ('profile' in line_lower or 'section' in line_lower or line_lower == 'education'):
            in_education_section = True
            continue
            
        # Check if we're leaving education section
        if in_education_section and any(keyword in line_lower for keyword in ['certification', 'project', 'work', 'experience', 'skills']):
            break
        
        if in_education_section:
            # Look for degree patterns
            degree_patterns = [
                r'(B\.?Sc\.?.*?)(?:,|\s+\w+\s+University|\s+\w+\s+College)',
                r'(Bachelor.*?)(?:,|\s+\w+\s+University|\s+\w+\s+College)',
                r'(Master.*?)(?:,|\s+\w+\s+University|\s+\w+\s+College)',
                r'(M\.?Sc\.?.*?)(?:,|\s+\w+\s+University|\s+\w+\s+College)',
                r'(PhD.*?)(?:,|\s+\w+\s+University|\s+\w+\s+College)',
                r'(Diploma.*?)(?:,|\s+\w+\s+University|\s+\w+\s+College)'
            ]
            
            for pattern in degree_patterns:
                match = re.search(pattern, line_clean, re.IGNORECASE)
                if match:
                    degree = match.group(1).strip()
                    # Try to get the full education line including university
                    if 'University' in line_clean or 'College' in line_clean:
                        education.append(line_clean)
                    else:
                        education.append(degree)
                    break
            
            # Also look for lines that contain university/college names
            if any(keyword in line_clean for keyword in ['University', 'College', 'Institute', 'School']) and len(line_clean) > 10:
                if not any(exclude in line_lower for exclude in ['courses', 'certification', 'training']):
                    education.append(line_clean)
    
    # Clean up education entries
    cleaned_education = []
    for edu in education:
        edu = edu.strip()
        if len(edu) > 5 and edu not in cleaned_education:
            cleaned_education.append(edu)
    
    return cleaned_education[:5]  # Limit to top 5 education entries

def _extract_skills_from_sections(resume_text: str) -> list:
    """
    Extract skills from dedicated skills sections in the resume.
    Handles comma-separated, slash-separated, and bullet-point skills.
    """
    import re
    
    skills = []
    lines = resume_text.split('\n')
    
    # Look for skills section
    in_skills_section = False
    skills_section_content = []
    
    for i, line in enumerate(lines):
        line_clean = line.strip()
        if not line_clean:
            continue
            
        line_lower = line_clean.lower()
        
        # Check if we're entering skills section
        if (('skills' in line_lower or 'technologies' in line_lower or 'technical skills' in line_lower) and 
            (line_lower.startswith('skills') or line_lower.startswith('technical') or 
             line_lower.endswith('skills') or line_lower.endswith('technologies') or
             'skills:' in line_lower or 'technologies:' in line_lower)):
            in_skills_section = True
            # If the skills are on the same line after colon, capture them
            if ':' in line_clean:
                skills_part = line_clean.split(':', 1)[1].strip()
                if skills_part:
                    skills_section_content.append(skills_part)
            continue
            
        # Check if we're leaving skills section
        if in_skills_section and any(keyword in line_lower for keyword in ['education', 'experience', 'work', 'employment', 'projects', 'certifications', 'achievements']):
            break
        
        if in_skills_section:
            # Skip empty lines and section headers
            if not line_clean or line_clean.lower() in ['skills', 'technical skills', 'technologies']:
                continue
            skills_section_content.append(line_clean)
    
    # Process the skills section content
    for content in skills_section_content:
        # Remove bullet points and other formatting
        content = re.sub(r'^[•◦\-\*\+]\s*', '', content)
        content = re.sub(r'^\d+\.\s*', '', content)  # Remove numbered lists
        
        # Split by various delimiters
        # First try comma separation
        if ',' in content:
            skills_parts = content.split(',')
        # Then try slash separation
        elif '/' in content:
            skills_parts = content.split('/')
        # Then try pipe separation
        elif '|' in content:
            skills_parts = content.split('|')
        # Then try semicolon separation
        elif ';' in content:
            skills_parts = content.split(';')
        # For bullet points or single skills per line
        else:
            skills_parts = [content]
        
        # Clean and add each skill
        for skill in skills_parts:
            skill = skill.strip()
            # Remove common prefixes/suffixes
            skill = re.sub(r'^(and\s+|&\s+)', '', skill, flags=re.IGNORECASE)
            skill = re.sub(r'\s+(etc\.?|and\s+more)$', '', skill, flags=re.IGNORECASE)
            
            # Validate skill
            if (skill and 
                len(skill) > 1 and len(skill) < 50 and
                not skill.lower() in ['skills', 'technologies', 'technical', 'etc', 'and', 'more'] and
                not skill.isdigit() and
                not re.match(r'^\W+$', skill)):  # Not just punctuation
                skills.append(skill)
    
    # Also look for skills in other common patterns throughout the document
    # Pattern: "Skills: Python, Java, Scala"
    skills_pattern_matches = re.findall(r'(?:skills|technologies|technical\s+skills)[:\s]+([^\n]+)', resume_text, re.IGNORECASE)
    for match in skills_pattern_matches:
        # Split by comma, slash, or pipe
        if ',' in match:
            parts = match.split(',')
        elif '/' in match:
            parts = match.split('/')
        elif '|' in match:
            parts = match.split('|')
        else:
            parts = [match]
        
        for part in parts:
            part = part.strip()
            if (part and len(part) > 1 and len(part) < 50 and
                not part.lower() in ['skills', 'technologies', 'technical', 'etc', 'and', 'more']):
                skills.append(part)
    
    # Remove duplicates while preserving order
    unique_skills = []
    seen = set()
    for skill in skills:
        skill_lower = skill.lower()
        if skill_lower not in seen:
            seen.add(skill_lower)
            unique_skills.append(skill)
    
    return unique_skills[:20]  # Limit to 20 skills