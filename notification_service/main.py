from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from emailFuncs import *

app = FastAPI()

class EmailOTPRequest(BaseModel):
    email: str

class PasswordResetRequest(BaseModel):
    email: str
    link: str

class EventConfirmRequest(BaseModel):
    email: str
    event_title: str
    event_description: str
    event_date: str
    event_time: str
    event_location: str

   
@app.post("/send-otp/") 
@app.post("/send-otp")
def send_otp(data: EmailOTPRequest):
    otp = generate_otp(data.email)
    try:
        send_otp_email(data.email, otp)
        return {"message": "OTP sent", "otp": otp}
    except Exception as e:
        print("BABALBALBALABALB")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-reset-link")
def send_reset_link(data: PasswordResetRequest):
    try:
        send_email_password_reset(data.email, data.link)
        return {"message": "Password reset email sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-event-confirmation")
@app.post("/send-event-confirmation/")
def send_event_confirm(req: EventConfirmRequest):
    try:
        status = send_event_confirmation_email(
            req.email,
            req.event_title,
            req.event_description,
            req.event_date,
            req.event_time,
            req.event_location
        )
        return {"message": "Confirmation email sent", "status": status}
    except Exception as e:
        raise HTTPException(500, str(e))