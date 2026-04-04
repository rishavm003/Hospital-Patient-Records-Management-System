"""
Department Model — MongoDB collection operations
"""
from datetime import datetime, timezone
from bson import ObjectId
from config.database import db_config


class Department:
    COLLECTION = 'departments'

    def __init__(self):
        self._col = None

    @property
    def col(self):
        if not self._col:
            self._col = db_config.get_collection(self.COLLECTION)
        return self._col

    def create_department(self, data: dict) -> str:
        doc = {
            'name': data['name'],
            'description': data.get('description', ''),
            'head': ObjectId(data['head']) if data.get('head') else None,
            'floor': data.get('floor', ''),
            'phoneNumber': data.get('phoneNumber', ''),
            'email': data.get('email', ''),
            'workingHours': data.get('workingHours', {'startTime': '09:00', 'endTime': '17:00'}),
            'totalBeds': data.get('totalBeds', 0),
            'availableBeds': data.get('availableBeds', 0),
            'isActive': True,
            'createdAt': datetime.now(timezone.utc),
            'updatedAt': datetime.now(timezone.utc)
        }
        result = self.col.insert_one(doc)
        return str(result.inserted_id)

    def find_all(self, active_only=True):
        query = {'isActive': True} if active_only else {}
        docs = list(self.col.find(query).sort('name', 1))
        return self._serialize_list(docs)

    def find_by_id(self, dept_id: str):
        try:
            doc = self.col.find_one({'_id': ObjectId(dept_id)})
            return self._serialize(doc) if doc else None
        except Exception:
            return None

    def find_by_name(self, name: str):
        return self.col.find_one({'name': name})

    def update_department(self, dept_id: str, data: dict):
        data['updatedAt'] = datetime.now(timezone.utc)
        self.col.update_one({'_id': ObjectId(dept_id)}, {'$set': data})

    def delete_department(self, dept_id: str):
        self.col.update_one({'_id': ObjectId(dept_id)}, {'$set': {'isActive': False}})

    def update_bed_count(self, dept_id: str, available_beds: int):
        self.col.update_one(
            {'_id': ObjectId(dept_id)},
            {'$set': {'availableBeds': available_beds, 'updatedAt': datetime.now(timezone.utc)}}
        )

    def _serialize(self, doc):
        if not doc:
            return None
        doc['_id'] = str(doc['_id'])
        if doc.get('head'):
            doc['head'] = str(doc['head'])
        return doc

    def _serialize_list(self, docs):
        return [self._serialize(d) for d in docs]
