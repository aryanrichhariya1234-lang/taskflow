import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")


# ───────────────────────────────────────────────────────────────────────────────
# Send Email
# ───────────────────────────────────────────────────────────────────────────────

def _send(to: str, subject: str, html_body: str):

    print("========== EMAIL DEBUG ==========", flush=True)
    print("TO:", to, flush=True)
    print("SUBJECT:", subject, flush=True)
    print("SMTP EMAIL:", SMTP_EMAIL, flush=True)

    try:

        if not SMTP_EMAIL:
            print("SMTP_EMAIL missing", flush=True)
            return

        if not SMTP_PASSWORD:
            print("SMTP_PASSWORD missing", flush=True)
            return

        msg = MIMEMultipart("alternative")

        msg["Subject"] = subject
        msg["From"] = SMTP_EMAIL
        msg["To"] = to

        msg.attach(
            MIMEText(html_body, "html")
        )

        print("Connecting to Gmail SMTP...", flush=True)

        with smtplib.SMTP_SSL(
            "smtp.gmail.com",
            465
        ) as smtp:

            print("Logging into Gmail...", flush=True)

            smtp.login(
                SMTP_EMAIL,
                SMTP_PASSWORD
            )

            print("Sending email...", flush=True)

            smtp.sendmail(
                SMTP_EMAIL,
                to,
                msg.as_string(),
            )

        print(f"[email] SUCCESS → {to}", flush=True)

    except Exception as e:

        print(
            "[email] ERROR:",
            str(e),
            flush=True
        )


# ───────────────────────────────────────────────────────────────────────────────
# NO THREADS IN PRODUCTION
# ───────────────────────────────────────────────────────────────────────────────

def send_async(
    to: str,
    subject: str,
    html_body: str
):

    # synchronous call
    _send(
        to,
        subject,
        html_body
    )


# ───────────────────────────────────────────────────────────────────────────────
# Templates
# ───────────────────────────────────────────────────────────────────────────────

def _base_template(content: str):

    frontend_url = os.getenv(
        "FRONTEND_URL",
        "http://localhost:3000"
    )

    return f"""
    <html>
    <body style="font-family:sans-serif;background:#f5f4f0;padding:40px;">

      <div style="
        max-width:600px;
        margin:auto;
        background:white;
        padding:32px;
        border-radius:12px;
      ">

        <h2>TaskFlow</h2>

        {content}

        <p style="margin-top:24px;">
          <a href="{frontend_url}">
            Open TaskFlow
          </a>
        </p>

      </div>

    </body>
    </html>
    """


# ───────────────────────────────────────────────────────────────────────────────
# Assignment Email
# ───────────────────────────────────────────────────────────────────────────────

def notify_task_assigned(
    assignee_email,
    assignee_name,
    creator_name,
    task_title,
    task_description,
    task_id,
    priority,
    due_date,
):

    frontend_url = os.getenv(
        "FRONTEND_URL",
        "http://localhost:3000"
    )

    content = f"""
    <p>Hi {assignee_name},</p>

    <p>
      <strong>{creator_name}</strong>
      assigned a task to you.
    </p>

    <h3>{task_title}</h3>

    <p>{task_description}</p>

    <p>Priority: {priority}</p>

    <a href="{frontend_url}/tasks/{task_id}">
      View Task
    </a>
    """

    send_async(
        assignee_email,
        f"Task Assigned: {task_title}",
        _base_template(content),
    )


# ───────────────────────────────────────────────────────────────────────────────
# Completion Email
# ───────────────────────────────────────────────────────────────────────────────

def notify_task_completed(
    creator_email,
    creator_name,
    completer_name,
    task_title,
    task_id,
):

    frontend_url = os.getenv(
        "FRONTEND_URL",
        "http://localhost:3000"
    )

    content = f"""
    <p>Hi {creator_name},</p>

    <p>
      <strong>{completer_name}</strong>
      completed your task.
    </p>

    <h3>{task_title}</h3>

    <a href="{frontend_url}/tasks/{task_id}">
      View Task
    </a>
    """

    send_async(
        creator_email,
        f"Task Completed: {task_title}",
        _base_template(content),
    )