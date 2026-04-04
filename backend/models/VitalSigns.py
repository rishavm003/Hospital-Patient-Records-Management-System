"""
VitalSigns Model — MongoDB collection operations
"""
from datetime import datetime, timezone
from bson import ObjectId
from config.database import db_config


class VitalSigns:
    COLLECTION = 'vital_signs'

    def __init__(self):
        self._col = None

    @property
    def col(self):
        if not self._col:
            self._col = db_config.get_collection(self.COLLECTION)
        return self._col

    def create_vital(self, data: dict) -> str:
        height = data.get('height')
        weight = data.get('weight')
        bmi = None
        if height and weight and height > 0:
            bmi = round(weight / ((height / 100) ** 2), 2)

        doc = {
            'patient': ObjectId(data['patient']),
            'recordedBy': ObjectId(data['recordedBy']),
            'recordedAt': data.get('recordedAt', datetime.now(timezone.utc)),
            'heartRate': data.get('heartRate'),
            'bloodPressure': data.get('bloodPressure', ''),
            'temperature': data.get('temperature'),
            'spo2': data.get('spo2'),
            'respiratoryRate': data.get('respiratoryRate'),
            'weight': weight,
            'height': height,
            'bmi': bmi,
            'notes': data.get('notes', ''),
            'createdAt': datetime.now(timezone.utc)
        }
        result = self.col.insert_one(doc)
        return str(result.inserted_id)

    def find_by_patient(self, patient_id: str, limit=20):
        docs = list(
            self.col.find({'patient': ObjectId(patient_id)})
            .sort('recordedAt', -1)
            .limit(limit)
        )
        return self._serialize_list(docs)

    def find_by_id(self, vital_id: str):
        try:
            doc = self.col.find_one({'_id': ObjectId(vital_id)})
            return self._serialize(doc) if doc else None
        except Exception:
            return None

    def get_latest(self, patient_id: str):
        doc = self.col.find_one({'patient': ObjectId(patient_id)}, sort=[('recordedAt', -1)])
        return self._serialize(doc) if doc else None

    def _serialize(self, doc):
        if not doc:
            return None
        doc['_id'] = str(doc['_id'])
        for field in ['patient', 'recordedBy']:
            if doc.get(field):
                doc[field] = str(doc[field])
        return doc

    def _serialize_list(self, docs):
        return [self._serialize(d) for d in docs]
