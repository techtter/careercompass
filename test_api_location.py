#!/usr/bin/env python3

import asyncio
import json
import aiohttp

async def test_job_recommendations_api():
    """Test the job recommendations API with Netherlands location"""
    
    print("🧪 Testing Job Recommendations API with Netherlands Location")
    print("=" * 70)
    
    # Test data for Netherlands user
    test_data = {
        "skills": ["Python", "Data Engineering", "Apache Spark", "SQL", "Machine Learning"],
        "experience": "5 years",
        "lastTwoJobs": ["Senior Data Engineer", "Data Engineer"],
        "location": "Netherlands"
    }
    
    print(f"📋 Test Request Data:")
    print(f"   Skills: {test_data['skills']}")
    print(f"   Experience: {test_data['experience']}")
    print(f"   Location: {test_data['location']}")
    print(f"   Last Jobs: {test_data['lastTwoJobs']}")
    
    try:
        async with aiohttp.ClientSession() as session:
            print(f"\n🔗 Making API request to: http://localhost:8000/api/job-recommendations")
            
            async with session.post(
                'http://localhost:8000/api/job-recommendations',
                json=test_data,
                headers={'Content-Type': 'application/json'}
            ) as response:
                
                print(f"📊 Response Status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get('success') and data.get('jobs'):
                        jobs = data['jobs']
                        total_jobs = len(jobs)
                        
                        print(f"✅ API Success: {data.get('message', 'Jobs retrieved')}")
                        print(f"📈 Total Jobs: {total_jobs}")
                        
                        # Analyze location distribution
                        netherlands_jobs = 0
                        top_5_netherlands = 0
                        
                        print(f"\n🔍 Job Analysis:")
                        print("-" * 50)
                        
                        for i, job in enumerate(jobs[:10], 1):  # Show top 10
                            title = job.get('title', 'Unknown')
                            company = job.get('company', 'Unknown')
                            location = job.get('location', 'Unknown')
                            country = job.get('country', '')
                            
                            is_netherlands = (
                                'Netherlands' in country or 
                                'Netherlands' in location or 
                                'Amsterdam' in location or
                                'Rotterdam' in location or
                                'Utrecht' in location
                            )
                            
                            if is_netherlands:
                                netherlands_jobs += 1
                                if i <= 5:
                                    top_5_netherlands += 1
                            
                            flag = "🇳🇱" if is_netherlands else "🌍"
                            print(f"{flag} #{i}: {title} at {company} - {location}")
                        
                        print(f"\n📊 Location Priority Analysis:")
                        print(f"   Netherlands jobs in top 10: {netherlands_jobs}/10 ({netherlands_jobs*10}%)")
                        print(f"   Netherlands jobs in top 5: {top_5_netherlands}/5 ({top_5_netherlands*20}%)")
                        
                        # Check first job
                        if jobs:
                            first_job = jobs[0]
                            first_location = first_job.get('location', '')
                            first_country = first_job.get('country', '')
                            is_first_netherlands = (
                                'Netherlands' in first_country or 
                                'Netherlands' in first_location
                            )
                            
                            if is_first_netherlands:
                                print("✅ SUCCESS: #1 job is from Netherlands!")
                            else:
                                print("⚠️  ISSUE: #1 job is not from Netherlands")
                                print(f"   First job location: {first_location}")
                                print(f"   First job country: {first_country}")
                        
                        # Overall assessment
                        if top_5_netherlands >= 3:
                            print("\n🎯 RESULT: Netherlands job prioritization is working correctly!")
                        elif netherlands_jobs >= 6:
                            print("\n🎯 RESULT: Netherlands jobs are well represented")
                        else:
                            print("\n❌ RESULT: Netherlands job prioritization needs improvement")
                            
                    else:
                        print("❌ API returned no jobs or failed")
                        print(f"Response: {data}")
                        
                else:
                    error_text = await response.text()
                    print(f"❌ API Error: {response.status}")
                    print(f"Error details: {error_text}")
                    
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_job_recommendations_api()) 