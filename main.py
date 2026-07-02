import os
import json
import sqlite3
import time
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from pydantic import BaseModel
from google import genai
from google.genai import types

load_dotenv()
app = FastAPI()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---- DATABASE SETUP ----
DB_NAME = "email_storage.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            body TEXT,
            category TEXT,
            reason TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database table on application startup
init_db()

# ---- PYDANTIC MODELS ----
class EmailPayload(BaseModel):
    subject: str
    body: str

class EmailCategory(BaseModel):
    category: str
    reason: str

# ---- DUMMY EMAILS FOR TESTING ----
dummy_emails = [
    {
        "id": 1,
        "subject": "Buy 1 Get 1 Free Shoes!",
        "body": "Don't miss this amazing offer. Click here to buy sneakers now!"
    },
    {
        "id": 2,
        "subject": "Update on your Application - Google",
        "body": "Thank you for interviewing with us. Unfortunately, we have decided to move forward with another candidate at this time."
    },
    {
        "id": 3,
        "subject": "Urgent: Complete your KYC",
        "body": "Your bank account will be blocked if you don't click this link immediately to update KYC."
    },
    {
        "id": 4,
        "subject": "Hey! Are we meeting today?",
        "body": "Let me know if you are free around 5 PM for a coffee."
    }
]

# ---- API ENDPOINTS ----

# 1. Classify and save a single email provided directly by the user via payload
@app.post("/classify-and-save")
def classify_and_save_email(payload: EmailPayload):
    prompt = f"Analyze this email and classify it into 'Ads', 'Spam', 'Rejected Job', or 'General'. Email: {payload.body}"
    
    ai_data = None
    retries = 3
    
    # Attempt to get response from Gemini API with Retry Logic
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=EmailCategory,
                )
            )
            ai_data = json.loads(response.text)
            break # Exit loop if successful
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2) # Wait 2 seconds before retrying if server is busy
            else:
                raise HTTPException(status_code=503, detail=f"Gemini API Error: {str(e)}")

    # Save to database if AI data was successfully parsed
    if ai_data:
        category = ai_data.get("category", "General")
        reason = ai_data.get("reason", "N/A")
        
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO emails (subject, body, category, reason) VALUES (?, ?, ?, ?)",
                (payload.subject, payload.body, category, reason)
            )
            conn.commit()
            conn.close()
        except Exception as db_err:
            raise HTTPException(status_code=500, detail=f"Database Error: {str(db_err)}")
        
        return {
            "status": "Success",
            "saved_data": {
                "subject": payload.subject,
                "category": category,
                "reason": reason
            }
        }
        
    raise HTTPException(status_code=500, detail="Failed to parse AI response.")


# 2. Automatically loop through, classify, and save all emails inside the dummy list
@app.post("/classify-and-save-all-dummy")
def classify_and_save_all_dummy():
    processed_count = 0

    for email in dummy_emails:
        prompt = f"Analyze this email and classify it into 'Ads', 'Spam', 'Rejected Job', or 'General'. Email: {email['body']}"
        
        try:
            response = client.models.generate_content(
                model='gemini-2.5-flash', 
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=EmailCategory,
                )
            )
            ai_data = json.loads(response.text)
            
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO emails (subject, body, category, reason) VALUES (?, ?, ?, ?)",
                (email["subject"], email["body"], ai_data.get("category", "General"), ai_data.get("reason", "N/A"))
            )
            conn.commit()
            conn.close()
            
            processed_count += 1
            
        except Exception as e:
            print(f"Error processing email {email['id']}: {e}")
            
        
        time.sleep(1) 
        
    return {"status": "Success", "message": f"Successfully classified and saved {processed_count} dummy emails."}


# 3. Retrieve and view all emails currently stored in the SQLite database
@app.get("/stored_emails")
def get_stored_emails():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, subject, body, category, reason FROM emails")
    rows = cursor.fetchall()
    conn.close()

    email_list = []
    for row in rows:
        email_data = {
            "id": row[0],
            "subject": row[1],
            "body": row[2],
            "category": row[3],
            "reason": row[4]
        }
        email_list.append(email_data)
        
    return {"stored_emails": email_list}