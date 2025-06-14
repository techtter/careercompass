#!/usr/bin/env python3

import asyncio
import sys
import os
import json
import aiohttp

async def debug_current_user_location():
    """Debug the current user's location data"""
    
    print("🔍 Debugging Current User Location Data")
    print("=" * 60)
    
    # Test with the user ID from the terminal logs
    user_id = "user_2yNYihsbMhwjcyoZqbgCgKPbd6B"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Get user profile
            print(f"📋 Fetching user profile for: {user_id}")
            async with session.get(f"http://127.0.0.1:8000/api/user-profile/{user_id}") as response:
                if response.status == 200:
                    profile_data = await response.json()
                    
                    print(f"✅ User profile retrieved successfully")
                    print(f"   Location: '{profile_data.get('location', 'N/A')}'")
                    print(f"   First Name: {profile_data.get('firstName', 'N/A')}")
                    print(f"   Last Name: {profile_data.get('lastName', 'N/A')}")
                    print(f"   Email: {profile_data.get('email', 'N/A')}")
                    print(f"   Phone: {profile_data.get('phone', 'N/A')}")
                    print(f"   Experience: {profile_data.get('experienceYears', 'N/A')} years")
                    print(f"   Skills: {len(profile_data.get('skills', []))} skills")
                    print(f"   Companies: {profile_data.get('companies', [])}")
                    print(f"   Job Titles: {profile_data.get('lastThreeJobTitles', [])}")
                    
                    # Check if location is None or empty
                    location = profile_data.get('location')
                    if not location:
                        print(f"\n❌ ISSUE FOUND: Location is {location}")
                        print(f"   This explains why job prioritization isn't working")
                        print(f"   The user needs to either:")
                        print(f"   1. Upload a resume with clear location information")
                        print(f"   2. Manually set their location in the profile")
                    else:
                        print(f"\n✅ Location is set: '{location}'")
                        
                        # Test job recommendations with this location
                        print(f"\n🔍 Testing job recommendations with current profile...")
                        
                        job_request = {
                            "skills": profile_data.get('skills', [])[:10],  # Limit to 10 skills
                            "experience": f"{profile_data.get('experienceYears', 2)} years",
                            "lastTwoJobs": profile_data.get('lastThreeJobTitles', [])[:2],
                            "location": location
                        }
                        
                        async with session.post(
                            "http://127.0.0.1:8000/api/job-recommendations",
                            json=job_request
                        ) as job_response:
                            if job_response.status == 200:
                                job_data = await job_response.json()
                                jobs = job_data.get('jobs', [])
                                
                                print(f"✅ Got {len(jobs)} job recommendations")
                                
                                # Check location prioritization
                                netherlands_jobs = 0
                                for i, job in enumerate(jobs[:5], 1):
                                    job_location = job.get('location', '')
                                    job_country = job.get('country', '')
                                    
                                    is_netherlands = (
                                        'Netherlands' in job_country or 
                                        'Netherlands' in job_location or
                                        'Amsterdam' in job_location or
                                        'Rotterdam' in job_location or
                                        'Utrecht' in job_location
                                    )
                                    
                                    if is_netherlands:
                                        netherlands_jobs += 1
                                    
                                    flag = "🇳🇱" if is_netherlands else "🌍"
                                    print(f"   {flag} #{i}: {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')} - {job_location}")
                                
                                print(f"\n📊 Netherlands jobs in top 5: {netherlands_jobs}/5 ({netherlands_jobs*20}%)")
                                
                                if netherlands_jobs >= 3:
                                    print("✅ Location prioritization is working!")
                                else:
                                    print("❌ Location prioritization needs improvement")
                            else:
                                error_text = await job_response.text()
                                print(f"❌ Job recommendations failed: {job_response.status}")
                                print(f"   Error: {error_text}")
                    
                else:
                    error_text = await response.text()
                    print(f"❌ Failed to get user profile: {response.status}")
                    print(f"   Error: {error_text}")
                    
    except Exception as e:
        print(f"❌ Debug failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_current_user_location()) 