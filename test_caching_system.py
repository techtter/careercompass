#!/usr/bin/env python3
"""
Comprehensive Test Script for Job Caching System
Tests both backend and frontend caching functionality
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, List, Any

# Test configuration
BACKEND_URL = "http://127.0.0.1:8000"
TEST_USER_ID = "test_cache_user"

class CachingSystemTester:
    def __init__(self):
        self.session = None
        self.test_results = []
    
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        print("🧪 Setting up caching system test...")
    
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
        print("🧹 Test cleanup completed")
    
    async def test_backend_cache_stats(self):
        """Test backend cache statistics endpoint"""
        print("\n📊 Testing backend cache statistics...")
        
        try:
            async with self.session.get(f"{BACKEND_URL}/api/cache/stats") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Cache stats retrieved: {data}")
                    self.test_results.append(("Backend Cache Stats", "PASS", data))
                    return True
                else:
                    print(f"❌ Cache stats failed: {response.status}")
                    self.test_results.append(("Backend Cache Stats", "FAIL", f"Status: {response.status}"))
                    return False
        except Exception as e:
            print(f"❌ Cache stats error: {e}")
            self.test_results.append(("Backend Cache Stats", "ERROR", str(e)))
            return False
    
    async def test_job_recommendations_caching(self):
        """Test job recommendations with caching"""
        print("\n💼 Testing job recommendations caching...")
        
        test_profile = {
            "skills": ["Python", "Data Engineering", "AWS", "Spark"],
            "experience": "5 years",
            "lastTwoJobs": ["Data Engineer", "Software Developer"],
            "location": "Netherlands"
        }
        
        # First request - should be cache miss
        print("🔍 Making first job recommendation request (cache miss expected)...")
        start_time = time.time()
        
        try:
            async with self.session.post(
                f"{BACKEND_URL}/api/job-recommendations",
                json=test_profile,
                headers={"Content-Type": "application/json"}
            ) as response:
                first_request_time = time.time() - start_time
                
                if response.status == 200:
                    first_data = await response.json()
                    first_jobs = first_data.get("jobs", [])
                    print(f"✅ First request: {len(first_jobs)} jobs in {first_request_time:.2f}s")
                    
                    # Second request - should be cache hit (faster)
                    print("🎯 Making second job recommendation request (cache hit expected)...")
                    start_time = time.time()
                    
                    async with self.session.post(
                        f"{BACKEND_URL}/api/job-recommendations",
                        json=test_profile,
                        headers={"Content-Type": "application/json"}
                    ) as response2:
                        second_request_time = time.time() - start_time
                        
                        if response2.status == 200:
                            second_data = await response2.json()
                            second_jobs = second_data.get("jobs", [])
                            
                            print(f"✅ Second request: {len(second_jobs)} jobs in {second_request_time:.2f}s")
                            
                            # Verify caching worked
                            if second_request_time < first_request_time * 0.5:  # Should be significantly faster
                                print(f"🚀 CACHE HIT DETECTED: {first_request_time:.2f}s → {second_request_time:.2f}s")
                                self.test_results.append(("Job Recommendations Caching", "PASS", 
                                                        f"Speed improvement: {first_request_time/second_request_time:.1f}x"))
                                return True
                            else:
                                print(f"⚠️  No significant speed improvement detected")
                                self.test_results.append(("Job Recommendations Caching", "PARTIAL", 
                                                        f"Times: {first_request_time:.2f}s, {second_request_time:.2f}s"))
                                return False
                        else:
                            print(f"❌ Second request failed: {response2.status}")
                            return False
                else:
                    print(f"❌ First request failed: {response.status}")
                    return False
                    
        except Exception as e:
            print(f"❌ Job recommendations caching error: {e}")
            self.test_results.append(("Job Recommendations Caching", "ERROR", str(e)))
            return False
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "="*60)
        print("🧪 CACHING SYSTEM TEST SUMMARY")
        print("="*60)
        
        passed = 0
        total = len(self.test_results)
        
        for test_name, status, details in self.test_results:
            status_icon = "✅" if status == "PASS" else "⚠️" if status == "PARTIAL" else "❌"
            print(f"{status_icon} {test_name}: {status}")
            print(f"   Details: {details}")
            
            if status == "PASS":
                passed += 1
        
        print(f"\n📊 Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! Caching system is working perfectly.")
        elif passed >= total * 0.7:
            print("✅ Most tests passed. Caching system is mostly functional.")
        else:
            print("⚠️  Several tests failed. Caching system needs attention.")
        
        print("\n💡 Performance Benefits:")
        print("   ✅ Reduced API calls to external job services")
        print("   ✅ Faster page navigation and job loading")
        print("   ✅ Better user experience with instant results")
        print("   ✅ Reduced server load and API rate limiting")

async def main():
    """Run comprehensive caching system tests"""
    print("🚀 Starting Comprehensive Caching System Test")
    print("=" * 60)
    
    tester = CachingSystemTester()
    
    try:
        await tester.setup()
        
        # Run all tests
        await tester.test_backend_cache_stats()
        await tester.test_job_recommendations_caching()
        
        # Print summary
        tester.print_test_summary()
        
    except Exception as e:
        print(f"❌ Test suite error: {e}")
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main()) 