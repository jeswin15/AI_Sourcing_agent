import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.utils.config import Config
import logging

class EmailService:
    def __init__(self):
        self.logger = logging.getLogger("integrations.email")
        self.logger.setLevel(logging.INFO)
        self.smtp_server = Config.SMTP_SERVER
        self.smtp_port = Config.SMTP_PORT
        self.smtp_user = Config.SMTP_USER
        self.smtp_password = Config.SMTP_PASSWORD
        self.sender = Config.OUTREACH_EMAIL_SENDER

    def send_outreach_email(self, startup_name: str, startup_link: str, rationale: str, recipient_email: str):
        """
        Sends an outreach email for a high-potential startup.
        """
        if not self.smtp_user or not self.smtp_password:
            self.logger.warning("SMTP credentials not provided, skipping email outreach.")
            return

        subject = f"Investment Interest – Holocene: {startup_name}"
        body = f"""
        Hello,

        We are from Holocene and we have been tracking your progress with {startup_name}.
        
        Your solution caught our attention due to:
        {rationale}
        
        We would love to learn more about your current stage and potential for growth. 
        Could you please share some more information or schedule a quick call?
        
        Best regards,
        Investment Team @ Holocene
        """

        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
                self.logger.info(f"Outreach email sent for {startup_name} to {recipient_email}")
        except Exception as e:
            self.logger.error(f"Failed to send outreach email: {e}")
