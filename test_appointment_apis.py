"""
Test Script for Appointment APIs - Step 2.4
Tests all appointment endpoints with sample data
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://127.0.0.1:5000"
API_BASE = f"{BASE_URL}/api"

# Test data
test_user = {
    "email": "doctor@test.com",
    "password": "password123"
}

test_patient_data = {
    "firstName": "John",
    "lastName": "Doe",
    "email": "john.doe@test.com",
    "phone": "9876543210",
    "dateOfBirth": "1990-01-15",
    "gender": "Male",
    "bloodGroup": "O+",
    "address": "123 Test Street",
    "city": "Test City",
    "state": "Test State",
    "zipCode": "12345"
}

test_doctor_data = {
    "firstName": "Jane",
    "lastName": "Smith",
    "email": "jane.smith@test.com",
    "password": "password123",
    "role": "Doctor",
    "phone": "9876543211",
    "specialization": "Cardiology",
    "department": "Cardiology"
}

test_appointment_data = {
    "patientId": "",
    "doctorId": "",
    "dateTime": (datetime.now() + timedelta(days=1)).replace(hour=10, minute=0).isoformat(),
    "type": "Consultation",
    "duration": 30,
    "department": "Cardiology",
    "notes": "Regular checkup appointment"
}

class APITester:
    def __init__(self):
        self.auth_token = None
        self.created_patient_id = None
        self.created_doctor_id = None
        self.created_appointment_id = None
    
    def test_auth(self):
        """Test authentication and get token"""
        print("🔐 Testing Authentication...")
        
        # Register and login doctor
        try:
            # Register doctor
            register_response = requests.post(f"{API_BASE}/auth/register", json=test_doctor_data)
            if register_response.status_code == 200:
                print("✅ Doctor registered successfully")
            
            # Login doctor
            login_response = requests.post(f"{API_BASE}/auth/login", json={
                "email": test_doctor_data["email"],
                "password": test_doctor_data["password"]
            })
            
            if login_response.status_code == 200:
                data = login_response.json()
                self.auth_token = data.get("data", {}).get("accessToken")
                print("✅ Authentication successful")
                return True
            else:
                print(f"❌ Login failed: {login_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Auth error: {str(e)}")
            return False
    
    def create_test_patient(self):
        """Create a test patient"""
        print("👤 Creating Test Patient...")
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.post(f"{API_BASE}/patients", json=test_patient_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.created_patient_id = data.get("data", {}).get("patientId")
                print(f"✅ Patient created: {self.created_patient_id}")
                return True
            else:
                print(f"❌ Patient creation failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Patient creation error: {str(e)}")
            return False
    
    def create_test_doctor(self):
        """Create a test doctor (already done in auth)"""
        print("👩‍⚕️ Getting Test Doctor ID...")
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(f"{API_BASE}/users/me", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.created_doctor_id = data.get("data", {}).get("_id")
                print(f"✅ Doctor ID retrieved: {self.created_doctor_id}")
                return True
            else:
                print(f"❌ Doctor ID retrieval failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Doctor ID error: {str(e)}")
            return False
    
    def test_create_appointment(self):
        """Test appointment creation"""
        print("📅 Testing Appointment Creation...")
        
        try:
            # Update test data with actual IDs
            test_appointment_data["patientId"] = self.created_patient_id
            test_appointment_data["doctorId"] = self.created_doctor_id
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.post(f"{API_BASE}/appointments", json=test_appointment_data, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                self.created_appointment_id = data.get("data", {}).get("appointmentId")
                print(f"✅ Appointment created: {self.created_appointment_id}")
                return True
            else:
                print(f"❌ Appointment creation failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Appointment creation error: {str(e)}")
            return False
    
    def test_get_appointments(self):
        """Test getting all appointments"""
        print("📋 Testing Get Appointments...")
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(f"{API_BASE}/appointments", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                appointments = data.get("data", [])
                print(f"✅ Retrieved {len(appointments)} appointments")
                return True
            else:
                print(f"❌ Get appointments failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Get appointments error: {str(e)}")
            return False
    
    def test_get_appointment_by_id(self):
        """Test getting a specific appointment"""
        print("🔍 Testing Get Appointment by ID...")
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(f"{API_BASE}/appointments/{self.created_appointment_id}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                appointment = data.get("data", {})
                print(f"✅ Retrieved appointment: {appointment.get('type')}")
                return True
            else:
                print(f"❌ Get appointment by ID failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Get appointment by ID error: {str(e)}")
            return False
    
    def test_update_appointment(self):
        """Test updating an appointment"""
        print("✏️ Testing Appointment Update...")
        
        try:
            update_data = {
                "notes": "Updated appointment notes",
                "type": "Follow-up"
            }
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.put(f"{API_BASE}/appointments/{self.created_appointment_id}", 
                                 json=update_data, headers=headers)
            
            if response.status_code == 200:
                print("✅ Appointment updated successfully")
                return True
            else:
                print(f"❌ Appointment update failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Appointment update error: {str(e)}")
            return False
    
    def test_cancel_appointment(self):
        """Test cancelling an appointment"""
        print("❌ Testing Appointment Cancellation...")
        
        try:
            cancel_data = {
                "reason": "Patient requested cancellation"
            }
            
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.post(f"{API_BASE}/appointments/{self.created_appointment_id}/cancel", 
                                   json=cancel_data, headers=headers)
            
            if response.status_code == 200:
                print("✅ Appointment cancelled successfully")
                return True
            else:
                print(f"❌ Appointment cancellation failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Appointment cancellation error: {str(e)}")
            return False
    
    def test_appointment_stats(self):
        """Test appointment statistics"""
        print("📊 Testing Appointment Statistics...")
        
        try:
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(f"{API_BASE}/appointments/stats", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                stats = data.get("data", {})
                print(f"✅ Retrieved stats: {stats.get('total', 0)} total appointments")
                return True
            else:
                print(f"❌ Appointment stats failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Appointment stats error: {str(e)}")
            return False
    
    def test_available_slots(self):
        """Test available time slots"""
        print("⏰ Testing Available Slots...")
        
        try:
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(f"{API_BASE}/appointments/available-slots?date={tomorrow}&doctorId={self.created_doctor_id}", 
                                   headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                slots = data.get("data", {}).get("slots", [])
                print(f"✅ Retrieved {len(slots)} available slots")
                return True
            else:
                print(f"❌ Available slots failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Available slots error: {str(e)}")
            return False
    
    def test_calendar_view(self):
        """Test calendar view"""
        print("📆 Testing Calendar View...")
        
        try:
            today = datetime.now()
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = requests.get(f"{API_BASE}/appointments/calendar/{today.year}/{today.month}", 
                                   headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                appointments = data.get("data", [])
                print(f"✅ Retrieved {len(appointments)} calendar appointments")
                return True
            else:
                print(f"❌ Calendar view failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Calendar view error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all appointment API tests"""
        print("🚀 Starting Appointment API Tests - Step 2.4\n")
        
        tests = [
            self.test_auth,
            self.create_test_patient,
            self.create_test_doctor,
            self.test_create_appointment,
            self.test_get_appointments,
            self.test_get_appointment_by_id,
            self.test_update_appointment,
            self.test_cancel_appointment,
            self.test_appointment_stats,
            self.test_available_slots,
            self.test_calendar_view
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            try:
                if test():
                    passed += 1
                print()
            except Exception as e:
                print(f"❌ Test failed with exception: {str(e)}\n")
        
        print(f"🎯 Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All appointment API tests passed! Step 2.4 is complete!")
        else:
            print("⚠️ Some tests failed. Check the errors above.")
        
        return passed == total

if __name__ == "__main__":
    tester = APITester()
    tester.run_all_tests()
