import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings

import pyotp
import time

# Simulated storage (Replace with a database or Redis in production)
otp_store = {}

# Generate and store OTP
def generate_otp(email):
    secret = pyotp.random_base32()  # Generate a new secret per user
    totp = pyotp.TOTP(secret)
    otp = totp.now()

    # Store OTP & secret
    otp_store[email] = {"otp": otp, "secret": secret, "timestamp": time.time()}
    
    return otp

# Fetch OTP (For debugging; remove in production)
def get_stored_otp(email):
    return otp_store.get(email, None)

# Read the HTML template
def load_email_template(filename, otp_code):
    template_path = os.path.join(settings.BASE_DIR, "accounts", filename)  # Adjust folder name if needed
    try:
        with open(template_path, "r", encoding="utf-8") as file:
            html_content = file.read()
        return html_content.replace("{{OTP_CODE}}", otp_code)
    except FileNotFoundError:
        print(f"Error: Template file not found at {template_path}")
        return None

# Send OTP email
def send_otp_email(email,otp_code):
    email_body = load_email_template("optTemplate.html", otp_code)  # Load email template

    message = Mail(
        from_email='donotreply@unihub.help',
        to_emails=email,
        subject='Your One-Time Password (OTP)',
        html_content=email_body
    )

    try: #please for the love of god remember to put this in a env file i beg
        # sg = SendGridAPIClient('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')
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"OTP Email Sent! Status: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")


def load_email_template_password_reset(filename, reset_link):
    template_path = os.path.join(settings.BASE_DIR, "accounts", filename)  
    try:
        with open(template_path, "r", encoding="utf-8") as file:
            html_content = file.read()
        return html_content.replace("{{RESET_LINK}}", reset_link)
    except FileNotFoundError:
        print(f"Error: Template file not found at {template_path}")
        return None

def send_email_password_reset(email, reset_link):
    email_body = load_email_template_password_reset("password_reset_template.html", reset_link)
    message = Mail(
        from_email='donotreply@unihub.help',
        to_emails=email,
        subject='Reset Your Password',
        html_content=email_body
    )
    try:
        # sg = SendGridAPIClient('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')
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)
        print(f"Password Reset Email Sent! Status: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")
