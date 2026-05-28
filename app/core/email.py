import resend

from app.core.config import settings


def send_contact_email(to_email: str, name: str, from_email: str, message: str) -> bool:
    if not settings.RESEND_API_KEY:
        print("RESEND_API_KEY not configured — skipping email")
        return False

    html_content = f"""
<h2>Contact Form Submission</h2>
<p><strong>Name:</strong> {name}</p>
<p><strong>Email:</strong> {from_email}</p>
<p><strong>Message:</strong></p>
<p>{message}</p>
"""

    params = {
        "from": "onboarding@resend.dev",
        "to": [to_email],
        "subject": f"Portfolio Contact: {name}",
        "html": html_content,
    }

    try:
        resend.api_key = settings.RESEND_API_KEY
        resend.Emails.send(params)
        return True
    except Exception as e:
        print(f"Failed to send email via Resend: {e}")
        return False
