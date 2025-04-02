from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from emailFuncs import *

app = FastAPI()

class EmailOTPRequest(BaseModel):
    email: str

class PasswordResetRequest(BaseModel):
    email: str
    link: str

@app.post("/send-otp")
def send_otp(data: EmailOTPRequest):
    otp = generate_otp(data.email)
    try:
        send_otp_email(data.email, otp)
        return {"message": "OTP sent", "otp": otp}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/send-reset-link")
def send_reset_link(data: PasswordResetRequest):
    try:
        send_email_password_reset(data.email, data.link)
        return {"message": "Password reset email sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
