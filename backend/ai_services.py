import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import re

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key with fallback
openai_api_key = os.getenv("OPENAI_API_KEY")
is_development_mode = not openai_api_key or openai_api_key in ['placeholder', 'test_key', 'your_api_key_here'] or len(openai_api_key) < 20

if not openai_api_key:
    print("Warning: OPENAI_API_KEY not set. Running in development mode with mock responses.")
    is_development_mode = True
elif openai_api_key in ['placeholder', 'test_key', 'your_api_key_here'] or len(openai_api_key) < 20:
    print("Warning: Using placeholder OpenAI API key. Running in development mode with mock responses.")
    is_development_mode = True
else:
    print(f"✅ Using real OpenAI API key (ends with: ...{openai_api_key[-8:]}) - AI parsing enabled")

# Initialize LLM only if we have a real API key
if not is_development_mode:
    llm = ChatOpenAI(temperature=0.7, model_name="gpt-4")
else:
    llm = None
    print("Development mode: AI services will return mock data")

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
    Parses resume content using AI and returns structured data.
    Simplified to rely purely on AI parsing without regex fallbacks.
    """
    if is_development_mode:
        return _get_mock_resume_parse(resume_text)

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

    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(resume_text=resume_text)
    
    try:
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
        # Return a simple fallback with basic information
        return _get_simple_fallback_parse(resume_text)

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
    
    # Extract name from first few non-empty lines
    for line in lines[:10]:
        line = line.strip()
        if (line and len(line.split()) >= 2 and len(line) < 50 and 
            '@' not in line and not any(char.isdigit() for char in line) and
            not line.lower().startswith(('resume', 'curriculum', 'cv', 'email', 'phone', 'address'))):
            words = line.split()
            if len(words) >= 2 and all(len(word) > 1 for word in words[:2]):
                first_name = words[0].strip().title()
                last_name = ' '.join(words[1:]).strip().title()
                break
    
    # Extract skills (look for technical keywords)
    skill_keywords = [
        'python', 'javascript', 'java', 'c++', 'html', 'css', 'react', 'angular', 'vue',
        'node.js', 'express', 'django', 'flask', 'spring', 'mysql', 'postgresql', 'mongodb',
        'aws', 'azure', 'docker', 'kubernetes', 'git', 'agile', 'scrum', 'project management',
        'leadership', 'communication', 'teamwork', 'problem solving', 'data analysis',
        'machine learning', 'artificial intelligence', 'web development', 'mobile development'
    ]
    
    resume_lower = resume_text.lower()
    for skill in skill_keywords:
        if skill in resume_lower:
            skills.append(skill.title())
    
    # If no technical skills found, add some generic ones
    if not skills:
        skills = ["Communication", "Problem Solving", "Team Collaboration", "Project Management"]
    else:
        skills = skills[:8]  # Limit to 8 skills
    
    # Extract companies (look for common company indicators)
    company_indicators = ['inc', 'corp', 'llc', 'ltd', 'company', 'technologies', 'systems', 'solutions']
    for line in lines:
        line_lower = line.lower().strip()
        if any(indicator in line_lower for indicator in company_indicators):
            # Clean up the line to extract company name
            cleaned_line = re.sub(r'\d{4}[-–]\d{4}|\d{4}[-–]present|present', '', line, flags=re.IGNORECASE).strip()
            if cleaned_line and len(cleaned_line) < 100:
                companies.append(cleaned_line.strip())
    
    if not companies:
        companies = ["Previous Company", "Current Organization"]
    else:
        companies = companies[:3]  # Limit to 3 companies
    
    # Extract job titles (look for lines that might be job titles)
    title_keywords = ['engineer', 'developer', 'manager', 'analyst', 'specialist', 'coordinator', 
                     'director', 'senior', 'junior', 'lead', 'architect', 'consultant']
    for line in lines:
        line_clean = line.strip()
        if (line_clean and len(line_clean) < 100 and 
            any(keyword in line_clean.lower() for keyword in title_keywords)):
            # Remove date patterns from job titles
            cleaned_title = re.sub(r'\d{4}[-–]\d{4}|\d{4}[-–]present|present|\(\d+\s*years?\)', '', line_clean, flags=re.IGNORECASE).strip()
            if cleaned_title and len(cleaned_title) > 5:
                job_titles.append(cleaned_title)
    
    if not job_titles:
        job_titles = ["Software Developer", "Technical Analyst"]
    else:
        job_titles = job_titles[:3]  # Limit to 3 job titles
    
    # Extract education (look for degree keywords)
    education_keywords = ['bachelor', 'master', 'degree', 'university', 'college', 'phd', 'doctorate', 'certificate']
    for line in lines:
        line_lower = line.lower().strip()
        if any(keyword in line_lower for keyword in education_keywords) and len(line.strip()) < 150:
            education.append(line.strip())
    
    if not education:
        education = ["Bachelor's Degree in Computer Science"]
    else:
        education = education[:3]  # Limit to 3 education entries
    
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
        "certifications": ["Professional Development", "Industry Training"]
    }
    
    return json.dumps(mock_data)

def generate_career_path(job_title: str, experience: str, skills: list[str]):
    """
    Generates a personalized career path recommendation using an AI model.
    """
    if is_development_mode:
        return _get_mock_career_path(job_title, experience, skills)
    
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

def analyze_skill_gap(skills: list[str], job_description: str):
    """
    Analyzes the gap between a user's skills and a job description.
    """
    if is_development_mode:
        return _get_mock_skill_gap(skills, job_description)
    
    prompt = PromptTemplate(
        input_variables=["skills", "job_description"],
        template="""
        As a career advisor, analyze the skill gap between the user's current skills and the provided job description.

        User's Skills: {skills}

        Job Description:
        {job_description}

        Please provide the following:
        1.  **Missing Skills:** List the key skills required by the job that are missing from the user's skill set.
        2.  **Skill Enhancement:** Suggest areas where the user's existing skills can be improved to better match the job requirements.
        3.  **Learning Recommendations:** For each missing skill, recommend a type of learning resource (e.g., online course, certification, book) and suggest a specific platform or provider (e.g., Coursera, Udemy, Pluralsight).

        Present the information in a clear, structured format.
        """
    )

    skill_str = ", ".join(skills)
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(skills=skill_str, job_description=job_description)

    return response

def optimize_resume(resume_text: str, job_description: str):
    """
    Optimizes a user's resume for a specific job description.
    """
    if is_development_mode:
        return _get_mock_resume_optimization(resume_text, job_description)
    
    prompt = PromptTemplate(
        input_variables=["resume_text", "job_description"],
        template="""
        As a professional resume writer and career coach, please analyze the following resume and job description. Provide actionable advice to optimize the resume for this specific role.

        User's Resume:
        {resume_text}

        Job Description:
        {job_description}

        Please provide the following:
        1.  **Keyword Optimization:** Identify and suggest incorporating 5-7 key terms from the job description that are missing in the resume.
        2.  **Impactful Bullet Points:** Rewrite 3-5 bullet points from the resume to be more results-oriented, using the STAR (Situation, Task, Action, Result) method.
        3.  **Summary/Objective Statement:** Suggest a tailored summary or objective statement (2-3 sentences) that aligns with the job description.
        4.  **Overall Feedback:** Provide a brief overall assessment of the resume's strengths and weaknesses in relation to the job.

        Present the information in a clear, structured, and easy-to-read format.
        """
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(resume_text=resume_text, job_description=job_description)

    return response 