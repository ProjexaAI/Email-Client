import hashlib
import secrets
from datetime import datetime
from database import users_collection, settings_collection

def hash_password(password: str) -> str:
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed_password

def create_user(username: str, password: str, email: str, is_admin: bool = False):
    """Create a new user"""
    # Check if username already exists
    if users_collection.find_one({"username": username}):
        return None, "Username already exists"

    # Check if email already exists
    if users_collection.find_one({"email": email}):
        return None, "Email already exists"

    user_doc = {
        "username": username,
        "email": email,
        "password": hash_password(password),
        "is_admin": is_admin,
        "created_at": datetime.now(),
        "last_login": datetime.now(),
        "is_active": True,
    }

    result = users_collection.insert_one(user_doc)
    user_doc["_id"] = str(result.inserted_id)
    return user_doc, None

def authenticate_user(username: str, password: str):
    """Authenticate user with username and password"""
    user = users_collection.find_one({"username": username})

    if not user:
        return None, "Invalid username or password"

    if not user.get("is_active", False):
        return None, "Account is inactive"

    if not verify_password(password, user["password"]):
        return None, "Invalid username or password"

    # Update last login
    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.now()}}
    )

    return user, None

def check_if_any_user_exists() -> bool:
    """Check if any user exists in the database"""
    return users_collection.count_documents({}) > 0

def get_settings():
    """Get application settings from database"""
    settings = settings_collection.find_one({"type": "app_settings"})
    if not settings:
        # Create default settings
        settings = {
            "type": "app_settings",
            "resend_api_key": "",
            "r2_account_id": "",
            "r2_access_key_id": "",
            "r2_secret_access_key": "",
            "r2_bucket_name": "",
            "r2_public_url": "",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        settings_collection.insert_one(settings)
    return settings

def update_settings(settings_data: dict):
    """Update application settings"""
    settings_data["updated_at"] = datetime.now()
    settings_collection.update_one(
        {"type": "app_settings"},
        {"$set": settings_data},
        upsert=True
    )
