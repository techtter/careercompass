#!/usr/bin/env python3

import asyncio
import sys
import os
import json

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from ai_services import parse_resume_content, _extract_country_from_work_history, _get_mock_resume_parse

def test_netherlands_location_detection():
    """Test that Netherlands location detection is working correctly"""
    
    print("🧪 Testing Netherlands Location Detection")
    print("=" * 60)
    
    # Test case with Netherlands-specific content
    netherlands_resume = """
John Doe
Senior Data Engineer
Email: john.doe@example.com
Phone: +31 6 12345678
Location: Amsterdam, Netherlands

WORK EXPERIENCE:
2020-2023: Senior Data Engineer at TechCorp B.V., Amsterdam
- Developed data pipelines using Apache Spark and Kafka
- Worked with Azure cloud services and Databricks
- Led a team of 5 engineers

2018-2020: Data Engineer at ING Bank, Utrecht
- Built ETL processes for financial data
- Implemented real-time streaming solutions
- Technologies: Python, SQL, Apache Airflow

EDUCATION:
2014-2018: Bachelor of Computer Science
University of Amsterdam, Netherlands

SKILLS:
Python, Apache Spark, Kafka, Azure, SQL, Machine Learning, Docker, Kubernetes
"""
    
    print("📋 Test Case: Netherlands Resume")
    print("=" * 40)
    
    # Test 1: Direct country extraction
    print("🔍 Test 1: Direct country extraction from work history")
    companies = ["TechCorp B.V.", "ING Bank"]
    job_titles = ["Senior Data Engineer", "Data Engineer"]
    detected_country = _extract_country_from_work_history(netherlands_resume, companies, job_titles)
    print(f"   Result: '{detected_country}'")
    print(f"   Expected: 'Netherlands'")
    print(f"   Status: {'✅ PASS' if detected_country == 'Netherlands' else '❌ FAIL'}")
    print()
    
    # Test 2: Full resume parsing
    print("🔍 Test 2: Full resume parsing")
    try:
        parsed_result = parse_resume_content(netherlands_resume)
        parsed_data = json.loads(parsed_result) if isinstance(parsed_result, str) else parsed_result
        
        location = parsed_data.get('location', '')
        print(f"   Parsed location: '{location}'")
        print(f"   Expected: 'Netherlands' or 'Amsterdam, Netherlands'")
        
        is_netherlands = (
            'Netherlands' in location or 
            'Amsterdam' in location or
            location == 'Netherlands'
        )
        
        print(f"   Status: {'✅ PASS' if is_netherlands else '❌ FAIL'}")
        
        # Show full parsed data for debugging
        print(f"   Full parsed data:")
        print(f"     - First Name: {parsed_data.get('firstName', 'N/A')}")
        print(f"     - Last Name: {parsed_data.get('lastName', 'N/A')}")
        print(f"     - Email: {parsed_data.get('email', 'N/A')}")
        print(f"     - Phone: {parsed_data.get('phone', 'N/A')}")
        print(f"     - Location: {parsed_data.get('location', 'N/A')}")
        print(f"     - Companies: {parsed_data.get('companies', [])}")
        print(f"     - Skills: {len(parsed_data.get('skills', []))} skills found")
        
    except Exception as e:
        print(f"   ❌ FAIL: Error parsing resume: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test 3: Mock parsing specifically
    print("🔍 Test 3: Mock resume parsing")
    try:
        mock_result = _get_mock_resume_parse(netherlands_resume)
        mock_data = json.loads(mock_result)
        
        mock_location = mock_data.get('location', '')
        print(f"   Mock parsed location: '{mock_location}'")
        print(f"   Expected: 'Netherlands' or contains Netherlands")
        
        is_mock_netherlands = (
            'Netherlands' in mock_location or 
            'Amsterdam' in mock_location or
            mock_location == 'Netherlands'
        )
        
        print(f"   Status: {'✅ PASS' if is_mock_netherlands else '❌ FAIL'}")
        
        # Show companies found
        mock_companies = mock_data.get('companies', [])
        print(f"   Companies found: {mock_companies}")
        
    except Exception as e:
        print(f"   ❌ FAIL: Error in mock parsing: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("🔍 Summary:")
    print("   If any tests fail, the location detection needs to be fixed")
    print("   The issue is likely in the pattern matching or extraction logic")

if __name__ == "__main__":
    test_netherlands_location_detection() 