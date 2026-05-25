import os

import resend


# ───────────────────────────────────────────────────────────────────────────────
# Resend Setup
# ───────────────────────────────────────────────────────────────────────────────

resend.api_key = os.getenv("RESEND_API_KEY")


# ───────────────────────────────────────────────────────────────────────────────
# Send Email
# ───────────────────────────────────────────────────────────────────────────────

def send_async(
    to: str,
    subject: str,
    html_body: str,
):

    try:

        print("========== EMAIL DEBUG ==========", flush=True)
        print("TO:", to, flush=True)
        print("SUBJECT:", subject, flush=True)

        response = resend.Emails.send({

            "from": os.getenv(
                "EMAIL_FROM",
                "onboarding@resend.dev"
            ),

            "to": [to],

            "subject": subject,

            "html": html_body,
        })

        print(
            "[email] SENT SUCCESSFULLY",
            response,
            flush=True
        )

    except Exception as e:

        print(
            "[email] ERROR:",
            str(e),
            flush=True
        )


# ───────────────────────────────────────────────────────────────────────────────
# Base Template
# ───────────────────────────────────────────────────────────────────────────────

def _base_template(content: str):

    frontend_url = os.getenv(
        "FRONTEND_URL",
        "http://localhost:3000"
    )

    return f"""
    <!DOCTYPE html>

    <html>

    <body style="
        font-family:sans-serif;
        background:#f5f4f0;
        padding:40px;
    ">

      <div style="
        max-width:600px;
        margin:auto;
        background:white;
        padding:32px;
        border-radius:12px;
      ">

        <h2 style="margin-top:0;">
          TaskFlow
        </h2>

        {content}

        <p style="margin-top:32px;">

          <a
            href="{frontend_url}"
            style="
              display:inline-block;
              padding:12px 20px;
              background:black;
              color:white;
              text-decoration:none;
              border-radius:8px;
            "
          >
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

    due = due_date if due_date else "No due date"

    content = f"""
    <p>
      Hi {assignee_name or assignee_email},
    </p>

    <p>
      <strong>{creator_name}</strong>
      assigned a task to you.
    </p>

    <div style="
      background:#f5f5f5;
      padding:20px;
      border-radius:8px;
      margin:24px 0;
    ">

      <h3 style="margin-top:0;">
        {task_title}
      </h3>

      <p>
        {task_description or "No description"}
      </p>

      <p>
        <strong>Priority:</strong> {priority}
      </p>

      <p>
        <strong>Due:</strong> {due}
      </p>

    </div>

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
    <p>
      Hi {creator_name or creator_email},
    </p>

    <p>
      <strong>{completer_name}</strong>
      completed your task 🎉
    </p>

    <div style="
      background:#f5f5f5;
      padding:20px;
      border-radius:8px;
      margin:24px 0;
    ">

      <h3 style="margin-top:0;">
        {task_title}
      </h3>

      <p>
        Status: DONE
      </p>

    </div>

    <a href="{frontend_url}/tasks/{task_id}">
      View Task
    </a>
    """

    send_async(
        creator_email,
        f"Task Completed: {task_title}",
        _base_template(content),
    )