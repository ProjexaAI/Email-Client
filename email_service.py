import requests
from typing import List, Optional
from auth import get_settings

class ResendService:
    def __init__(self):
        self.base_url = "https://api.resend.com"

    def get_api_key(self):
        """Get API key from database settings"""
        settings = get_settings()
        return settings.get("resend_api_key", "")

    def send_email(
        self,
        to: List[str],
        subject: str,
        html: str,
        from_email: str = "onboarding@resend.dev",
        reply_to: Optional[str] = None,
        attachments: Optional[List[dict]] = None
    ) -> dict:
        """
        Send an email using Resend API
        """
        api_key = self.get_api_key()
        if not api_key:
            raise Exception("Resend API key not configured. Please set it in settings.")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "from": from_email,
            "to": to,
            "subject": subject,
            "html": html
        }

        if reply_to:
            payload["reply_to"] = reply_to

        if attachments:
            payload["attachments"] = attachments

        response = requests.post(
            f"{self.base_url}/emails",
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to send email: {response.text}")

    def reply_to_email(
        self,
        original_from: str,
        subject: str,
        html: str,
        from_email: str = "onboarding@resend.dev"
    ) -> dict:
        """
        Reply to an email
        """
        # Add "Re: " prefix if not already present
        if not subject.startswith("Re: "):
            subject = f"Re: {subject}"

        return self.send_email(
            to=[original_from],
            subject=subject,
            html=html,
            from_email=from_email
        )

resend_service = ResendService()
