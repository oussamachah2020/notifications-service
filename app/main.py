from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, model_rebuild  # Import model_rebuild

import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import List
from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushMessage,
    PushTicket,
    PushServerError,
    PushTicketError,
)

class NotificationBody(BaseModel):
    userId: str
    title: str
    content: str

# Load environment variables from the .env file
load_dotenv()

app = FastAPI()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")
supabase: Client = create_client(url, key)

def getUsersPushToken(userId: str):
    response = supabase.table('tokens').select("push_token").eq("user_id", userId).execute()
    if response:
        data = response.data
        if data:
            push_tokens = [entry["push_token"] for entry in data]
            return push_tokens
    raise HTTPException(status_code=500, detail="Supabase request failed")


def notifyUser(body: NotificationBody):
    push_tokens = getUsersPushToken(body.userId)
    failed_push_tokens = []

    if push_tokens:
        for push_token in push_tokens:
            try:
                ticket: PushTicket = PushClient().publish(
                    PushMessage(to=push_token,
                                title=body.title,
                                body=body.content))

                if ticket.status == "ok":
                    return "Notification sent successfully !"
            except Exception as e:
                failed_push_tokens.append({"push_token": push_token, "error": str(e)})

    if failed_push_tokens:
        raise HTTPException(status_code=500, detail={"message": "Some notifications failed to send", "failed_tokens": failed_push_tokens})


@app.post("/send-notification")
def notify(body: NotificationBody):
    notifyUser(body)
    return {"message": "Notifications sent successfully"}

# For the "/check" route, you can use the getUsersPushToken function
@app.post("/check")
async def check(body: NotificationBody):
    push_tokens = await getUsersPushToken(body.userId)
    return {"push_tokens": push_tokens}

# Apply model_rebuild to Pydantic models to suppress the warnings
NotificationBody = model_rebuild(NotificationBody)
