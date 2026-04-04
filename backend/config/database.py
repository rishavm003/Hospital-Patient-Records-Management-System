"""
Database Configuration for Hospital Patient Records Management System
MongoDB connection and configuration
"""

import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseConfig:
    """Database configuration class"""
    
    def __init__(self):
        self.MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/hospital_prms')
        self.DATABASE_NAME = os.getenv('DATABASE_NAME', 'hospital_prms')
        self.client = None
        self.db = None
    
    def connect(self):
        """Establish MongoDB connection"""
        try:
            self.client = MongoClient(self.MONGODB_URI)
            self.db = self.client[self.DATABASE_NAME]
            print(f"✅ Connected to MongoDB: {self.DATABASE_NAME}")
            return True
        except Exception as e:
            print(f"❌ MongoDB connection error: {e}")
            return False
    
    def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("✅ MongoDB connection closed")
    
    def get_database(self):
        """Get database instance"""
        return self.db
    
    def get_collection(self, collection_name):
        """Get specific collection"""
        return self.db[collection_name] if self.db is not None else None

# Global database instance
db_config = DatabaseConfig()
