"""
Medical Record Model for Hospital Patient Records Management System
Handles patient medical records, diagnoses, treatments, and vital signs
"""

from datetime import datetime, timedelta
from bson.objectid import ObjectId
from config.database import db_config


class MedicalRecord:
    """Medical Record model class"""
    
    def __init__(self):
        self.collection = db_config.get_collection('medical_records')
    
    def create_medical_record(self, record_data):
        """Create a new medical record"""
        try:
            # Add timestamps and default values
            record_data['createdAt'] = datetime.utcnow()
            record_data['updatedAt'] = datetime.utcnow()
            record_data['status'] = record_data.get('status', 'Active')
            
            result = self.collection.insert_one(record_data)
            if result.inserted_id:
                return {'success': True, 'data': str(result.inserted_id)}
            else:
                return {'success': False, 'message': 'Failed to create medical record'}
        except Exception as e:
            return {'success': False, 'message': f'Error creating medical record: {str(e)}'}
    
    def get_medical_records(self, filters=None, page=1, page_size=10):
        """Get medical records with optional filters and pagination"""
        try:
            query = {}
            
            if filters:
                # Patient filter
                if filters.get('patientId'):
                    query['patientId'] = ObjectId(filters['patientId'])
                
                # Doctor filter
                if filters.get('doctorId'):
                    query['doctorId'] = ObjectId(filters['doctorId'])
                
                # Status filter
                if filters.get('status'):
                    query['status'] = filters['status']
                
                # Date range filter
                if filters.get('dateFrom'):
                    query['createdAt'] = {'$gte': filters['dateFrom']}
                if filters.get('dateTo'):
                    query['createdAt'] = query.get('createdAt', {})
                    query['createdAt']['$lte'] = filters['dateTo']
                
                # Diagnosis filter
                if filters.get('diagnosis'):
                    query['diagnosis'] = {'$regex': filters['diagnosis'], '$options': 'i'}
            
            # Calculate pagination
            skip = (page - 1) * page_size
            
            # Get total count
            total_items = self.collection.count_documents(query)
            
            # Get paginated results
            records = list(self.collection.find(query)
                        .sort('createdAt', -1)  # Sort by creation date descending
                        .skip(skip)
                        .limit(page_size))
            
            # Convert ObjectId to string for JSON serialization
            for record in records:
                record['_id'] = str(record['_id'])
                if 'patientId' in record:
                    record['patientId'] = str(record['patientId'])
                if 'doctorId' in record:
                    record['doctorId'] = str(record['doctorId'])
            
            total_pages = (total_items + page_size - 1) // page_size
            
            return {
                'success': True,
                'data': records,
                'pagination': {
                    'currentPage': page,
                    'totalPages': total_pages,
                    'totalItems': total_items,
                    'pageSize': page_size,
                    'hasNext': page < total_pages,
                    'hasPrev': page > 1
                }
            }
        except Exception as e:
            return {'success': False, 'message': f'Error fetching medical records: {str(e)}'}
    
    def get_medical_record_by_id(self, record_id):
        """Get a specific medical record by ID"""
        try:
            record = self.collection.find_one({'_id': ObjectId(record_id)})
            if record:
                record['_id'] = str(record['_id'])
                if 'patientId' in record:
                    record['patientId'] = str(record['patientId'])
                if 'doctorId' in record:
                    record['doctorId'] = str(record['doctorId'])
                return {'success': True, 'data': record}
            else:
                return {'success': False, 'message': 'Medical record not found'}
        except Exception as e:
            return {'success': False, 'message': f'Error fetching medical record: {str(e)}'}
    
    def update_medical_record(self, record_id, update_data):
        """Update an existing medical record"""
        try:
            update_data['updatedAt'] = datetime.utcnow()
            
            # Remove fields that shouldn't be updated directly
            update_data.pop('_id', None)
            update_data.pop('createdAt', None)
            
            result = self.collection.update_one(
                {'_id': ObjectId(record_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                return {'success': True, 'message': 'Medical record updated successfully'}
            else:
                return {'success': False, 'message': 'Medical record not found or no changes made'}
        except Exception as e:
            return {'success': False, 'message': f'Error updating medical record: {str(e)}'}
    
    def get_patient_medical_records(self, patient_id, page=1, page_size=10):
        """Get all medical records for a specific patient"""
        try:
            query = {'patientId': ObjectId(patient_id)}
            
            # Calculate pagination
            skip = (page - 1) * page_size
            
            # Get total count
            total_items = self.collection.count_documents(query)
            
            # Get paginated results
            records = list(self.collection.find(query)
                        .sort('createdAt', -1)
                        .skip(skip)
                        .limit(page_size))
            
            # Convert ObjectId to string
            for record in records:
                record['_id'] = str(record['_id'])
                if 'patientId' in record:
                    record['patientId'] = str(record['patientId'])
                if 'doctorId' in record:
                    record['doctorId'] = str(record['doctorId'])
            
            total_pages = (total_items + page_size - 1) // page_size
            
            return {
                'success': True,
                'data': records,
                'pagination': {
                    'currentPage': page,
                    'totalPages': total_pages,
                    'totalItems': total_items,
                    'pageSize': page_size,
                    'hasNext': page < total_pages,
                    'hasPrev': page > 1
                }
            }
        except Exception as e:
            return {'success': False, 'message': f'Error fetching patient medical records: {str(e)}'}
    
    def add_vital_signs(self, record_id, vital_signs):
        """Add vital signs to a medical record"""
        try:
            vital_signs['recordedAt'] = datetime.utcnow()
            vital_signs['recordedBy'] = vital_signs.get('recordedBy')
            
            result = self.collection.update_one(
                {'_id': ObjectId(record_id)},
                {
                    '$push': {'vitalSigns': vital_signs},
                    '$set': {'updatedAt': datetime.utcnow()}
                }
            )
            
            if result.modified_count > 0:
                return {'success': True, 'message': 'Vital signs added successfully'}
            else:
                return {'success': False, 'message': 'Medical record not found'}
        except Exception as e:
            return {'success': False, 'message': f'Error adding vital signs: {str(e)}'}
    
    def add_prescription(self, record_id, prescription):
        """Add prescription to a medical record"""
        try:
            prescription['prescribedAt'] = datetime.utcnow()
            prescription['prescribedBy'] = prescription.get('prescribedBy')
            
            result = self.collection.update_one(
                {'_id': ObjectId(record_id)},
                {
                    '$push': {'prescriptions': prescription},
                    '$set': {'updatedAt': datetime.utcnow()}
                }
            )
            
            if result.modified_count > 0:
                return {'success': True, 'message': 'Prescription added successfully'}
            else:
                return {'success': False, 'message': 'Medical record not found'}
        except Exception as e:
            return {'success': False, 'message': f'Error adding prescription: {str(e)}'}
    
    def get_medical_record_stats(self, start_date=None, end_date=None):
        """Get medical record statistics"""
        try:
            match_stage = {}
            group_stage = {
                '_id': None,
                'totalRecords': {'$sum': 1},
                'activeRecords': {
                    '$sum': {'$cond': [{'$eq': ['$status', 'Active']}, 1, 0]}
                },
                'recordsByDiagnosis': {
                    '$push': {
                        'diagnosis': '$diagnosis',
                        'count': 1
                    }
                }
            }
            
            if start_date or end_date:
                match_stage['createdAt'] = {}
                if start_date:
                    match_stage['createdAt']['$gte'] = start_date
                if end_date:
                    match_stage['createdAt']['$lte'] = end_date
            
            pipeline = [
                {'$match': match_stage},
                {'$group': group_stage}
            ]
            
            stats = list(self.collection.aggregate(pipeline))
            
            if stats:
                stat_data = stats[0]
                return {
                    'success': True,
                    'data': {
                        'totalRecords': stat_data.get('totalRecords', 0),
                        'activeRecords': stat_data.get('activeRecords', 0),
                        'recordsByDiagnosis': stat_data.get('recordsByDiagnosis', [])
                    }
                }
            else:
                return {
                    'success': True,
                    'data': {
                        'totalRecords': 0,
                        'activeRecords': 0,
                        'recordsByDiagnosis': []
                    }
                }
        except Exception as e:
            return {'success': False, 'message': f'Error fetching medical record stats: {str(e)}'}
    
    def delete_medical_record(self, record_id):
        """Delete a medical record (soft delete by updating status)"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(record_id)},
                {'$set': {'status': 'Deleted', 'deletedAt': datetime.utcnow()}}
            )
            
            if result.modified_count > 0:
                return {'success': True, 'message': 'Medical record deleted successfully'}
            else:
                return {'success': False, 'message': 'Medical record not found'}
        except Exception as e:
            return {'success': False, 'message': f'Error deleting medical record: {str(e)}'}
