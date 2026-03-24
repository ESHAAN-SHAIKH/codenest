"""
Quick API test script to verify all endpoints work
"""

import requests
import json

BASE_URL = "http://localhost:5000"

print("="*60)
print("CODENEST Cognitive API Test")
print("="*60)

# Test 1: Get all concepts
print("\n[1/6] Testing GET /api/cognitive/concepts")
try:
    response = requests.get(f"{BASE_URL}/api/cognitive/concepts")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Found {data['data']['total']} concepts")
        if data['data']['concepts']:
            print(f"   Sample: {data['data']['concepts'][0]['name']} ({data['data']['concepts'][0]['category']})")
    else:
        print(f"❌ Failed: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 2: Get archetype definitions
print("\n[2/6] Testing GET /api/archetypes/definitions")
try:
    response = requests.get(f"{BASE_URL}/api/archetypes/definitions")
    if response.status_code == 200:
        data = response.json()
        archetypes = list(data['data']['archetypes'].keys())
        print(f"✅ Success! Found {len(archetypes)} archetypes")
        print(f"   Types: {', '.join(archetypes)}")
    else:
        print(f"❌ Failed: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 3: Get user mastery profile (user 1)
print("\n[3/6] Testing GET /api/cognitive/mastery/1")
try:
    response = requests.get(f"{BASE_URL}/api/cognitive/mastery/1")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! User has mastery for {data['data']['total_concepts']} concepts")
        print(f"   Average mastery: {data['data']['average_mastery']}")
    else:
        print(f"❌ Failed: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 4: Start debugging session
print("\n[4/6] Testing POST /api/debugging/start")
try:
    payload = {"user_id": 1, "difficulty": "medium"}
    response = requests.post(f"{BASE_URL}/api/debugging/start", json=payload)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! Started debugging session")
        print(f"   Bug type: {data['data']['challenge']['bug_type']}")
        print(f"   Difficulty: {data['data']['challenge']['difficulty']}")
    else:
        print(f"❌ Failed: {response.status_code} - {response.text}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 5: Get archetype progress (user 1)
print("\n[5/6] Testing GET /api/archetypes/progress/1")
try:
    response = requests.get(f"{BASE_URL}/api/archetypes/progress/1")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Success! User has {len(data['data']['archetypes'])} archetype records")
        if data['data']['dominant_archetype']:
            print(f"   Dominant: {data['data']['dominant_archetype']['archetype_type']}")
    else:
        print(f"❌ Failed: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test 6: Get adaptive next challenge
print("\n[6/6] Testing GET /api/cognitive/adaptive-next/1")
try:
    response = requests.get(f"{BASE_URL}/api/cognitive/adaptive-next/1")
    if response.status_code == 200:
        data = response.json()
        if data['data']['has_recommendation']:
            print(f"✅ Success! Got recommendation")
            print(f"   Reason: {data['data']['recommendation_reason']}")
            print(f"   Message: {data['data']['message'][:60]}...")
        else:
            print(f"✅ Success! {data['data']['message']}")
    else:
        print(f"❌ Failed: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*60)
print("API Test Complete!")
print("="*60)
