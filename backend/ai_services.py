import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Load environment variables from .env file
load_dotenv()

# Make sure to set your OPENAI_API_KEY in your .env file
# You can get your key from https://platform.openai.com/account/api-keys

if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

llm = ChatOpenAI(temperature=0.7, model_name="gpt-4")

def generate_career_path(job_title: str, experience: str, skills: list[str]):
    """
    Generates a personalized career path recommendation using an AI model.
    """
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

def parse_resume_content(resume_text: str):
    """
    Intelligently parses resume content using AI to extract structured information.
    """
    prompt = PromptTemplate(
        input_variables=["resume_text"],
        template="""
        As an expert resume parser, analyze the following resume text and extract key information in a structured JSON format.

        Resume Text:
        {resume_text}

        Please extract and return the following information in a JSON format:
        {{
            "name": "Full name of the person",
            "email": "Email address if available",
            "phone": "Phone number if available", 
            "location": "Location/address if available",
            "experience": "Total years of experience (estimate if not explicit)",
            "skills": ["array", "of", "technical", "and", "professional", "skills"],
            "lastTwoJobs": ["Most recent job title", "Second most recent job title"],
            "education": "Highest education level or most relevant degree",
            "summary": "Brief professional summary (2-3 sentences)"
        }}

        Instructions:
        - If information is not available, use null for that field
        - For experience, provide your best estimate in years (e.g., "5 years", "2-3 years")
        - For skills, include both technical and soft skills mentioned
        - For lastTwoJobs, extract the actual job titles, not company names
        - Return only valid JSON, no additional text or explanations
        """
    )

    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.run(resume_text=resume_text)
    
    return response 