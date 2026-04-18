"""
Email Service - Send emails via SMTP
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import logging

from src.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.SMTP_FROM_EMAIL
        self.use_tls = settings.SMTP_USE_TLS
        self.frontend_url = settings.FRONTEND_URL

    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email via SMTP"""
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured. Email not sent.")
            print(f"\n[EMAIL MOCK] To: {to_email}")
            print(f"Subject: {subject}")
            print(f"Content: {html_content[:200]}...\n")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email

            html_part = MIMEText(html_content, "html")
            msg.attach(html_part)

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_email, to_email, msg.as_string())

            logger.info(f"Email sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            print(f"[EMAIL ERROR] {e}")
            return False


    def send_invite_email(self, to_email: str, org_name: str, inviter_name: str, role: str, project_name: str = None, invite_token: str = None) -> bool:
        """Send organization or project invite email"""
        try:
            signup_url = f"{self.frontend_url}/signup"
            
            project_section = ""
            if project_name:
                project_section = f"""
                <div class="project-details">
                    <p><strong>Project:</strong> {project_name}</p>
                </div>
                """
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 0;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                        background-color: #ffffff;
                    }}
                    .header {{
                        background-color: #059669;
                        color: white;
                        padding: 30px;
                        text-align: center;
                        border-radius: 8px 8px 0 0;
                    }}
                    .content {{
                        padding: 30px;
                        color: #333333;
                    }}
                    .project-details {{
                        background-color: #f0fdf4;
                        padding: 15px;
                        border-radius: 6px;
                        margin: 20px 0;
                        border-left: 4px solid #059669;
                    }}
                    .button {{
                        display: inline-block;
                        padding: 12px 24px;
                        background-color: #059669;
                        color: white;
                        text-decoration: none;
                        border-radius: 6px;
                        margin: 20px 0;
                    }}
                    .footer {{
                        text-align: center;
                        padding: 20px;
                        color: #666666;
                        font-size: 12px;
                        border-top: 1px solid #eeeeee;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Brick SPMES</h1>
                    </div>
                    <div class="content">
                        <h2>You've been invited to join {org_name}!</h2>
                        <p><strong>{inviter_name}</strong> has invited you to join their organization on Brick SPMES as a <strong>{role}</strong>.</p>
                        {project_section}
                        <p>Brick helps teams monitor projects, track budgets, manage tasks, and generate reports in real time.</p>
                        <div style="text-align: center;">
                            <a href="{signup_url}" class="button">Accept Invitation</a>
                        </div>
                        <p>If the button doesn't work, copy and paste this link into your browser:</p>
                        <p><a href="{signup_url}">{signup_url}</a></p>
                        <p>After signing up, you'll automatically join <strong>{org_name}</strong>{f" and the project <strong>{project_name}</strong>" if project_name else ""} and can start collaborating.</p>
                    </div>
                    <div class="footer">
                        <p>&copy; 2026 Brick SPMES. All rights reserved.</p>
                        <p>This is an automated message, please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            subject = f"Invitation to join {org_name}" + (f" - {project_name}" if project_name else "") + " on Brick SPMES"
            
            # If SMTP is not configured, just log and return True
            if not self.smtp_user or not self.smtp_password:
                print(f"\n[EMAIL MOCK] To: {to_email}")
                print(f"Subject: {subject}")
                print(f"Content: {html_content[:500]}...\n")
                print("NOTE: Email not actually sent because SMTP is not configured.")
                return True
                
            return self._send_email(to_email, subject, html_content)
            
        except Exception as e:
            print(f"Error in send_invite_email: {e}")
            # Return True anyway so the invite can still be created
            return True


    def send_task_assigned_email(self, to_email: str, task_title: str, project_title: str, due_date: str, assigned_by: str) -> bool:
        """Send task assignment email"""
        dashboard_url = f"{self.frontend_url}/dashboard"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #ffffff;
                }}
                .header {{
                    background-color: #059669;
                    color: white;
                    padding: 30px;
                    text-align: center;
                    border-radius: 8px 8px 0 0;
                }}
                .content {{
                    padding: 30px;
                    color: #333333;
                }}
                .task-details {{
                    background-color: #f9f9f9;
                    padding: 15px;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
                .button {{
                    display: inline-block;
                    padding: 12px 24px;
                    background-color: #059669;
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    margin: 20px 0;
                }}
                .footer {{
                    text-align: center;
                    padding: 20px;
                    color: #666666;
                    font-size: 12px;
                    border-top: 1px solid #eeeeee;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Brick SPMES</h1>
                </div>
                <div class="content">
                    <h2>New Task Assigned: {task_title}</h2>
                    <p><strong>{assigned_by}</strong> has assigned you a new task.</p>
                    
                    <div class="task-details">
                        <p><strong>Project:</strong> {project_title}</p>
                        <p><strong>Due Date:</strong> {due_date}</p>
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="{dashboard_url}" class="button">View Task</a>
                    </div>
                </div>
                <div class="footer">
                    <p>&copy; 2026 Brick SPMES. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        subject = f"New Task Assigned: {task_title}"
        return self._send_email(to_email, subject, html_content)


email_service = EmailService()