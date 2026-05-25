import os

import sib_api_v3_sdk

from sib_api_v3_sdk.rest import ApiException

from datetime import datetime


# ─────────────────────────────────────────────────────────────
# Brevo Setup
# ─────────────────────────────────────────────────────────────

configuration = sib_api_v3_sdk.Configuration()

configuration.api_key['api-key'] = os.getenv(
    "BREVO_API_KEY"
)

api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
    sib_api_v3_sdk.ApiClient(configuration)
)

EMAIL_FROM = os.getenv(
    "EMAIL_FROM",
    "yourgmail@gmail.com"
)

EMAIL_FROM_NAME = os.getenv(
    "EMAIL_FROM_NAME",
    "TaskFlow"
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
        print("TO:", to)
        print("SUBJECT:", subject)
        print("=================================\n")

        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(

            sender={
                "name": EMAIL_FROM_NAME,
                "email": EMAIL_FROM
            },

            to=[
                {
                    "email": to
                }
            ],

            subject=subject,

            html_content=html_body,
        )

        response = api_instance.send_transac_email(
            send_smtp_email
        )

        print(
            "[EMAIL] SENT SUCCESSFULLY:",
            response,
            flush=True
        )

        return response

    except ApiException as e:

        print(
            "[BREVO ERROR]:",
            str(e),
            flush=True
        )

        return None

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

      <meta charset="UTF-8">

      <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
      >

      <title>TaskFlow</title>

    </head>

    <body style="
      margin:0;
      padding:0;
      background:#f4f4f5;
      font-family:Arial,sans-serif;
      color:#111827;
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
                background:white;
                border-radius:16px;
                overflow:hidden;
                box-shadow:0 4px 16px rgba(0,0,0,0.08);
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
                  ">
                    TaskFlow
                  </h1>

                  <p style="
                    color:#d1d5db;
                    margin-top:8px;
                    font-size:14px;
                  ">
                    Smart Task Management
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
                  background:#f9fafb;
                  border-top:1px solid #e5e7eb;
                  padding:24px;
                  text-align:center;
                ">

                  <p style="
                    margin:0;
                    font-size:13px;
                    color:#6b7280;
                  ">
                    © {current_year} TaskFlow
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
      Hi
      <strong>{assignee_name or assignee_email}</strong>,
    </p>

    <p>
      <strong>{creator_name}</strong>
      assigned a new task to you.
    </p>

    <div style="
      background:#f9fafb;
      border:1px solid #e5e7eb;
      padding:24px;
      border-radius:12px;
      margin:24px 0;
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
        {task_description or "No description provided"}
      </p>

      <p>
        <strong>Priority:</strong>
        {priority}
      </p>

      <p>
        <strong>Due Date:</strong>
        {due}
      </p>

    </div>

    <div style="text-align:center;">

      <a
        href="{FRONTEND_URL}/tasks/{task_id}"
        style="
          display:inline-block;
          background:#111827;
          color:white;
          padding:14px 28px;
          border-radius:8px;
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
      Hi
      <strong>{creator_name or creator_email}</strong>,
    </p>

    <p>
      <strong>{completer_name}</strong>
      completed your task 🎉
    </p>

    <div style="
      background:#ecfdf5;
      border:1px solid #10b981;
      padding:24px;
      border-radius:12px;
      margin:24px 0;
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
          border-radius:8px;
          text-decoration:none;
          font-weight:bold;
        "
      >
        View Task
      </a>

    </div>
    """

    send_async(
        creator_email,
        f"✅ Task Completed: {task_title}",
        _base_template(content),
    )