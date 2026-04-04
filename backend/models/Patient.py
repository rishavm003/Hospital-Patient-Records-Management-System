"""
Patient Model for Hospital Patient Records Management System
Handles patient data, medical history, and related information
"""

from datetime import datetime
from bson.objectid import ObjectId
from config.database import db_config

class Patient:
    """Patient model class"""
    
    def __init__(self):
        self.collection = db_config.get_collection('patients')
    
    def create_patient(self, patient_data):
        """Create a new patient"""
        try:
            # Add timestamps
            patient_data['createdAt'] = datetime.utcnow()
            patient_data['updatedAt'] = datetime.utcnow()
            
            # Set default status
            if 'status' not in patient_data:
                patient_data['status'] = 'Active'
            
            # Initialize arrays if not present
            if 'medicalHistory' not in patient_data:
                patient_data['medicalHistory'] = []
            if 'allergies' not in patient_data:
                patient_data['allergies'] = []
            if 'currentMedications' not in patient_data:
                patient_data['currentMedications'] = []
            if 'documents' not in patient_data:
                patient_data['documents'] = []
            
            result = self.collection.insert_one(patient_data)
            return str(result.inserted_id)
        except Exception as e:
            raise Exception(f"Error creating patient: {e}")
    
    def find_by_id(self, patient_id):
        """Find patient by ID"""
        return self.collection.find_one({'_id': ObjectId(patient_id)})
    
    def find_by_email(self, email):
        """Find patient by email"""
        return self.collection.find_one({'email': email})
    
    def search_patients(self, query, page=1, page_size=10):
        """Search patients by name, email, or phone"""
        skip = (page - 1) * page_size
        
        search_filter = {
            '$or': [
                {'firstName': {'$regex': query, '$options': 'i'}},
                {'lastName': {'$regex': query, '$options': 'i'}},
                {'email': {'$regex': query, '$options': 'i'}},
                {'phone': {'$regex': query, '$options': 'i'}}
            ]
        }
        
        patients = list(self.collection.find(search_filter)
                       .skip(skip)
                       .limit(page_size)
                       .sort('createdAt', -1))
        
        total = self.collection.count_documents(search_filter)
        
        return {
            'patients': patients,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    
    def get_all_patients(self, page=1, page_size=10):
        """Get all patients with pagination"""
        skip = (page - 1) * page_size
        
        patients = list(self.collection.find({})
                       .skip(skip)
                       .limit(page_size)
                       .sort('createdAt', -1))
        
        total = self.collection.count_documents({})
        
        return {
            'patients': patients,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
    
    def update_patient(self, patient_id, update_data):
        """Update patient information"""
        update_data['updatedAt'] = datetime.utcnow()
        self.collection.update_one(
            {'_id': ObjectId(patient_id)},
            {'$set': update_data}
        )
    
    def add_medical_history(self, patient_id, medical_data):
        """Add medical history entry"""
        medical_entry = {
            'condition': medical_data['condition'],
            'diagnosedDate': medical_data.get('diagnosedDate', datetime.utcnow()),
            'notes': medical_data.get('notes', ''),
            'addedAt': datetime.utcnow()
        }
        
        self.collection.update_one(
            {'_id': ObjectId(patient_id)},
            {'$push': {'medicalHistory': medical_entry},
             '$set': {'updatedAt': datetime.utcnow()}}
        )
    
    def add_allergy(self, patient_id, allergy_data):
        """Add allergy information"""
        allergy_entry = {
            'allergen': allergy_data['allergen'],
            'severity': allergy_data['severity'],
            'reaction': allergy_data.get('reaction', ''),
            'addedAt': datetime.utcnow()
        }
        
        self.collection.update_one(
            {'_id': ObjectId(patient_id)},
            {'$push': {'allergies': allergy_entry},
             '$set': {'updatedAt': datetime.utcnow()}}
        )
    
    def add_medication(self, patient_id, medication_data):
        """Add current medication"""
        medication_entry = {
            'medicineName': medication_data['medicineName'],
            'dosage': medication_data['dosage'],
            'frequency': medication_data['frequency'],
            'startDate': medication_data.get('startDate', datetime.utcnow()),
            'endDate': medication_data.get('endDate', None),
            'addedAt': datetime.utcnow()
        }
        
        self.collection.update_one(
            {'_id': ObjectId(patient_id)},
            {'$push': {'currentMedications': medication_entry},
             '$set': {'updatedAt': datetime.utcnow()}}
        )
    
    def upload_document(self, patient_id, document_data):
        """Upload patient document"""
        document_entry = {
            'fileName': document_data['fileName'],
            'fileType': document_data['fileType'],
            'fileSize': document_data['fileSize'],
            'url': document_data['url'],
            'category': document_data['category'],
            'uploadedDate': datetime.utcnow(),
            'uploadedBy': document_data['uploadedBy']
        }
        
        self.collection.update_one(
            {'_id': ObjectId(patient_id)},
            {'$push': {'documents': document_entry},
             '$set': {'updatedAt': datetime.utcnow()}}
        )
    
    def update_status(self, patient_id, status, discharge_date=None):
        """Update patient status"""
        update_data = {
            'status': status,
            'updatedAt': datetime.utcnow()
        }
        
        if discharge_date:
            update_data['dischargeDate'] = discharge_date
        
        self.collection.update_one(
            {'_id': ObjectId(patient_id)},
            {'$set': update_data}
        )
    
    def delete_patient(self, patient_id):
        """Delete patient record (soft delete by setting status)"""
        self.collection.update_one(
            {'_id': ObjectId(patient_id)},
            {'$set': {
                'status': 'Deleted',
                'updatedAt': datetime.utcnow()
            }}
        )
    
    def get_patients_by_status(self, status, page=1, page_size=10):
        """Get patients by status"""
        skip = (page - 1) * page_size
        
        patients = list(self.collection.find({'status': status})
                       .skip(skip)
                       .limit(page_size)
                       .sort('createdAt', -1))
        
        total = self.collection.count_documents({'status': status})
        
        return {
            'patients': patients,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
