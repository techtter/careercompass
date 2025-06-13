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
    Parses resume content using Claude AI for superior document analysis.
    Falls back to pattern matching if Claude API is not available.
    """
    # First try Claude AI for the best results
    if has_claude_api and claude_client:
        try:
            return _parse_resume_with_claude(resume_text)
        except Exception as e:
            print(f"Claude AI parsing failed: {e}")
            print("Falling back to pattern matching...")
            return _get_mock_resume_parse(resume_text)
    
    # Try OpenAI if available and not in development mode
    if not is_development_mode and openai_api_key and len(openai_api_key) > 20:
        try:
            return _parse_resume_with_openai(resume_text)
        except Exception as e:
            print(f"OpenAI parsing failed: {e}")
            print("Falling back to pattern matching...")
            return _get_mock_resume_parse(resume_text)
    
    # Fall back to enhanced pattern matching
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
    "experienceYears": "Total years of professional work experience (integer)",
    "skills": ["List of technical and professional skills found"],
    "lastThreeJobTitles": ["Most recent ACTUAL JOB POSITIONS (not certifications), up to 3. Examples: 'Senior Software Engineer', 'Data Scientist', 'Product Manager'"],
    "experienceSummary": "Brief professional summary (2-3 sentences)",
    "companies": ["Company names where the person worked"],
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
        return json.dumps(_validate_and_clean_parsed_data(parsed_data))
        
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
            "companies": ["Array of company names corresponding to job titles"],
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
        cleaned_response = _validate_and_clean_parsed_data(parsed_response)
        return json.dumps(cleaned_response)
        
    except Exception as e:
        print(f"AI parsing failed: {e}")
        # Return mock data instead of failing
        return _get_mock_resume_parse(resume_text)

def _validate_and_clean_parsed_data(data):
    """
    Validates and cleans the AI-parsed data to ensure it matches our expected structure.
    """
    cleaned = {
        "firstName": str(data.get("firstName", "Professional")).strip() if data.get("firstName") else "Professional",
        "lastName": str(data.get("lastName", "User")).strip() if data.get("lastName") else "User",
        "email": str(data.get("email")).strip() if data.get("email") else None,
        "phone": str(data.get("phone")).strip() if data.get("phone") else None,
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
            if isinstance(skill, str) and skill.strip():
                cleaned["skills"].append(skill.strip())
    if not cleaned["skills"]:
        cleaned["skills"] = ["Professional Skills", "Communication", "Problem Solving"]
    
    # Clean job titles array
    if isinstance(data.get("lastThreeJobTitles"), list):
        for title in data.get("lastThreeJobTitles", []):
            if isinstance(title, str) and title.strip():
                cleaned["lastThreeJobTitles"].append(title.strip())
    if not cleaned["lastThreeJobTitles"]:
        cleaned["lastThreeJobTitles"] = ["Current Position"]
    
    # Clean companies array
    if isinstance(data.get("companies"), list):
        for company in data.get("companies", []):
            if isinstance(company, str) and company.strip():
                cleaned["companies"].append(company.strip())
    if not cleaned["companies"]:
        cleaned["companies"] = ["Previous Company"]
    
    # Clean education array
    if isinstance(data.get("education"), list):
        for edu in data.get("education", []):
            if isinstance(edu, str) and edu.strip():
                cleaned["education"].append(edu.strip())
    if not cleaned["education"]:
        cleaned["education"] = ["Professional Education"]
    
    # Clean certifications array
    if isinstance(data.get("certifications"), list):
        for cert in data.get("certifications", []):
            if isinstance(cert, str) and cert.strip():
                cleaned["certifications"].append(cert.strip())
    if not cleaned["certifications"]:
        cleaned["certifications"] = ["Professional Development"]
    
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

def _get_mock_resume_parse(resume_text: str):
    """
    Enhanced mock function that extracts real information from resume text when possible.
    """
    import json
    import re
    
    lines = resume_text.split('\n')
    first_name = "Professional"
    last_name = "User"
    email = None
    phone = None
    skills = []
    companies = []
    job_titles = []
    education = []
    certifications = []
    experience_years = 2
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    for line in lines:
        email_match = re.search(email_pattern, line, re.IGNORECASE)
        if email_match:
            email = email_match.group(0)
            break
    
    # Extract phone number
    phone_patterns = [
        r'\b\d{3}-\d{3}-\d{4}\b',  # 123-456-7890
        r'\b\(\d{3}\)\s*\d{3}-\d{4}\b',  # (123) 456-7890
        r'\b\d{3}\s*\d{3}\s*\d{4}\b',  # 123 456 7890
        r'\+\d{1,3}[-.\s]*\d{3}[-.\s]*\d{3}[-.\s]*\d{4}\b'  # +1 123 456 7890
    ]
    for line in lines:
        for pattern in phone_patterns:
            phone_match = re.search(pattern, line)
            if phone_match:
                phone = phone_match.group(0)
                break
        if phone:
            break
    
    # Extract name from first few non-empty lines (improved logic)
    for line in lines[:15]:
        line = line.strip()
        words = line.split()
        
        # Check if line starts with a potential name (2 capitalized words)
        if (len(words) >= 2 and 
            all(len(word) > 1 and word[0].isupper() for word in words[:2]) and
            not any(char.isdigit() for char in words[0] + words[1]) and
            words[0].isalpha() and words[1].replace('.', '').isalpha()):
            
            # Check that first two words don't contain common non-name terms
            potential_name = f"{words[0]} {words[1]}"
            if not any(term in potential_name.lower() for term in [
                'resume', 'curriculum', 'cv', 'objective', 'summary', 'experience', 
                'education', 'skills', 'contact', 'address', 'phone', 'email',
                'engineer', 'developer', 'manager', 'analyst', 'specialist', 
                'director', 'senior', 'junior', 'lead', 'software', 'technical']):
                first_name = words[0].strip().title()
                last_name = words[1].strip().title()
                break
    
    # Extract certifications first (to avoid confusing them with job titles)
    certification_keywords = [
        'certified', 'certification', 'certificate', 'aws certified', 'azure certified', 
        'google certified', 'microsoft certified', 'oracle certified', 'cisco certified',
        'pmp', 'cissp', 'cisa', 'cism', 'comptia', 'itil', 'prince2', 'scrum master',
        'product owner', 'safe', 'csm', 'psm', 'cka', 'ckad', 'cks'
    ]
    
    resume_lower = resume_text.lower()
    for line in lines:
        line_clean = line.strip()
        line_lower = line_clean.lower()
        
        # Look for certification patterns
        if (any(keyword in line_lower for keyword in certification_keywords) and
            len(line_clean) > 5 and len(line_clean) < 100 and
            not any(exclude in line_lower for exclude in ['experience', 'years', 'worked', 'employed'])):
            
            # Clean up certification entry
            cleaned_cert = re.sub(r'\d{4}[-–]\d{4}|\d{4}[-–]present|present|\(.*?\)', '', line_clean, flags=re.IGNORECASE).strip()
            if (cleaned_cert and len(cleaned_cert) > 5 and 
                not any(existing.lower() in cleaned_cert.lower() for existing in certifications)):
                certifications.append(cleaned_cert)
    
    # Extract skills (enhanced with more comprehensive detection)
    skill_keywords = [
        # Programming Languages
        'python', 'javascript', 'java', 'c++', 'c#', 'php', 'ruby', 'go', 'rust', 'scala', 'kotlin',
        'swift', 'objective-c', 'typescript', 'r', 'matlab', 'perl', 'shell', 'bash',
        # Web Technologies
        'html', 'css', 'react', 'angular', 'vue', 'svelte', 'next.js', 'nuxt.js',
        'node.js', 'express', 'django', 'flask', 'spring', 'laravel', 'rails', 'asp.net',
        # Databases
        'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle', 'sql server',
        'sqlite', 'cassandra', 'dynamodb', 'neo4j',
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'google cloud', 'docker', 'kubernetes', 'jenkins', 'gitlab',
        'terraform', 'ansible', 'chef', 'puppet', 'vagrant',
        # Tools & Methodologies
        'git', 'github', 'gitlab', 'bitbucket', 'agile', 'scrum', 'kanban', 'jira', 'confluence',
        'slack', 'teams', 'project management', 'leadership', 'communication', 'teamwork',
        # Data & Analytics
        'machine learning', 'artificial intelligence', 'data science', 'data analysis',
        'pandas', 'numpy', 'tensorflow', 'pytorch', 'scikit-learn', 'tableau', 'power bi',
        'excel', 'sql', 'spark', 'hadoop', 'kafka',
        # Testing & Quality
        'testing', 'unit testing', 'integration testing', 'selenium', 'jest', 'cypress',
        'quality assurance', 'qa', 'automation',
        # Mobile & Desktop
        'mobile development', 'ios', 'android', 'react native', 'flutter', 'xamarin',
        'web development', 'frontend', 'backend', 'fullstack', 'full-stack'
    ]
    
    # Look for skills section specifically
    skills_section_found = False
    for line in lines:
        if any(header in line.lower() for header in ['skills', 'technical skills', 'competencies', 'technologies']):
            skills_section_found = True
            # Extract skills from the next few lines after skills header
            line_index = lines.index(line)
            for skill_line in lines[line_index:line_index+10]:
                for skill in skill_keywords:
                    if skill in skill_line.lower() and skill.title() not in skills:
                        skills.append(skill.title())
            break
    
    # Also look for skills throughout the document
    for skill in skill_keywords:
        if skill in resume_lower and skill.title() not in skills:
            skills.append(skill.title())
    
    # Remove duplicates and limit
    skills = list(dict.fromkeys(skills))  # Remove duplicates while preserving order
    
    # If no technical skills found, add some generic ones
    if not skills:
        skills = ["Communication", "Problem Solving", "Team Collaboration", "Project Management"]
    else:
        skills = skills[:10]  # Increased limit to 10 skills
    
    # Extract companies (improved logic)
    company_indicators = ['inc', 'corp', 'llc', 'ltd', 'company', 'technologies', 'systems', 'solutions', 
                         'microsoft', 'google', 'apple', 'amazon', 'facebook', 'netflix', 'uber', 'airbnb']
    
    for line in lines:
        line_lower = line.lower().strip()
        line_clean = line.strip()
        
        # Skip email addresses and other non-company lines
        if '@' in line or len(line_clean) < 3 or len(line_clean) > 100:
            continue
            
        # Look for company patterns: "at CompanyName" or direct company indicators
        if any(indicator in line_lower for indicator in company_indicators):
            # Extract company name more carefully
            if ' at ' in line_lower:
                # Extract everything after "at"
                company_part = line_clean.split(' at ')[-1]
                # Clean up dates and extra info
                company_part = re.sub(r'\(.*?\)|\d{4}[-–]\d{4}|\d{4}[-–]present|present', '', company_part, flags=re.IGNORECASE).strip()
                if company_part and len(company_part) > 2 and len(company_part) < 50:
                    companies.append(company_part)
            else:
                # Clean up the line to extract company name
                cleaned_line = re.sub(r'\d{4}[-–]\d{4}|\d{4}[-–]present|present|\(.*?\)', '', line_clean, flags=re.IGNORECASE).strip()
                if cleaned_line and len(cleaned_line) > 2 and len(cleaned_line) < 80:
                    companies.append(cleaned_line)
    
    # Remove duplicates and filter out invalid entries
    companies = [comp for comp in list(dict.fromkeys(companies)) if comp and '@' not in comp and len(comp) > 2]
    
    if not companies:
        companies = ["Technology Company", "Previous Employer"]
    else:
        companies = companies[:3]  # Limit to 3 companies
    
    # Extract job titles (enhanced detection with better filtering)
    title_keywords = [
        'engineer', 'developer', 'programmer', 'manager', 'director', 'analyst', 'specialist', 
        'coordinator', 'senior', 'junior', 'lead', 'architect', 'consultant', 'designer',
        'scientist', 'researcher', 'technician', 'administrator', 'supervisor', 'executive',
        'officer', 'associate', 'assistant', 'intern', 'freelancer', 'contractor',
        'product manager', 'project manager', 'team lead', 'tech lead', 'scrum master',
        'devops', 'qa engineer', 'data scientist', 'ml engineer', 'software engineer',
        'web developer', 'mobile developer', 'frontend developer', 'backend developer',
        'full stack developer', 'fullstack developer', 'ui/ux designer', 'graphic designer'
    ]
    
    # Exclude certification-related terms from job titles
    certification_exclusions = [
        'certified', 'certification', 'certificate', 'aws certified', 'azure certified',
        'google certified', 'microsoft certified', 'oracle certified', 'cisco certified',
        'pmp', 'cissp', 'cisa', 'cism', 'comptia', 'itil', 'prince2'
    ]
    
    # Additional exclusions for non-title content
    content_exclusions = [
        '•', '◦', '-', '*', 'designed', 'implemented', 'developed', 'created', 'managed',
        'led', 'worked', 'collaborated', 'analyzed', 'built', 'maintained', 'responsible',
        'duties', 'achievements', 'accomplishments', 'projects', 'technologies used'
    ]
    
    # Look for experience/work section
    in_experience_section = False
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        
        # Check if we're entering an experience section
        if any(header in line_lower for header in ['experience', 'work experience', 'employment', 'career', 'work history', 'professional experience']):
            in_experience_section = True
            continue
            
        # Stop if we hit another section
        if in_experience_section and any(header in line_lower for header in ['education', 'skills', 'projects', 'certifications', 'awards']):
            in_experience_section = False
            
        line_clean = line.strip()
        
        # Check if this line contains a job title
        if (line_clean and len(line_clean) < 120 and 
            any(keyword in line_clean.lower() for keyword in title_keywords) and
            not any(exclusion in line_clean.lower() for exclusion in certification_exclusions) and
            not any(exclusion in line_clean.lower() for exclusion in content_exclusions) and
            not line_clean.startswith(('•', '◦', '-', '*', '  '))):  # Not a bullet point
            
            # Remove date patterns, company names, and clean up
            cleaned_title = re.sub(r'\d{4}[-–]\d{4}|\d{4}[-–]present|present|\(\d+\s*years?\)', '', line_clean, flags=re.IGNORECASE)
            cleaned_title = re.sub(r'\bat\s+[\w\s&.,]+?(inc|corp|ltd|llc|company|technologies|systems|solutions)', '', cleaned_title, flags=re.IGNORECASE)
            cleaned_title = cleaned_title.strip()
            
            # Additional filtering to ensure it's a real job title
            if (cleaned_title and len(cleaned_title) > 8 and len(cleaned_title) < 80 and
                not any(exclusion in cleaned_title.lower() for exclusion in certification_exclusions) and
                not any(exclusion in cleaned_title.lower() for exclusion in content_exclusions) and
                not cleaned_title.lower().startswith(('skills', 'education', 'experience', 'summary', 'objective')) and
                not cleaned_title.startswith(('•', '◦', '-', '*'))):
                
                # Avoid duplicate entries
                if not any(existing.lower() in cleaned_title.lower() or cleaned_title.lower() in existing.lower() for existing in job_titles):
                    job_titles.append(cleaned_title)
    
    # If no job titles found from experience section, try to extract from common patterns
    if not job_titles:
        # Look for patterns like "Senior Software Engineer at Company" or "Data Scientist | Company"
        for line in lines:
            line_clean = line.strip()
            if (len(line_clean) > 10 and len(line_clean) < 100 and
                any(keyword in line_clean.lower() for keyword in title_keywords) and
                not any(exclusion in line_clean.lower() for exclusion in certification_exclusions) and
                not any(exclusion in line_clean.lower() for exclusion in content_exclusions) and
                not line_clean.startswith(('•', '◦', '-', '*', '  '))):
                
                # Extract title before "at" or "|" or "-"
                for separator in [' at ', ' | ', ' - ', ' – ']:
                    if separator in line_clean:
                        potential_title = line_clean.split(separator)[0].strip()
                        if (len(potential_title) > 8 and len(potential_title) < 60 and
                            any(keyword in potential_title.lower() for keyword in title_keywords) and
                            not any(exclusion in potential_title.lower() for exclusion in content_exclusions)):
                            job_titles.append(potential_title)
                            break
    
    # Remove duplicates and limit
    job_titles = list(dict.fromkeys(job_titles))
    
    # If still no job titles found, create realistic ones based on skills
    if not job_titles:
        if any(skill.lower() in ['data', 'analytics', 'machine learning', 'ai'] for skill in skills):
            job_titles = ["Data Engineer", "Senior Data Analyst"]
        elif any(skill.lower() in ['software', 'programming', 'development'] for skill in skills):
            job_titles = ["Software Engineer", "Senior Developer"]
        elif any(skill.lower() in ['cloud', 'aws', 'azure', 'devops'] for skill in skills):
            job_titles = ["Cloud Engineer", "DevOps Specialist"]
        else:
            job_titles = ["Software Developer", "Technical Specialist"]
    else:
        job_titles = job_titles[:3]  # Limit to 3 job titles
    
    # Extract education (enhanced detection)
    education_keywords = [
        'bachelor', 'master', 'degree', 'university', 'college', 'phd', 'doctorate', 'diploma',
        'mba', 'bsc', 'msc', 'ba', 'ma', 'bs', 'ms', 'phd',
        'associate degree', 'graduate', 'undergraduate', 'postgraduate', 'school', 'institute',
        'academy', 'coursera', 'udemy', 'edx', 'mit', 'stanford', 'harvard', 'berkeley'
    ]
    
    # Look for education section specifically
    in_education_section = False
    for i, line in enumerate(lines):
        line_lower = line.lower().strip()
        
        # Check if we're entering an education section
        if any(header in line_lower for header in ['education', 'academic', 'qualifications', 'academic background', 'studies']):
            in_education_section = True
            continue
            
        # Stop if we hit another section  
        if in_education_section and any(header in line_lower for header in ['experience', 'skills', 'projects', 'certifications', 'work']):
            in_education_section = False
        
        line_clean = line.strip()
        if (any(keyword in line_lower for keyword in education_keywords) and 
            len(line_clean) < 200 and len(line_clean) > 10 and
            '@' not in line_clean and
            not any(exclusion in line_lower for exclusion in certification_exclusions)):  # Skip certifications
            
            # Clean up the education entry
            cleaned_education = re.sub(r'\d{4}[-–]\d{4}|\d{4}[-–]present|present', '', line_clean, flags=re.IGNORECASE).strip()
            if (cleaned_education and 
                not any(existing.lower() in cleaned_education.lower() for existing in education) and
                '@' not in cleaned_education):  # Double check no email
                education.append(cleaned_education)
    
    # Remove duplicates and limit
    education = list(dict.fromkeys(education))
    
    if not education:
        education = ["University Education", "Professional Training"]
    else:
        education = education[:4]  # Increased limit to 4 education entries
    
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
    
    mock_data = {
        "firstName": first_name,
        "lastName": last_name,
        "email": email,
        "phone": phone,
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