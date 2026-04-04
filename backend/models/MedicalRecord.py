"""
MedicalRecord Model — MongoDB collection operations
"""
from datetime import datetime, timezone
from bson import ObjectId
from config.database import db_config


class MedicalRecord:
    COLLECTION = 'medical_records'

    def __init__(self):
        self._col = None

    @property
    def col(self):
        if not self._col:
            self._col = db_config.get_collection(self.COLLECTION)
        return self._col

    def create_record(self, data: dict) -> str:
        doc = {
            'patient': ObjectId(data['patient']),
            'doctor': ObjectId(data['doctor']),
            'appointment': ObjectId(data['appointment']) if data.get('appointment') else None,
            'date': data.get('date', datetime.now(timezone.utc)),
            'diagnosis': data.get('diagnosis', ''),
            'symptoms': data.get('symptoms', []),
            'treatment': data.get('treatment', ''),
            'doctorNotes': data.get('doctorNotes', ''),
            'vitals': data.get('vitals', {
                'heartRate': None,
                'bloodPressure': '',
                'temperature': None,
                'spo2': None,
                'respiratoryRate': None
            }),
            'medications': data.get('medications', []),
            'labTests': [ObjectId(lt) for lt in data.get('labTests', [])],
            'attachments': data.get('attachments', []),
            'status': 'Active',
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

    def find_by_id(self, record_id: str):
        try:
            doc = self.col.find_one({'_id': ObjectId(record_id)})
            return self._serialize(doc) if doc else None
        except Exception:
            return None

    def find_by_patient(self, patient_id: str, page=1, page_size=10):
        query = {'patient': ObjectId(patient_id)}
        skip = (page - 1) * page_size
        total = self.col.count_documents(query)
        docs = list(self.col.find(query).skip(skip).limit(page_size).sort('date', -1))
        return self._serialize_list(docs), total

    def update_record(self, record_id: str, data: dict):
        data['updatedAt'] = datetime.now(timezone.utc)
        self.col.update_one({'_id': ObjectId(record_id)}, {'$set': data})

    def _serialize(self, doc):
        if not doc:
            return None
        doc['_id'] = str(doc['_id'])
        for field in ['patient', 'doctor', 'appointment']:
            if doc.get(field):
                doc[field] = str(doc[field])
        doc['labTests'] = [str(lt) for lt in doc.get('labTests', [])]
        return doc

    def _serialize_list(self, docs):
        return [self._serialize(d) for d in docs]
