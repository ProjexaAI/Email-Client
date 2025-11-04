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
        attachments: Optional[List[dict]] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        text: Optional[str] = None,
        email_headers: Optional[dict] = None,
        tags: Optional[List[dict]] = None
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

        if text:
            payload["text"] = text

        if reply_to:
            payload["reply_to"] = reply_to

        if cc:
            payload["cc"] = cc

        if bcc:
            payload["bcc"] = bcc

        if attachments:
            payload["attachments"] = attachments

        if email_headers:
            payload["headers"] = email_headers

        if tags:
            payload["tags"] = tags

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
        message_id: str,
        from_email: str = "onboarding@resend.dev",
        references: Optional[List[str]] = None
    ) -> dict:
        """
        Reply to an email with proper threading using In-Reply-To and References headers
        """
        # Add "Re: " prefix if not already present
        if not subject.startswith("Re: "):
            subject = f"Re: {subject}"

        # Build email headers for threading
        email_headers = {
            "In-Reply-To": message_id
        }

        # Add References header if there are previous message IDs
        if references:
            # Include all previous references and the current message_id
            all_references = references + [message_id]
            email_headers["References"] = " ".join(all_references)
        else:
            # First reply in thread, just use the message_id
            email_headers["References"] = message_id

        return self.send_email(
            to=[original_from],
            subject=subject,
            html=html,
            from_email=from_email,
            email_headers=email_headers
        )

    def get_email(self, email_id: str) -> dict:
        """
        Fetch full email content from Resend API
        """
        api_key = self.get_api_key()
        if not api_key:
            raise Exception("Resend API key not configured. Please set it in settings.")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        response = requests.get(
            f"{self.base_url}/emails/receiving/{email_id}",
            headers=headers
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch email: {response.text}")

    def list_emails(self, limit: int = 100, has_more: bool = False) -> dict:
        """
        List all received emails from Resend API
        """
        api_key = self.get_api_key()
        if not api_key:
            raise Exception("Resend API key not configured. Please set it in settings.")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        params = {"limit": limit}

        response = requests.get(
            f"{self.base_url}/emails/receiving",
            headers=headers,
            params=params
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to list emails: {response.text}")

    def get_email_attachments(self, email_id: str) -> dict:
        """
        Get all attachments for a specific email
        """
        api_key = self.get_api_key()
        if not api_key:
            raise Exception("Resend API key not configured. Please set it in settings.")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        response = requests.get(
            f"{self.base_url}/emails/receiving/{email_id}/attachments",
            headers=headers
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch attachments: {response.text}")

    def get_attachment(self, email_id: str, attachment_id: str) -> dict:
        """
        Get details for a specific attachment including download URL
        """
        api_key = self.get_api_key()
        if not api_key:
            raise Exception("Resend API key not configured. Please set it in settings.")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        response = requests.get(
            f"{self.base_url}/emails/receiving/{email_id}/attachments/{attachment_id}",
            headers=headers
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch attachment: {response.text}")

    def download_attachment(self, download_url: str) -> bytes:
        """
        Download attachment content from the provided URL
        """
        response = requests.get(download_url)

        if response.status_code == 200:
            return response.content
        else:
            raise Exception(f"Failed to download attachment: {response.text}")

resend_service = ResendService()
