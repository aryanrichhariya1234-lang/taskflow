import os
import resend
from datetime import datetime


# ─────────────────────────────────────────────────────────────
# Resend Configuration
# ─────────────────────────────────────────────────────────────

resend.api_key = os.getenv("RESEND_API_KEY")

EMAIL_FROM = os.getenv(
    "EMAIL_FROM",
    "onboarding@resend.dev"
)

FRONTEND_URL = os.getenv(
    "FRONTEND_URL",
    "http://localhost:3000"
)


# ─────────────────────────────────────────────────────────────
# Send Email
# ─────────────────────────────────────────────────────────────

def send_async(
    to: str,
    subject: str,
    html_body: str,
):

    try:

        print("\n========== EMAIL DEBUG ==========")
        print(f"TO: {to}")
        print(f"SUBJECT: {subject}")
        print("=================================\n")

        response = resend.Emails.send({

            "from": EMAIL_FROM,

            "to": [to],

            "subject": subject,

            "html": html_body,
        })

        print(
            "[EMAIL] SENT SUCCESSFULLY:",
            response,
            flush=True
        )

        return response

    except Exception as e:

        print(
            "[EMAIL ERROR]:",
            str(e),
            flush=True
        )

        return None


# ─────────────────────────────────────────────────────────────
# Base Template
# ─────────────────────────────────────────────────────────────

def _base_template(content: str):

    current_year = datetime.now().year

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

      <meta charset="UTF-8" />

      <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
      />

      <title>TaskFlow</title>

    </head>

    <body style="
      margin:0;
      padding:0;
      background:#f4f7fb;
      font-family:Arial,sans-serif;
      color:#1f2937;
    ">

      <table
        width="100%"
        cellpadding="0"
        cellspacing="0"
        style="padding:40px 16px;"
      >

        <tr>

          <td align="center">

            <table
              width="100%"
              cellpadding="0"
              cellspacing="0"
              style="
                max-width:620px;
                background:#ffffff;
                border-radius:16px;
                overflow:hidden;
                box-shadow:0 4px 20px rgba(0,0,0,0.06);
              "
            >

              <!-- Header -->

              <tr>

                <td style="
                  background:#111827;
                  padding:32px;
                  text-align:center;
                ">

                  <h1 style="
                    margin:0;
                    color:white;
                    font-size:28px;
                    letter-spacing:1px;
                  ">
                    TaskFlow
                  </h1>

                  <p style="
                    margin-top:8px;
                    color:#d1d5db;
                    font-size:14px;
                  ">
                    Task Management Platform
                  </p>

                </td>

              </tr>

              <!-- Content -->

              <tr>

                <td style="
                  padding:40px 32px;
                  line-height:1.7;
                  font-size:15px;
                ">

                  {content}

                </td>

              </tr>

              <!-- Footer -->

              <tr>

                <td style="
                  padding:24px 32px;
                  background:#f9fafb;
                  border-top:1px solid #e5e7eb;
                  text-align:center;
                ">

                  <p style="
                    margin:0;
                    font-size:13px;
                    color:#6b7280;
                  ">
                    © {current_year} TaskFlow.
                    All rights reserved.
                  </p>

                  <p style="
                    margin-top:8px;
                    font-size:12px;
                    color:#9ca3af;
                  ">
                    Manage your tasks efficiently.
                  </p>

                </td>

              </tr>

            </table>

          </td>

        </tr>

      </table>

    </body>

    </html>
    """


# ─────────────────────────────────────────────────────────────
# Assignment Email
# ─────────────────────────────────────────────────────────────

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

    due = due_date if due_date else "No due date"

    content = f"""

    <p>
      Hi <strong>{assignee_name or assignee_email}</strong>,
    </p>

    <p>
      <strong>{creator_name}</strong>
      assigned a new task to you.
    </p>

    <div style="
      background:#f9fafb;
      border:1px solid #e5e7eb;
      border-radius:12px;
      padding:24px;
      margin:28px 0;
    ">

      <h2 style="
        margin-top:0;
        color:#111827;
      ">
        {task_title}
      </h2>

      <p style="
        color:#4b5563;
      ">
        {task_description or 'No description provided.'}
      </p>

      <table
        width="100%"
        cellpadding="8"
        cellspacing="0"
        style="margin-top:20px;"
      >

        <tr>

          <td>
            <strong>Priority:</strong>
          </td>

          <td>
            {priority}
          </td>

        </tr>

        <tr>

          <td>
            <strong>Due Date:</strong>
          </td>

          <td>
            {due}
          </td>

        </tr>

      </table>

    </div>

    <div style="text-align:center;">

      <a
        href="{FRONTEND_URL}/tasks/{task_id}"
        style="
          display:inline-block;
          background:#111827;
          color:white;
          padding:14px 28px;
          border-radius:10px;
          text-decoration:none;
          font-weight:bold;
        "
      >
        View Task
      </a>

    </div>
    """

    send_async(
        assignee_email,
        f"📌 Task Assigned: {task_title}",
        _base_template(content),
    )


# ─────────────────────────────────────────────────────────────
# Completion Email
# ─────────────────────────────────────────────────────────────

def notify_task_completed(
    creator_email,
    creator_name,
    completer_name,
    task_title,
    task_id,
):

    content = f"""

    <p>
      Hi <strong>{creator_name or creator_email}</strong>,
    </p>

    <p>
      Great news 🎉
    </p>

    <p>
      <strong>{completer_name}</strong>
      completed your task successfully.
    </p>

    <div style="
      background:#ecfdf5;
      border:1px solid #10b981;
      border-radius:12px;
      padding:24px;
      margin:28px 0;
    ">

      <h2 style="
        margin-top:0;
        color:#065f46;
      ">
        {task_title}
      </h2>

      <p style="
        color:#047857;
        font-weight:bold;
      ">
        Status: COMPLETED
      </p>

    </div>

    <div style="text-align:center;">

      <a
        href="{FRONTEND_URL}/tasks/{task_id}"
        style="
          display:inline-block;
          background:#10b981;
          color:white;
          padding:14px 28px;
          border-radius:10px;
          text-decoration:none;
          font-weight:bold;
        "
      >
        View Completed Task
      </a>

    </div>
    """

    send_async(
        creator_email,
        f"✅ Task Completed: {task_title}",
        _base_template(content),
    )