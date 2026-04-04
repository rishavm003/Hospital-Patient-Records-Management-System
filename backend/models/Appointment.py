"""
Appointment Model for Hospital Patient Records Management System
Handles appointment scheduling, status tracking, and calendar management
"""

from datetime import datetime, timedelta
from bson.objectid import ObjectId
from config.database import db_config


class Appointment:
    """Appointment model class"""
    
    def __init__(self):
        self.collection = db_config.get_collection('appointments')
    
    def create_appointment(self, appointment_data):
        """Create a new appointment"""
        try:
            # Add timestamps and default values
            appointment_data['createdAt'] = datetime.utcnow()
            appointment_data['updatedAt'] = datetime.utcnow()
            appointment_data['status'] = appointment_data.get('status', 'Scheduled')
            
            # Validate appointment time
            appointment_datetime = datetime.fromisoformat(appointment_data['dateTime'])
            if appointment_datetime < datetime.utcnow():
                return {'success': False, 'message': 'Appointment time cannot be in the past'}
            
            result = self.collection.insert_one(appointment_data)
            if result.inserted_id:
                return {'success': True, 'data': str(result.inserted_id)}
            else:
                return {'success': False, 'message': 'Failed to create appointment'}
        except Exception as e:
            return {'success': False, 'message': f'Error creating appointment: {str(e)}'}
    
    def get_appointments(self, filters=None, page=1, page_size=10):
        """Get appointments with optional filters and pagination"""
        try:
            query = {}
            
            if filters:
                # Status filter
                if filters.get('status'):
                    query['status'] = filters['status']
                
                # Date range filter
                if filters.get('dateFrom'):
                    query['dateTime'] = {'$gte': filters['dateFrom']}
                if filters.get('dateTo'):
                    query['dateTime'] = query.get('dateTime', {})
                    query['dateTime']['$lte'] = filters['dateTo']
                
                # Patient filter
                if filters.get('patientId'):
                    query['patientId'] = ObjectId(filters['patientId'])
                
                # Doctor filter
                if filters.get('doctorId'):
                    query['doctorId'] = ObjectId(filters['doctorId'])
                
                # Department filter
                if filters.get('department'):
                    query['department'] = filters['department']
            
            # Calculate pagination
            skip = (page - 1) * page_size
            
            # Get total count
            total_items = self.collection.count_documents(query)
            
            # Get paginated results
            appointments = list(self.collection.find(query)
                              .sort('dateTime', 1)  # Sort by date ascending
                              .skip(skip)
                              .limit(page_size))
            
            # Convert ObjectId to string for JSON serialization
            for appointment in appointments:
                appointment['_id'] = str(appointment['_id'])
                if 'patientId' in appointment:
                    appointment['patientId'] = str(appointment['patientId'])
                if 'doctorId' in appointment:
                    appointment['doctorId'] = str(appointment['doctorId'])
            
            total_pages = (total_items + page_size - 1) // page_size
            
            return {
                'success': True,
                'data': appointments,
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
            return {'success': False, 'message': f'Error fetching appointments: {str(e)}'}
    
    def get_appointment_by_id(self, appointment_id):
        """Get a specific appointment by ID"""
        try:
            appointment = self.collection.find_one({'_id': ObjectId(appointment_id)})
            if appointment:
                appointment['_id'] = str(appointment['_id'])
                if 'patientId' in appointment:
                    appointment['patientId'] = str(appointment['patientId'])
                if 'doctorId' in appointment:
                    appointment['doctorId'] = str(appointment['doctorId'])
                return {'success': True, 'data': appointment}
            else:
                return {'success': False, 'message': 'Appointment not found'}
        except Exception as e:
            return {'success': False, 'message': f'Error fetching appointment: {str(e)}'}
    
    def update_appointment(self, appointment_id, update_data):
        """Update an existing appointment"""
        try:
            update_data['updatedAt'] = datetime.utcnow()
            
            # Remove fields that shouldn't be updated directly
            update_data.pop('_id', None)
            update_data.pop('createdAt', None)
            
            result = self.collection.update_one(
                {'_id': ObjectId(appointment_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                return {'success': True, 'message': 'Appointment updated successfully'}
            else:
                return {'success': False, 'message': 'Appointment not found or no changes made'}
        except Exception as e:
            return {'success': False, 'message': f'Error updating appointment: {str(e)}'}
    
    def cancel_appointment(self, appointment_id, reason=None):
        """Cancel an appointment"""
        try:
            update_data = {
                'status': 'Cancelled',
                'cancelledAt': datetime.utcnow(),
                'cancelReason': reason
            }
            
            result = self.collection.update_one(
                {'_id': ObjectId(appointment_id)},
                {'$set': update_data}
            )
            
            if result.modified_count > 0:
                return {'success': True, 'message': 'Appointment cancelled successfully'}
            else:
                return {'success': False, 'message': 'Appointment not found'}
        except Exception as e:
            return {'success': False, 'message': f'Error cancelling appointment: {str(e)}'}
    
    def check_appointment_conflict(self, doctor_id, date_time, duration_minutes=30, exclude_appointment_id=None):
        """Check if appointment conflicts with existing appointments"""
        try:
            # Convert to datetime if string
            if isinstance(date_time, str):
                date_time = datetime.fromisoformat(date_time)
            
            # Calculate appointment end time
            appointment_end = date_time + timedelta(minutes=duration_minutes)
            
            # Build query to find overlapping appointments
            query = {
                'doctorId': ObjectId(doctor_id),
                'status': {'$in': ['Scheduled', 'Confirmed']},
                '$or': [
                    # Appointment starts during another appointment
                    {
                        'dateTime': {'$gte': date_time.isoformat(), '$lt': appointment_end.isoformat()}
                    },
                    # Appointment ends during another appointment
                    {
                        'dateTime': {'$lt': date_time.isoformat()},
                        '$expr': {
                            '$add': ['$dateTime', {'$multiply': ['$duration', 60000]}]  # Convert minutes to milliseconds
                        }
                    }
                ]
            }
            
            # Exclude current appointment from conflict check
            if exclude_appointment_id:
                query['_id'] = {'$ne': ObjectId(exclude_appointment_id)}
            
            conflicting_appointments = list(self.collection.find(query))
            
            return {
                'hasConflict': len(conflicting_appointments) > 0,
                'conflicts': conflicting_appointments
            }
        except Exception as e:
            return {'hasConflict': False, 'error': str(e)}
    
    def get_appointments_by_date_range(self, start_date, end_date, doctor_id=None):
        """Get appointments within a date range"""
        try:
            query = {
                'dateTime': {
                    '$gte': start_date,
                    '$lte': end_date
                },
                'status': {'$in': ['Scheduled', 'Confirmed']}
            }
            
            if doctor_id:
                query['doctorId'] = ObjectId(doctor_id)
            
            appointments = list(self.collection.find(query)
                              .sort('dateTime', 1))
            
            # Convert ObjectId to string
            for appointment in appointments:
                appointment['_id'] = str(appointment['_id'])
                if 'patientId' in appointment:
                    appointment['patientId'] = str(appointment['patientId'])
                if 'doctorId' in appointment:
                    appointment['doctorId'] = str(appointment['doctorId'])
            
            return {
                'success': True,
                'data': appointments
            }
        except Exception as e:
            return {'success': False, 'message': f'Error fetching appointments: {str(e)}'}
    
    def get_appointment_stats(self, start_date=None, end_date=None):
        """Get appointment statistics"""
        try:
            match_stage = {}
            group_stage = {
                '_id': '$status',
                'count': {'$sum': 1}
            }
            
            if start_date or end_date:
                match_stage['dateTime'] = {}
                if start_date:
                    match_stage['dateTime']['$gte'] = start_date
                if end_date:
                    match_stage['dateTime']['$lte'] = end_date
            
            pipeline = [
                {'$match': match_stage},
                {'$group': group_stage},
                {'$sort': {'_id': 1}}
            ]
            
            stats = list(self.collection.aggregate(pipeline))
            
            # Format stats
            total = sum(stat['count'] for stat in stats)
            formatted_stats = {}
            
            for stat in stats:
                formatted_stats[stat['_id']] = {
                    'count': stat['count'],
                    'percentage': total > 0 and round((stat['count'] / total) * 100, 1) or 0
                }
            
            return {
                'success': True,
                'data': {
                    'total': total,
                    'byStatus': formatted_stats
                }
            }
        except Exception as e:
            return {'success': False, 'message': f'Error fetching stats: {str(e)}'}
    
    def delete_appointment(self, appointment_id):
        """Delete an appointment (soft delete by updating status)"""
        try:
            result = self.collection.update_one(
                {'_id': ObjectId(appointment_id)},
                {'$set': {'status': 'Deleted', 'deletedAt': datetime.utcnow()}}
            )
            
            if result.modified_count > 0:
                return {'success': True, 'message': 'Appointment deleted successfully'}
            else:
                return {'success': False, 'message': 'Appointment not found'}
        except Exception as e:
            return {'success': False, 'message': f'Error deleting appointment: {str(e)}'}

    def _generate_appointment_number(self) -> str:
        count = self.col.count_documents({}) + 1
        year = datetime.now().year
        return f"AP-{year}-{str(count).zfill(4)}"

    def create_appointment(self, data: dict) -> str:
        doc = {
            'appointmentNumber': self._generate_appointment_number(),
            'patient': ObjectId(data['patient']),
            'doctor': ObjectId(data['doctor']),
            'department': ObjectId(data['department']) if data.get('department') else None,
            'date': data['date'],
            'startTime': data['startTime'],
            'endTime': data.get('endTime', ''),
            'type': data.get('type', 'Consultation'),
            'status': 'Scheduled',
            'purpose': data.get('purpose', ''),
            'doctorNotes': '',
            'cancellationReason': None,
            'cancelledBy': None,
            'cancelledAt': None,
            'createdAt': datetime.now(timezone.utc),
            'updatedAt': datetime.now(timezone.utc)
        }
        result = self.col.insert_one(doc)
        return str(result.inserted_id)

    def find_all(self, filters=None, page=1, page_size=10):
        query = filters or {}
        skip = (page - 1) * page_size
        total = self.col.count_documents(query)
        docs = list(self.col.find(query).skip(skip).limit(page_size).sort('date', -1))
        return self._serialize_list(docs), total

    def find_by_id(self, appointment_id: str):
        try:
            doc = self.col.find_one({'_id': ObjectId(appointment_id)})
            return self._serialize(doc) if doc else None
        except Exception:
            return None

    def find_by_patient(self, patient_id: str, page=1, page_size=10):
        query = {'patient': ObjectId(patient_id)}
        skip = (page - 1) * page_size
        total = self.col.count_documents(query)
        docs = list(self.col.find(query).skip(skip).limit(page_size).sort('date', -1))
        return self._serialize_list(docs), total

    def find_by_doctor(self, doctor_id: str, date=None):
        query = {'doctor': ObjectId(doctor_id)}
        if date:
            query['date'] = date
        docs = list(self.col.find(query).sort('startTime', 1))
        return self._serialize_list(docs)

    def update_appointment(self, appointment_id: str, data: dict):
        data['updatedAt'] = datetime.now(timezone.utc)
        self.col.update_one({'_id': ObjectId(appointment_id)}, {'$set': data})

    def cancel_appointment(self, appointment_id: str, reason: str, cancelled_by: str):
        self.col.update_one(
            {'_id': ObjectId(appointment_id)},
            {'$set': {
                'status': 'Cancelled',
                'cancellationReason': reason,
                'cancelledBy': ObjectId(cancelled_by),
                'cancelledAt': datetime.now(timezone.utc),
                'updatedAt': datetime.now(timezone.utc)
            }}
        )

    def complete_appointment(self, appointment_id: str, doctor_notes: str):
        self.col.update_one(
            {'_id': ObjectId(appointment_id)},
            {'$set': {'status': 'Completed', 'doctorNotes': doctor_notes, 'updatedAt': datetime.now(timezone.utc)}}
        )

    def count_by_status(self):
        pipeline = [{'$group': {'_id': '$status', 'count': {'$sum': 1}}}]
        return list(self.col.aggregate(pipeline))

    def _serialize(self, doc):
        if not doc:
            return None
        doc['_id'] = str(doc['_id'])
        for field in ['patient', 'doctor', 'department', 'cancelledBy']:
            if doc.get(field):
                doc[field] = str(doc[field])
        return doc

    def _serialize_list(self, docs):
        return [self._serialize(d) for d in docs]
