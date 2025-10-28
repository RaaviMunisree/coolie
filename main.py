# from fastapi import FastAPI
# from pydantic import BaseModel
# import sqlite3
# import random

# DB_NAME = "bookings.db"

# app = FastAPI(title="Coolie No.1 API")

# # Mock coolies
# coolies = [
#     {"name": "Raju", "rating": 4.5, "station": "Gwalior"},
#     {"name": "Sita", "rating": 4.2, "station": "Jaipur"},
#     {"name": "Amit", "rating": 4.8, "station": "Udaipur"},
#     {"name": "Pooja", "rating": 4.7, "station": "Delhi"},
#     {"name": "Rahul", "rating": 4.6, "station": "Mumbai"},
# ]

# # Translation dictionaries
# translations = {
#     "Hindi": {"hello":"नमस्ते"},
#     "Marathi": {"hello":"नमस्कार"},
#     "Tamil": {"hello":"வணக்கம்"},
#     "Bengali": {"hello":"নমস্কার"},
#     "Gujarati": {"hello":"નમસ્તે"},
# }

# # Pydantic models
# class Booking(BaseModel):
#     passenger: str
#     city: str
#     arrival: str
#     luggage_weight: float
#     service: str

# class Translation(BaseModel):
#     text: str
#     language: str

# # -------------------
# # API Endpoints
# # -------------------

# @app.post("/book")
# def book_service(booking: Booking):
#     # assign helper
#     available = [c for c in coolies if c["station"]==booking.city]
#     if not available:
#         assigned = random.choice(coolies)
#         fallback_msg = f"No local helper at {booking.city}, assigned {assigned['name']}"
#     else:
#         assigned = random.choice(available)
#         fallback_msg = ""

#     fare = 30 + booking.luggage_weight*2.5

#     # Save to SQLite
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#     cursor.execute("""
#         INSERT INTO bookings (passenger, city, arrival, luggage_weight, service, assigned_helper, fare)
#         VALUES (?, ?, ?, ?, ?, ?, ?)
#     """, (booking.passenger, booking.city, booking.arrival, booking.luggage_weight, booking.service, assigned["name"], fare))
#     conn.commit()
#     conn.close()

#     return {"message": "Booking confirmed", "assigned_helper": assigned["name"], "fare": fare, "fallback": fallback_msg}


# @app.get("/bookings")
# def get_bookings():
#     conn = sqlite3.connect(DB_NAME)
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM bookings")
#     data = cursor.fetchall()
#     conn.close()
#     return {"bookings": data}


# @app.post("/translate")
# def translate(trans: Translation):
#     text = trans.text.lower()
#     language = trans.language
#     dictionary = translations.get(language, {})
#     translated = " ".join([dictionary.get(word, word) for word in text.split()])
#     return {"translated_text": translated}


# main.py
from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import random
import os

# -------------------------------
# Database setup
# -------------------------------
DB_NAME = "bookings.db"

def init_db():
    """Initialize the SQLite database and bookings table"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            passenger TEXT,
            city TEXT,
            arrival TEXT,
            luggage_weight REAL,
            service TEXT,
            assigned_helper TEXT,
            fare REAL
        )
    """)
    conn.commit()
    conn.close()
    print(f"Database '{DB_NAME}' initialized successfully.")

# Initialize DB before starting FastAPI app
init_db()

# -------------------------------
# FastAPI app setup
# -------------------------------
app = FastAPI(title="Coolie No.1 API")

# -------------------------------
# Mock data
# -------------------------------
coolies = [
    {"name": "Raju", "rating": 4.5, "station": "Gwalior"},
    {"name": "Sita", "rating": 4.2, "station": "Jaipur"},
    {"name": "Amit", "rating": 4.8, "station": "Udaipur"},
    {"name": "Pooja", "rating": 4.7, "station": "Delhi"},
    {"name": "Rahul", "rating": 4.6, "station": "Mumbai"},
]

translations = {
    "Hindi": {"hello": "नमस्ते"},
    "Marathi": {"hello": "नमस्कार"},
    "Tamil": {"hello": "வணக்கம்"},
    "Bengali": {"hello": "নমস্কার"},
    "Gujarati": {"hello": "નમસ્તે"},
}

# -------------------------------
# Pydantic models
# -------------------------------
class Booking(BaseModel):
    passenger: str
    city: str
    arrival: str
    luggage_weight: float
    service: str

class Translation(BaseModel):
    text: str
    language: str

# -------------------------------
# API Endpoints
# -------------------------------
@app.post("/book")
def book_service(booking: Booking):
    # Assign helper
    available = [c for c in coolies if c["station"] == booking.city]
    if not available:
        assigned = random.choice(coolies)
        fallback_msg = f"No local helper at {booking.city}, assigned {assigned['name']}"
    else:
        assigned = random.choice(available)
        fallback_msg = ""

    fare = 30 + booking.luggage_weight * 2.5

    # Save booking to DB
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO bookings 
        (passenger, city, arrival, luggage_weight, service, assigned_helper, fare)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (booking.passenger, booking.city, booking.arrival, booking.luggage_weight,
          booking.service, assigned["name"], fare))
    conn.commit()
    conn.close()

    return {"message": "Booking confirmed", "assigned_helper": assigned["name"], "fare": fare, "fallback": fallback_msg}

@app.get("/bookings")
def get_bookings():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings")
    data = cursor.fetchall()
    conn.close()
    return {"bookings": data}

@app.post("/translate")
def translate(trans: Translation):
    text = trans.text.lower()
    language = trans.language
    dictionary = translations.get(language, {})
    translated = " ".join([dictionary.get(word, word) for word in text.split()])
    return {"translated_text": translated}
