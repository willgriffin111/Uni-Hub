import os
import time
import logging
import pyotp
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

logging.getLogger("python_http_client").setLevel(logging.INFO) # Stop email template debug logs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

otp_store = {}

def generate_otp(email):
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)
    otp = totp.now()
    otp_store[email] = {"otp": otp, "secret": secret, "timestamp": time.time()}

    logger.debug(f"Generated OTP for {email}: {otp}")
    logger.debug(f"Stored secret for {email}: {secret}")
    return otp

def load_email_template(filename, otp_code):
    template_path = os.path.join(BASE_DIR, filename)

    try:
        with open(template_path, "r", encoding="utf-8") as file:
            html_content = file.read()
        return html_content.replace("{{OTP_CODE}}", otp_code)
    except FileNotFoundError:
        print(f"Error: Template file not found at {template_path}")
        return None

def send_otp_email(email, otp_code):
    email_body = load_email_template("optTemplate.html", otp_code)
    message = Mail(
        from_email='donotreply@unihub.help',
        to_emails=email,
        subject='Your One-Time Password (OTP)',
        html_content=email_body
    )
    try:
        sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        response = sg.send(message)
        print(f"OTP Email Sent! Status: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")
        raise

def load_email_template_password_reset(filename, reset_link):
    template_path = os.path.join(BASE_DIR, filename)
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
        sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
        response = sg.send(message)
        print(f"Password Reset Email Sent! Status: {response.status_code}")
    except Exception as e:
        print(f"Error sending email: {e}")
        raise

def load_email_template_event_confirmation(filename, title, description, date, time, location):
    template_path = os.path.join(BASE_DIR, filename)
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            html = f.read()
    except FileNotFoundError:
        logger.error(f"Template not found: {template_path}")
        return None

    html = html.replace("{{EVENT_TITLE}}", title)
    html = html.replace("{{EVENT_DESCRIPTION}}", description)
    html = html.replace("{{EVENT_DATE}}", date)
    html = html.replace("{{EVENT_TIME}}", time)
    html = html.replace("{{EVENT_LOCATION}}", location)
    return html

def send_event_confirmation_email(email, title, description, date, time, location):
    body = load_email_template_event_confirmation(
        "event_confirmation_template.html",
        title, description, date, time, location
    )
    if body is None:
        raise RuntimeError("Event confirmation template missing")

    message = Mail(
        from_email="donotreply@unihub.help",
        to_emails=email,
        subject=f"You're attending: {title}",
        html_content=body
    )
    sg = SendGridAPIClient(os.environ["SENDGRID_API_KEY"])
    resp = sg.send(message)
    logger.info(f"Sent event-confirm email to {email}, status={resp.status_code}")
    return resp.status_code