#!/usr/bin/env python3

import requests
import json

def test_user_job_recommendations():
    """Test the new user-specific job recommendations endpoint"""
    
    # Test the new endpoint that uses saved user profile data
    print("🧪 Testing user-specific job recommendations endpoint...")
    print("=" * 60)
    
    # Test user ID (this should match the mock user in the backend)
    user_id = "user_2yNYihsbMhwjcyoZqbgCgKPbd6B"
    
    try:
        # Call the new endpoint
        response = requests.get(f"http://localhost:8000/api/job-recommendations/{user_id}")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ SUCCESS: Got {len(data.get('jobs', []))} job recommendations")
            print(f"📍 User Location: {data.get('user_location', 'Not found')}")
            print(f"🌍 User Country: {data.get('user_country', 'Not found')}")
            print(f"📊 Profile Source: {data.get('profile_source', 'Not specified')}")
            print(f"💬 Message: {data.get('message', 'No message')}")
            
            # Check if we have jobs
            jobs = data.get('jobs', [])
            if jobs:
                print(f"\n🔍 First few job recommendations:")
                for i, job in enumerate(jobs[:5]):
                    print(f"  {i+1}. {job.get('title', 'No title')} at {job.get('company', 'No company')}")
                    print(f"     📍 Location: {job.get('location', 'No location')}")
                    print(f"     🌍 Country: {job.get('country', 'No country')}")
                    print(f"     📊 Match Score: {job.get('match_score', 'No score')}")
                    print(f"     🔗 Source: {job.get('source', 'No source')}")
                    print()
                
                # Check if Netherlands jobs are prioritized
                netherlands_jobs = [job for job in jobs if 'Netherlands' in job.get('country', '')]
                if netherlands_jobs:
                    print(f"🇳🇱 Found {len(netherlands_jobs)} Netherlands jobs")
                    print(f"📊 Netherlands jobs in top 5: {len([job for job in jobs[:5] if 'Netherlands' in job.get('country', '')])}")
                else:
                    print("⚠️  No Netherlands jobs found")
                    
            else:
                print("❌ No job recommendations returned")
                
        else:
            print(f"❌ ERROR: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to backend server")
        print("💡 Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_user_job_recommendations() 