import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from dotenv import load_dotenv

from deep_reader.models import Paper

class EmailNotifier:
    def __init__(self):
        load_dotenv()
        self.host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.port = int(os.getenv("SMTP_PORT", "587"))
        self.user = os.getenv("SMTP_USER")
        self.password = os.getenv("SMTP_PASSWORD")
        self.sender_email = os.getenv("SENDER_EMAIL", self.user)
        self.recipient_email = os.getenv("RECIPIENT_EMAIL")

    def send_daily_digest(self, papers: List[Paper]):
        """Sends an email with the list of papers."""
        if not papers:
            print("No papers to send.")
            return

        if not self.user or not self.password or not self.recipient_email:
            print("SMTP credentials or recipient not set. Skipping email.")
            return

        msg = MIMEMultipart()
        msg["From"] = self.sender_email
        msg["To"] = self.recipient_email
        msg["Subject"] = f"DeepReader Daily Digest - {len(papers)} Papers"

        body = self._format_email_body(papers)
        msg.attach(MIMEText(body, "html"))

        try:
            with smtplib.SMTP(self.host, self.port) as server:
                server.starttls()
                server.login(self.user, self.password)
                server.send_message(msg)
            print(f"Email sent to {self.recipient_email}")
        except Exception as e:
            print(f"Failed to send email: {e}")

    def _format_email_body(self, papers: List[Paper]) -> str:
        html = "<h1>Daily Research Papers</h1>"
        for paper in papers:
            html += f"""
            <div style="margin-bottom: 20px; border-bottom: 1px solid #ccc; padding-bottom: 10px;">
                <h3><a href="{paper.pdf_url or '#'}">{paper.title}</a></h3>
                <p><strong>Authors:</strong> {', '.join(paper.authors)}</p>
                <p><strong>Category:</strong> {paper.primary_category}</p>
                <p>{paper.summary[:500]}...</p>
                <p><em>Published: {paper.published_date.strftime('%Y-%m-%d')}</em></p>
            </div>
            """
        return html
