"""
LabTest Model — MongoDB collection operations
"""
from datetime import datetime, timezone
from bson import ObjectId
from config.database import db_config


class LabTest:
    COLLECTION = 'lab_tests'

    def __init__(self):
        self._col = None

    @property
    def col(self):
        if not self._col:
            self._col = db_config.get_collection(self.COLLECTION)
        return self._col

    def _generate_test_number(self) -> str:
        count = self.col.count_documents({}) + 1
        year = datetime.now().year
        return f"LT-{year}-{str(count).zfill(4)}"

    def create_test(self, data: dict) -> str:
        doc = {
            'testNumber': self._generate_test_number(),
            'patient': ObjectId(data['patient']),
            'requestedBy': ObjectId(data['requestedBy']),
            'testType': data.get('testType', ''),
            'testName': data.get('testName', ''),
            'urgency': data.get('urgency', 'Routine'),
            'status': 'Pending',
            'resultDate': None,
            'results': {},
            'referenceRange': {},
            'normalcy': None,
            'notes': data.get('notes', ''),
            'labTechnician': ObjectId(data['labTechnician']) if data.get('labTechnician') else None,
            'attachments': data.get('attachments', []),
            'orderedDate': datetime.now(timezone.utc),
            'createdAt': datetime.now(timezone.utc),
            'updatedAt': datetime.now(timezone.utc)
        }
        result = self.col.insert_one(doc)
        return str(result.inserted_id)

    def find_all(self, filters=None, page=1, page_size=10):
        query = filters or {}
        skip = (page - 1) * page_size
        total = self.col.count_documents(query)
        docs = list(self.col.find(query).skip(skip).limit(page_size).sort('orderedDate', -1))
        return self._serialize_list(docs), total

    def find_by_id(self, test_id: str):
        try:
            doc = self.col.find_one({'_id': ObjectId(test_id)})
            return self._serialize(doc) if doc else None
        except Exception:
            return None

    def find_by_patient(self, patient_id: str, page=1, page_size=10):
        query = {'patient': ObjectId(patient_id)}
        skip = (page - 1) * page_size
        total = self.col.count_documents(query)
        docs = list(self.col.find(query).skip(skip).limit(page_size).sort('orderedDate', -1))
        return self._serialize_list(docs), total

    def update_results(self, test_id: str, data: dict):
        update_data = {
            'results': data.get('results', {}),
            'referenceRange': data.get('referenceRange', {}),
            'normalcy': data.get('normalcy'),
            'notes': data.get('notes', ''),
            'status': 'Completed',
            'resultDate': datetime.now(timezone.utc),
            'updatedAt': datetime.now(timezone.utc)
        }
        if data.get('labTechnician'):
            update_data['labTechnician'] = ObjectId(data['labTechnician'])
        self.col.update_one({'_id': ObjectId(test_id)}, {'$set': update_data})

    def update_status(self, test_id: str, status: str):
        self.col.update_one(
            {'_id': ObjectId(test_id)},
            {'$set': {'status': status, 'updatedAt': datetime.now(timezone.utc)}}
        )

    def count_by_status(self):
        pipeline = [{'$group': {'_id': '$status', 'count': {'$sum': 1}}}]
        return list(self.col.aggregate(pipeline))

    def _serialize(self, doc):
        if not doc:
            return None
        doc['_id'] = str(doc['_id'])
        for field in ['patient', 'requestedBy', 'labTechnician']:
            if doc.get(field):
                doc[field] = str(doc[field])
        return doc

    def _serialize_list(self, docs):
        return [self._serialize(d) for d in docs]
