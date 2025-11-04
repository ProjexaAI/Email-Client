from fastapi import FastAPI, Request, HTTPException, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime
from typing import Optional
import os
from dotenv import load_dotenv

from database import emails_collection, users_collection
from auth import (
    authenticate_user,
    create_user,
    check_if_any_user_exists,
    get_settings,
    update_settings
)
from email_service import resend_service
from r2_service import r2_service

load_dotenv()

app = FastAPI(title="Simple Email Client")

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-this")
)

# Mount static files and templates
templates = Jinja2Templates(directory="templates")

# Dependency to check if user is authenticated
def get_current_user(request: Request):
    if not request.session.get("is_authenticated"):
        return None
    return request.session.get("user")

def require_auth(request: Request):
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

def require_admin(request: Request):
    user = get_current_user(request)
    if not user or not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

# Routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, message: Optional[str] = None):
    # Check if any user exists, if not redirect to setup
    if not check_if_any_user_exists():
        return RedirectResponse("/setup")

    user = get_current_user(request)
    if not user:
        return RedirectResponse("/login")

    # Get all emails sorted by date
    emails = list(emails_collection.find().sort("created_at", -1))

    # Convert ObjectId to string for JSON serialization
    for email in emails:
        email["_id"] = str(email["_id"])

    return templates.TemplateResponse(
        "inbox.html",
        {"request": request, "user": user, "emails": emails}
    )

@app.get("/setup", response_class=HTMLResponse)
async def setup_page(request: Request, message: Optional[str] = None):
    # If users already exist, redirect to login
    if check_if_any_user_exists():
        return RedirectResponse("/login")

    return templates.TemplateResponse(
        "setup.html",
        {"request": request, "message": message}
    )

@app.post("/setup")
async def setup(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    # Check if users already exist
    if check_if_any_user_exists():
        return RedirectResponse("/login")

    # Validate passwords match
    if password != confirm_password:
        return RedirectResponse("/setup?message=Passwords do not match")

    # Create first admin user
    user, error = create_user(username, password, email, is_admin=True)

    if error:
        return RedirectResponse(f"/setup?message={error}")

    # Log the user in
    request.session["user"] = {
        "username": user["username"],
        "email": user["email"],
        "is_admin": user["is_admin"]
    }
    request.session["is_authenticated"] = True

    return RedirectResponse("/")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, message: Optional[str] = None):
    # Check if setup is needed
    if not check_if_any_user_exists():
        return RedirectResponse("/setup")

    # If already logged in, redirect to home
    if get_current_user(request):
        return RedirectResponse("/")

    return templates.TemplateResponse(
        "login.html",
        {"request": request, "message": message}
    )

@app.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    user, error = authenticate_user(username, password)

    if error:
        return RedirectResponse(f"/login?message={error}")

    # Set session
    request.session["user"] = {
        "username": user["username"],
        "email": user["email"],
        "is_admin": user.get("is_admin", False)
    }
    request.session["is_authenticated"] = True

    return RedirectResponse("/")

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login")

@app.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, message: Optional[str] = None):
    user = require_admin(request)
    settings = get_settings()

    # Get all users
    all_users = list(users_collection.find())
    for u in all_users:
        u["_id"] = str(u["_id"])
        del u["password"]  # Don't send password to frontend

    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
            "user": user,
            "settings": settings,
            "users": all_users,
            "message": message
        }
    )

@app.post("/settings/api")
async def update_api_settings(
    request: Request,
    resend_api_key: str = Form(...),
    r2_account_id: str = Form(""),
    r2_access_key_id: str = Form(""),
    r2_secret_access_key: str = Form(""),
    r2_bucket_name: str = Form(""),
    r2_public_url: str = Form("")
):
    user = require_admin(request)

    settings_data = {
        "resend_api_key": resend_api_key,
        "r2_account_id": r2_account_id,
        "r2_access_key_id": r2_access_key_id,
        "r2_secret_access_key": r2_secret_access_key,
        "r2_bucket_name": r2_bucket_name,
        "r2_public_url": r2_public_url
    }

    update_settings(settings_data)

    return RedirectResponse("/settings?message=Settings updated successfully", status_code=303)

@app.post("/settings/users")
async def create_new_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    is_admin: bool = Form(False)
):
    admin = require_admin(request)

    user, error = create_user(username, password, email, is_admin)

    if error:
        return RedirectResponse(f"/settings?message={error}", status_code=303)

    return RedirectResponse("/settings?message=User created successfully", status_code=303)

@app.delete("/settings/users/{username}")
async def delete_user(request: Request, username: str):
    admin = require_admin(request)

    # Don't allow deleting yourself
    if admin["username"] == username:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    result = users_collection.delete_one({"username": username})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"status": "success", "message": "User deleted"}

@app.post("/webhook/email")
async def receive_email(request: Request):
    """
    Webhook endpoint to receive emails from Resend
    """
    try:
        payload = await request.json()

        if payload.get("type") != "email.received":
            return {"status": "ignored"}

        email_data = payload["data"]

        # Process attachments and upload to R2
        attachments = []
        if email_data.get("attachments"):
            for attachment in email_data["attachments"]:
                try:
                    attachments.append({
                        "id": attachment["id"],
                        "filename": attachment["filename"],
                        "content_type": attachment["content_type"],
                        "content_disposition": attachment.get("content_disposition"),
                        "content_id": attachment.get("content_id"),
                    })
                except Exception as e:
                    print(f"Error processing attachment: {e}")

        # Store email in MongoDB
        email_doc = {
            "email_id": email_data["email_id"],
            "created_at": datetime.fromisoformat(email_data["created_at"].replace("Z", "+00:00")),
            "from": email_data["from"],
            "to": email_data["to"],
            "cc": email_data.get("cc", []),
            "bcc": email_data.get("bcc", []),
            "subject": email_data["subject"],
            "message_id": email_data.get("message_id"),
            "attachments": attachments,
            "is_read": False,
            "is_replied": False,
            "received_at": datetime.now()
        }

        # Insert or update email
        emails_collection.update_one(
            {"email_id": email_data["email_id"]},
            {"$set": email_doc},
            upsert=True
        )

        return {"status": "success", "email_id": email_data["email_id"]}

    except Exception as e:
        print(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/email/{email_id}", response_class=HTMLResponse)
async def view_email(request: Request, email_id: str):
    user = require_auth(request)
    email = emails_collection.find_one({"email_id": email_id})

    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    # Mark as read
    emails_collection.update_one(
        {"email_id": email_id},
        {"$set": {"is_read": True}}
    )

    email["_id"] = str(email["_id"])

    return templates.TemplateResponse(
        "email_view.html",
        {"request": request, "user": user, "email": email}
    )

@app.post("/email/{email_id}/reply")
async def reply_to_email(
    request: Request,
    email_id: str,
    reply_content: str = Form(...)
):
    user = require_auth(request)
    email = emails_collection.find_one({"email_id": email_id})

    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    try:
        # Extract sender email from "Name <email>" format
        from_email = email["from"]
        if "<" in from_email and ">" in from_email:
            sender_email = from_email.split("<")[1].split(">")[0]
        else:
            sender_email = from_email

        # Send reply using Resend
        result = resend_service.reply_to_email(
            original_from=sender_email,
            subject=email["subject"],
            html=f"<p>{reply_content}</p>"
        )

        # Mark email as replied
        emails_collection.update_one(
            {"email_id": email_id},
            {"$set": {"is_replied": True}}
        )

        return JSONResponse({"status": "success", "message": "Reply sent successfully"})

    except Exception as e:
        print(f"Error sending reply: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/email/{email_id}")
async def delete_email(request: Request, email_id: str):
    user = require_auth(request)
    result = emails_collection.delete_one({"email_id": email_id})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Email not found")

    return {"status": "success", "message": "Email deleted"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
