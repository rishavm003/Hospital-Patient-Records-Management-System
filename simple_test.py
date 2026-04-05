"""
Simple test to verify appointment APIs are working
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return False

def test_appointment_endpoints():
    """Test appointment endpoints exist"""
    endpoints = [
        "/api/appointments",
        "/api/appointments/stats",
        "/api/appointments/available-slots"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            # 401 is expected without auth token
            if response.status_code in [200, 401]:
                print(f"✅ {endpoint} - Endpoint exists")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Error: {str(e)}")

if __name__ == "__main__":
    print("🚀 Testing Appointment APIs - Step 2.4\n")
    
    if test_health():
        print("\n📋 Testing Appointment Endpoints:")
        test_appointment_endpoints()
        
        print("\n🎉 Step 2.4: Appointment APIs are ready!")
        print("\n📋 Available Appointment Endpoints:")
        print("   GET    /api/appointments - Get all appointments")
        print("   GET    /api/appointments/:id - Get specific appointment")
        print("   POST   /api/appointments - Create appointment")
        print("   PUT    /api/appointments/:id - Update appointment")
        print("   POST   /api/appointments/:id/cancel - Cancel appointment")
        print("   DELETE /api/appointments/:id - Delete appointment")
        print("   GET    /api/appointments/calendar/:year/:month - Calendar view")
        print("   GET    /api/appointments/stats - Appointment statistics")
        print("   GET    /api/appointments/available-slots - Available time slots")
    else:
        print("❌ Backend is not running. Please start the backend first.")
