import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pyrogram import Client
from pyrogram.raw.functions.contacts import ImportContacts
from pyrogram.raw.types import InputPhoneContact as PyrogramInputPhoneContact

# Load .env variables
load_dotenv()

API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SESSION_NAME = os.getenv('SESSION_NAME')

# Initialize Pyrogram client
app_pyro = Client(SESSION_NAME, api_id=int(API_ID), api_hash=API_HASH)

# Initialize FastAPI app
app = FastAPI(docs_url='/', title='Get Username Api')


@app.get("/get_username/{phone_number}", status_code=200)
async def get_username(phone_number: str):
    if not phone_number.startswith('+'):
        raise HTTPException(status_code=400, detail="Invalid phone number. Must start with '+'.")

    async with app_pyro:
        try:
            # Use Pyrogram to import the contact and get the username
            contact = PyrogramInputPhoneContact(client_id=0, phone=phone_number, first_name="temp", last_name="")
            result = await app_pyro.invoke(ImportContacts(contacts=[contact]))

            if result.users:
                user = result.users[0]
                username = user.username if user.username else None

                if username:
                    return {"username": username, "status_code": 200}
                else:
                    raise HTTPException(status_code=404, detail="No username found.")
            else:
                raise HTTPException(status_code=404, detail="No user found with this phone number.")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

# Run with: uvicorn script_name:app --reload
