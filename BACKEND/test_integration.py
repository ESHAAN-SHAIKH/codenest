"""
Integration Test Script for CODENEST Frontend-Backend
Tests all API endpoints to ensure frontend-backend connectivity
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_endpoint(method, endpoint, data=None, description=""):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Method: {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ SUCCESS")
            try:
                print(f"Response: {json.dumps(response.json(), indent=2)[:200]}...")
            except:
                print(f"Response: {response.text[:200]}...")
        else:
            print(f"❌ FAILED")
            print(f"Response: {response.text[:200]}")
            
        return response.status_code == 200
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def main():
    print("="*60)
    print("CODENEST INTEGRATION TEST")
    print("="*60)
    
    results = []
    
    # Test 1: Root endpoint
    results.append(test_endpoint("GET", "/", description="Root Health Check"))
    
    # Test 2: Progress API
    results.append(test_endpoint("GET", "/api/progress/map?user_id=demo_user", 
                                description="Get Skill Map Progress"))
    
    # Test 3: Execute Languages
    results.append(test_endpoint("GET", "/api/execute/languages", 
                                description="Get Supported Languages"))
    
    # Test 4: Execute Code (Python)
    results.append(test_endpoint("POST", "/api/execute/", 
                                data={"code": "print('Hello from Python!')", "language": "python"},
                                description="Execute Python Code"))
    
    # Test 5: Validate Lesson
    results.append(test_endpoint("POST", "/api/execute/validate",
                                data={"user_output": "Hello", "expected_output": "Hello"},
                                description="Validate Lesson Output"))
    
    # Test 6: AI Chat
    results.append(test_endpoint("POST", "/api/ai/chat",
                                data={"message": "What is a variable?"},
                                description="AI Chat"))
    
    # Test 7: AI Explain Code
    results.append(test_endpoint("POST", "/api/ai/explain",
                                data={"code": "x = 5"},
                                description="AI Code Explanation"))
    
    # Test 8: AI Get Hint
    results.append(test_endpoint("POST", "/api/ai/hint",
                                data={"lesson_id": 1, "user_code": ""},
                                description="AI Hint Generation"))
    
    # Test 9: Complete Lesson
    results.append(test_endpoint("POST", "/api/progress/complete",
                                data={"user_id": "demo_user", "lesson_id": 1, "stars": 3},
                                description="Complete Lesson"))
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n✅ All tests passed! Frontend-Backend integration is GOOD!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check configuration.")

if __name__ == "__main__":
    main()
