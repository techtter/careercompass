import asyncio
import aiohttp
import time

async def test():
    print('🚀 Starting Caching System Test')
    
    async with aiohttp.ClientSession() as session:
        # Test cache stats
        try:
            async with session.get('http://127.0.0.1:8000/api/cache/stats') as response:
                if response.status == 200:
                    data = await response.json()
                    print(f'✅ Cache stats: {data}')
                else:
                    print(f'❌ Cache stats failed: {response.status}')
        except Exception as e:
            print(f'❌ Cache stats error: {e}')
        
        # Test job recommendations caching
        test_profile = {
            'skills': ['Python', 'Data Engineering'],
            'experience': '5 years',
            'lastTwoJobs': ['Data Engineer'],
            'location': 'Netherlands'
        }
        
        print('🔍 Testing job recommendations caching...')
        
        # First request
        start = time.time()
        try:
            async with session.post('http://127.0.0.1:8000/api/job-recommendations', json=test_profile) as response:
                first_time = time.time() - start
                if response.status == 200:
                    data = await response.json()
                    print(f'✅ First request: {len(data.get("jobs", []))} jobs in {first_time:.2f}s')
                    
                    # Second request
                    start = time.time()
                    async with session.post('http://127.0.0.1:8000/api/job-recommendations', json=test_profile) as response2:
                        second_time = time.time() - start
                        if response2.status == 200:
                            data2 = await response2.json()
                            print(f'✅ Second request: {len(data2.get("jobs", []))} jobs in {second_time:.2f}s')
                            
                            if second_time < first_time * 0.5:
                                print(f'🚀 CACHE HIT! Speed improvement: {first_time/second_time:.1f}x')
                            else:
                                print(f'⚠️  No significant caching detected')
                        else:
                            print(f'❌ Second request failed: {response2.status}')
                else:
                    print(f'❌ First request failed: {response.status}')
        except Exception as e:
            print(f'❌ Job recommendations error: {e}')

if __name__ == "__main__":
    asyncio.run(test()) 