from fastapi import FastAPI, Request, HTTPException, Depends, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from datetime import datetime
from typing import Optional, List
import os
from dotenv import load_dotenv
import io

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

    # Keep datetime objects for server-side template rendering (so strftime works),
    # but prepare a JSON-serializable copy for client-side JavaScript.
    serializable_emails = []
    for email in emails:
        # Ensure _id is a string for templates
        email["_id"] = str(email["_id"])

        # Create a shallow copy and convert datetimes to ISO strings for JS
        ser = email.copy()
        if isinstance(ser.get("created_at"), datetime):
            ser["created_at"] = ser["created_at"].isoformat()
        if isinstance(ser.get("received_at"), datetime):
            ser["received_at"] = ser["received_at"].isoformat()

        serializable_emails.append(ser)

    return templates.TemplateResponse(
        "inbox.html",
        {"request": request, "user": user, "emails": emails, "emails_json": serializable_emails}
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
    send_from_email: str = Form("onboarding@resend.dev"),
    r2_account_id: str = Form(""),
    r2_access_key_id: str = Form(""),
    r2_secret_access_key: str = Form(""),
    r2_bucket_name: str = Form(""),
    r2_public_url: str = Form("")
):
    user = require_admin(request)

    settings_data = {
        "resend_api_key": resend_api_key,
        "send_from_email": send_from_email,
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
        email_id = email_data.get("email_id")

        # Fetch the full email content from Resend API
        try:
            full_email = resend_service.get_email(email_id)
        except Exception as e:
            print(f"Error fetching full email content: {e}")
            # Continue with webhook data if API fetch fails
            full_email = email_data

        # Process attachments and upload to R2
        attachments = []
        if full_email.get("attachments"):
            for attachment in full_email["attachments"]:
                try:
                    attachments.append({
                        "id": attachment.get("id"),
                        "filename": attachment.get("filename"),
                        "content_type": attachment.get("content_type"),
                        "content_disposition": attachment.get("content_disposition"),
                        "content_id": attachment.get("content_id"),
                    })
                except Exception as e:
                    print(f"Error processing attachment: {e}")

        # Store email in MongoDB with full content
        email_doc = {
            "email_id": email_id,
            "created_at": datetime.fromisoformat(full_email.get("created_at", email_data.get("created_at")).replace("Z", "+00:00")),
            "from": full_email.get("from", email_data.get("from")),
            "to": full_email.get("to", email_data.get("to")),
            "cc": full_email.get("cc", []),
            "bcc": full_email.get("bcc", []),
            "reply_to": full_email.get("reply_to", []),
            "subject": full_email.get("subject", email_data.get("subject")),
            "html": full_email.get("html", ""),
            "text": full_email.get("text", ""),
            "message_id": full_email.get("message_id"),
            "headers": full_email.get("headers", {}),
            "attachments": attachments,
            "is_read": False,
            "is_replied": False,
            "received_at": datetime.now(),
            "reply_history": []  # Track all replies sent to this email
        }

        # Insert or update email
        emails_collection.update_one(
            {"email_id": email_id},
            {"$set": email_doc},
            upsert=True
        )

        return {"status": "success", "email_id": email_id}

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

        # Get configured send from email
        settings = get_settings()
        configured_from_email = settings.get("send_from_email", "onboarding@resend.dev")

        # Get message_id for threading
        message_id = email.get("message_id")
        if not message_id:
            raise Exception("Original email has no message_id for threading")

        # Get previous references from email headers or reply history
        references = []
        if email.get("headers") and email["headers"].get("References"):
            # Parse existing references
            references = email["headers"]["References"].split()
        
        # Get previous reply message IDs from reply history
        if email.get("reply_history"):
            for reply in email["reply_history"]:
                if reply.get("message_id"):
                    references.append(reply["message_id"])

        # Send reply using Resend with proper threading
        result = resend_service.reply_to_email(
            original_from=sender_email,
            subject=email["subject"],
            html=f"<p>{reply_content}</p>",
            message_id=message_id,
            from_email=configured_from_email,
            references=references if references else None
        )

        # Update email with reply information
        reply_info = {
            "replied_at": datetime.now(),
            "replied_by": user["username"],
            "message_id": result.get("id")
        }

        emails_collection.update_one(
            {"email_id": email_id},
            {
                "$set": {"is_replied": True},
                "$push": {"reply_history": reply_info}
            }
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

@app.get("/api/email/{email_id}/content")
async def get_email_content(request: Request, email_id: str):
    """
    Fetch full email content from Resend API
    """
    user = require_auth(request)

    try:
        email_content = resend_service.get_email(email_id)
        return JSONResponse(email_content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/email/{email_id}/attachments")
async def get_email_attachments(request: Request, email_id: str):
    """
    Get all attachments for a specific email
    """
    user = require_auth(request)

    try:
        attachments = resend_service.get_email_attachments(email_id)
        return JSONResponse(attachments)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/email/{email_id}/attachments/{attachment_id}/download")
async def download_attachment(request: Request, email_id: str, attachment_id: str):
    """
    Download a specific attachment
    """
    user = require_auth(request)

    try:
        # Get attachment details including download URL
        attachment_info = resend_service.get_attachment(email_id, attachment_id)

        # Download the attachment content
        content = resend_service.download_attachment(attachment_info["download_url"])

        # Return as streaming response
        return StreamingResponse(
            io.BytesIO(content),
            media_type=attachment_info.get("content_type", "application/octet-stream"),
            headers={
                "Content-Disposition": f'attachment; filename="{attachment_info.get("filename", "download")}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/emails/search")
async def search_emails(
    request: Request,
    q: Optional[str] = Query(None, description="Search query"),
    from_email: Optional[str] = Query(None, description="Filter by sender email"),
    subject: Optional[str] = Query(None, description="Filter by subject"),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    has_attachments: Optional[bool] = Query(None, description="Filter emails with attachments")
):
    """
    Search and filter emails
    """
    user = require_auth(request)

    # Build MongoDB query
    query = {}

    # General search across from, subject, and to fields
    if q:
        query["$or"] = [
            {"from": {"$regex": q, "$options": "i"}},
            {"subject": {"$regex": q, "$options": "i"}},
            {"to": {"$regex": q, "$options": "i"}}
        ]

    # Specific filters
    if from_email:
        query["from"] = {"$regex": from_email, "$options": "i"}

    if subject:
        query["subject"] = {"$regex": subject, "$options": "i"}

    if is_read is not None:
        query["is_read"] = is_read

    if has_attachments:
        query["attachments"] = {"$exists": True, "$ne": []}

    # Execute query
    emails = list(emails_collection.find(query).sort("created_at", -1))

    # Convert ObjectId to string
    for email in emails:
        email["_id"] = str(email["_id"])
        # Convert datetime to ISO format
        if isinstance(email.get("created_at"), datetime):
            email["created_at"] = email["created_at"].isoformat()
        if isinstance(email.get("received_at"), datetime):
            email["received_at"] = email["received_at"].isoformat()

    return JSONResponse({"emails": emails, "count": len(emails)})

@app.post("/api/email/compose")
async def compose_email(
    request: Request,
    to_emails: str = Form(...),  # Changed to string to handle JSON array
    subject: str = Form(...),
    html_content: str = Form(...),
    cc: Optional[str] = Form(None),
    bcc: Optional[str] = Form(None),
    from_email: Optional[str] = Form(None),
    text_content: Optional[str] = Form(None),
    reply_to: Optional[str] = Form(None)
):
    """
    Compose and send a new email to specified recipients
    """
    user = require_auth(request)

    try:
        # Parse email addresses (can be comma-separated or JSON array)
        import json
        
        # Parse to_emails
        try:
            to_list = json.loads(to_emails)
        except:
            to_list = [email.strip() for email in to_emails.split(",")]

        # Parse cc if provided
        cc_list = None
        if cc:
            try:
                cc_list = json.loads(cc)
            except:
                cc_list = [email.strip() for email in cc.split(",")]

        # Parse bcc if provided
        bcc_list = None
        if bcc:
            try:
                bcc_list = json.loads(bcc)
            except:
                bcc_list = [email.strip() for email in bcc.split(",")]

        # Parse reply_to if provided
        reply_to_address = None
        if reply_to:
            try:
                reply_to_list = json.loads(reply_to)
                reply_to_address = reply_to_list[0] if reply_to_list else None
            except:
                reply_to_address = reply_to.strip()

        # Get configured send from email if not provided
        if not from_email:
            settings = get_settings()
            from_email = settings.get("send_from_email", "onboarding@resend.dev")

        # Send email using Resend
        result = resend_service.send_email(
            to=to_list,
            subject=subject,
            html=html_content,
            text=text_content,
            from_email=from_email,
            cc=cc_list,
            bcc=bcc_list,
            reply_to=reply_to_address
        )

        return JSONResponse({
            "status": "success",
            "message": "Email sent successfully",
            "email_id": result.get("id")
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/compose", response_class=HTMLResponse)
async def compose_page(request: Request):
    """
    Compose new email page
    """
    user = require_auth(request)

    return templates.TemplateResponse(
        "compose.html",
        {"request": request, "user": user}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
