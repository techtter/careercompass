#!/usr/bin/env python3
"""
Test script to demonstrate improved job title extraction
"""

import sys
import os
sys.path.append('backend')

from ai_services import _get_mock_resume_parse
import json

# Sample resume text with mixed job titles and certifications
sample_resume = """
Redde Pidugu
Senior Data Engineer
Email: rpidugu99@gmail.com
Phone: +31687222631

PROFESSIONAL EXPERIENCE

Lead Data Engineer / Solution Architect
DataTech Solutions Inc.
2020 - Present
• Designed and implemented large-scale data pipelines
• Led a team of 5 engineers in developing cloud-native solutions
• Architected microservices-based data processing systems

Senior Software Engineer
TechCorp Systems
2018 - 2020
• Developed scalable web applications using Python and Java
• Implemented CI/CD pipelines and DevOps practices
• Mentored junior developers and conducted code reviews

Data Analyst
Analytics Pro
2016 - 2018
• Analyzed large datasets to derive business insights
• Created dashboards and reports for stakeholders
• Worked with SQL, Python, and visualization tools

SKILLS
Python, Java, Scala, Apache Spark, Kafka, AWS, Azure, SQL, NoSQL, 
Machine Learning, Data Engineering, Microservices, DevOps

CERTIFICATIONS
• AWS Certified Solutions Architect - Professional
• Azure Certified Data Engineer Associate
• Google Cloud Professional Data Engineer
• Certified Kubernetes Administrator (CKA)
• PMP - Project Management Professional

EDUCATION
Master of Science in Computer Science
Stanford University, 2016

Bachelor of Engineering in Computer Science
University of Technology, 2014
"""

def test_job_title_extraction():
    """Test the improved job title extraction"""
    print("Testing improved job title extraction...")
    print("=" * 60)
    
    # Parse the resume
    result = _get_mock_resume_parse(sample_resume)
    parsed_data = json.loads(result)
    
    print("EXTRACTED DATA:")
    print("-" * 30)
    print(f"Name: {parsed_data['firstName']} {parsed_data['lastName']}")
    print(f"Email: {parsed_data['email']}")
    print(f"Phone: {parsed_data['phone']}")
    print(f"Experience Years: {parsed_data['experienceYears']}")
    
    print("\nJOB TITLES (lastThreeJobTitles):")
    for i, title in enumerate(parsed_data['lastThreeJobTitles'], 1):
        print(f"  {i}. {title}")
    
    print("\nCERTIFICATIONS:")
    for i, cert in enumerate(parsed_data['certifications'], 1):
        print(f"  {i}. {cert}")
    
    print("\nSKILLS:")
    skills_str = ", ".join(parsed_data['skills'][:10])  # Show first 10 skills
    print(f"  {skills_str}")
    if len(parsed_data['skills']) > 10:
        print(f"  ... and {len(parsed_data['skills']) - 10} more")
    
    print("\nCOMPANIES:")
    for i, company in enumerate(parsed_data['companies'], 1):
        print(f"  {i}. {company}")
    
    print("\nEDUCATION:")
    for i, edu in enumerate(parsed_data['education'], 1):
        print(f"  {i}. {edu}")
    
    print("\n" + "=" * 60)
    print("ANALYSIS:")
    print("-" * 30)
    
    # Check if job titles are correctly separated from certifications
    job_titles = parsed_data['lastThreeJobTitles']
    certifications = parsed_data['certifications']
    
    # Check for certification keywords in job titles (should be minimal)
    cert_keywords = ['certified', 'certification', 'certificate']
    job_titles_with_cert_keywords = [
        title for title in job_titles 
        if any(keyword in title.lower() for keyword in cert_keywords)
    ]
    
    # Check for job keywords in certifications (should be minimal)
    job_keywords = ['engineer', 'developer', 'manager', 'analyst', 'architect']
    certs_with_job_keywords = [
        cert for cert in certifications 
        if any(keyword in cert.lower() for keyword in job_keywords)
        and not any(cert_keyword in cert.lower() for cert_keyword in cert_keywords)
    ]
    
    print(f"✅ Job titles extracted: {len(job_titles)}")
    print(f"✅ Certifications extracted: {len(certifications)}")
    
    if job_titles_with_cert_keywords:
        print(f"⚠️  Job titles containing certification keywords: {job_titles_with_cert_keywords}")
    else:
        print("✅ No certification keywords found in job titles")
    
    if certs_with_job_keywords:
        print(f"⚠️  Certifications containing job keywords: {certs_with_job_keywords}")
    else:
        print("✅ No job keywords found in certifications (without cert keywords)")
    
    # Check if we have realistic job titles
    realistic_job_titles = [
        title for title in job_titles 
        if any(keyword in title.lower() for keyword in job_keywords)
    ]
    
    print(f"✅ Realistic job titles found: {len(realistic_job_titles)}")
    
    return parsed_data

if __name__ == "__main__":
    test_job_title_extraction() 