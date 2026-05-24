import os
import base64
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def _get_gmail_service():
    """Build authenticated Gmail service using service account credentials."""
    creds_path = os.getenv("GMAIL_CREDENTIALS_PATH", "gmail_credentials.json")
    sender_email = os.getenv("GMAIL_SENDER_EMAIL", "")

    if not os.path.exists(creds_path):
        print(f"[email] Credentials file not found at {creds_path}. Emails will be skipped.")
        return None

    try:
        credentials = service_account.Credentials.from_service_account_file(
            creds_path, scopes=SCOPES
        )
        # Domain-wide delegation: impersonate the sender address
        delegated = credentials.with_subject(sender_email)
        service = build("gmail", "v1", credentials=delegated, cache_discovery=False)
        return service
    except Exception as e:
        print(f"[email] Failed to build Gmail service: {e}")
        return None


def _build_message(to: str, subject: str, html_body: str) -> dict:
    msg = MIMEMultipart("alternative")
    msg["To"] = to
    msg["From"] = os.getenv("GMAIL_SENDER_EMAIL", "noreply@taskflow.app")
    msg["Subject"] = subject
    msg.attach(MIMEText(html_body, "html"))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    return {"raw": raw}


def _send(to: str, subject: str, html_body: str):
    """Internal: actually send via Gmail API."""
    service = _get_gmail_service()
    if service is None:
        print(f"[email] Would send to {to}: {subject}")
        return
    try:
        service.users().messages().send(
            userId="me", body=_build_message(to, subject, html_body)
        ).execute()
        print(f"[email] Sent to {to}: {subject}")
    except HttpError as e:
        print(f"[email] Gmail API error: {e}")


def send_async(to: str, subject: str, html_body: str):
    """Fire-and-forget email in a background thread."""
    t = threading.Thread(target=_send, args=(to, subject, html_body), daemon=True)
    t.start()


# ── Email templates ────────────────────────────────────────────────────────────

def _base_template(content: str) -> str:
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <style>
    body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background: #f5f4f0; margin: 0; padding: 40px 0; color: #1a1a18; }}
    .card {{ background: #ffffff; max-width: 560px; margin: 0 auto; border-radius: 12px; overflow: hidden; border: 1px solid #e0dfd8; }}
    .header {{ background: #1a1a18; padding: 28px 36px; }}
    .header h1 {{ color: #f0ede4; margin: 0; font-size: 18px; letter-spacing: -0.02em; font-weight: 500; }}
    .header span {{ color: #6ee7b7; font-weight: 700; }}
    .body {{ padding: 32px 36px; }}
    .body p {{ margin: 0 0 16px; line-height: 1.6; color: #3d3d3a; font-size: 15px; }}
    .task-box {{ background: #f5f4f0; border-radius: 8px; padding: 20px 24px; margin: 20px 0; border-left: 3px solid #6ee7b7; }}
    .task-box .title {{ font-size: 16px; font-weight: 600; color: #1a1a18; margin: 0 0 6px; }}
    .task-box .meta {{ font-size: 13px; color: #73726c; margin: 0; }}
    .cta {{ display: inline-block; background: #1a1a18; color: #f0ede4 !important; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 500; margin-top: 8px; }}
    .footer {{ padding: 20px 36px; border-top: 1px solid #e0dfd8; font-size: 12px; color: #9c9a92; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header"><h1>Task<span>Flow</span></h1></div>
    <div class="body">{content}</div>
    <div class="footer">TaskFlow · <a href="{frontend_url}" style="color:#9c9a92;">Open app</a></div>
  </div>
</body>
</html>
"""


def notify_task_assigned(
    assignee_email: str,
    assignee_name: str,
    creator_name: str,
    task_title: str,
    task_description: str,
    task_id: str,
    priority: str,
    due_date: str | None,
):
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    due = f"Due {due_date}" if due_date else "No due date"
    content = f"""
<p>Hi {assignee_name or assignee_email},</p>
<p><strong>{creator_name}</strong> assigned a new task to you:</p>
<div class="task-box">
  <div class="title">{task_title}</div>
  <div class="meta">{task_description or 'No description'} &nbsp;·&nbsp; Priority: {priority.upper()} &nbsp;·&nbsp; {due}</div>
</div>
<a href="{frontend_url}/tasks/{task_id}" class="cta">View task →</a>
"""
    send_async(
        to=assignee_email,
        subject=f"New task assigned to you: {task_title}",
        html_body=_base_template(content),
    )


def notify_task_completed(
    creator_email: str,
    creator_name: str,
    completer_name: str,
    task_title: str,
    task_id: str,
):
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    content = f"""
<p>Hi {creator_name or creator_email},</p>
<p><strong>{completer_name}</strong> marked your task as complete 🎉</p>
<div class="task-box">
  <div class="title">{task_title}</div>
  <div class="meta">Status: DONE</div>
</div>
<a href="{frontend_url}/tasks/{task_id}" class="cta">View task →</a>
"""
    send_async(
        to=creator_email,
        subject=f"Task completed: {task_title}",
        html_body=_base_template(content),
    )
