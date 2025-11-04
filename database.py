from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "email_client")

client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]

# Collections
users_collection = db["users"]
emails_collection = db["emails"]
settings_collection = db["settings"]

# Create indexes
emails_collection.create_index([("created_at", -1)])
emails_collection.create_index([("email_id", 1)], unique=True)
users_collection.create_index([("username", 1)], unique=True)
users_collection.create_index([("email", 1)], unique=True)
