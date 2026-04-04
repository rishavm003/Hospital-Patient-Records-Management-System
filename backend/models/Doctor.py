"""
Doctor Model — MongoDB collection operations
"""
from datetime import datetime, timezone
from bson import ObjectId
from config.database import db_config


class Doctor:
    COLLECTION = 'doctors'

    def __init__(self):
        self._col = None

    @property
    def col(self):
        if not self._col:
            self._col = db_config.get_collection(self.COLLECTION)
        return self._col

    def create_doctor(self, data: dict) -> str:
        doc = {
            'firstName': data['firstName'],
            'lastName': data['lastName'],
            'email': data['email'],
            'phone': data.get('phone', ''),
            'specialization': data.get('specialization', ''),
            'licenseNumber': data.get('licenseNumber', ''),
            'department': ObjectId(data['department']) if data.get('department') else None,
            'availability': data.get('availability', {}),
            'appointmentDuration': data.get('appointmentDuration', 30),
            'slotIntervals': data.get('slotIntervals', 30),
            'isActive': True,
            'joiningDate': data.get('joiningDate'),
            'createdAt': datetime.now(timezone.utc),
            'updatedAt': datetime.now(timezone.utc)
        }
        result = self.col.insert_one(doc)
        return str(result.inserted_id)

    def find_all(self, filters=None, page=1, page_size=10):
        query = filters or {}
        skip = (page - 1) * page_size
        total = self.col.count_documents(query)
        docs = list(self.col.find(query).skip(skip).limit(page_size).sort('createdAt', -1))
        return self._serialize_list(docs), total

    def find_by_id(self, doctor_id: str):
        try:
            doc = self.col.find_one({'_id': ObjectId(doctor_id)})
            return self._serialize(doc) if doc else None
        except Exception:
            return None

    def find_by_email(self, email: str):
        return self.col.find_one({'email': email})

    def update_doctor(self, doctor_id: str, data: dict):
        data['updatedAt'] = datetime.now(timezone.utc)
        self.col.update_one({'_id': ObjectId(doctor_id)}, {'$set': data})

    def delete_doctor(self, doctor_id: str):
        self.col.update_one({'_id': ObjectId(doctor_id)}, {'$set': {'isActive': False, 'updatedAt': datetime.now(timezone.utc)}})

    def find_by_department(self, department_id: str):
        docs = list(self.col.find({'department': ObjectId(department_id), 'isActive': True}))
        return self._serialize_list(docs)

    def _serialize(self, doc):
        if not doc:
            return None
        doc['_id'] = str(doc['_id'])
        if doc.get('department'):
            doc['department'] = str(doc['department'])
        return doc

    def _serialize_list(self, docs):
        return [self._serialize(d) for d in docs]
