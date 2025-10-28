from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from datetime import datetime
from deep_translator import GoogleTranslator

DB_FILE = "bookings.db"

app = FastAPI(title="Coolie No.1 Production")

# ---------------------------
# CORS
# ---------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------
# Booking Model
# ---------------------------
class Booking(BaseModel):
    name: str
    country: str = "India"
    state: str
    city: str
    luggage_weight: float
    arrival_time: str
    service_type: str
    # Add more fields here anytime, defaults ensure old rows are safe

# Translation Model
class TranslateRequest(BaseModel):
    text: str
    source: str = "auto"
    target: str

# ---------------------------
# Dynamic DB Initialization with default values
# ---------------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Minimal table creation
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT
        )
    ''')

    # Existing columns in DB
    c.execute("PRAGMA table_info(bookings)")
    existing_cols = [col[1] for col in c.fetchall()]

    # Booking fields from Pydantic model
    booking_fields = Booking.__annotations__  # dict of field_name: type
    type_mapping = {str: "TEXT", float: "REAL", int: "INTEGER", bool: "INTEGER"}

    for field_name, field_type in booking_fields.items():
        col_type = type_mapping.get(field_type, "TEXT")
        if field_name not in existing_cols:
            # Add column
            c.execute(f"ALTER TABLE bookings ADD COLUMN {field_name} {col_type}")
            # Set default value for existing rows
            default_value = getattr(Booking, field_name, None)
            if default_value is not None:
                c.execute(f"UPDATE bookings SET {field_name} = ?", (default_value,))

    # Ensure helper, fare, timestamp exist
    for extra in ["helper", "fare", "timestamp"]:
        if extra not in existing_cols:
            c.execute(f"ALTER TABLE bookings ADD COLUMN {extra} TEXT")
            c.execute(f"UPDATE bookings SET {extra} = ''")  # empty default

    conn.commit()
    conn.close()

init_db()

# ---------------------------
# Booking Endpoint
# ---------------------------
@app.post("/book")
def book_trolley(data: Booking):
    fare = 30 + data.luggage_weight * 2.5
    helper = f"Assigned Helper {data.city[:2].upper()}"
    timestamp = datetime.now().isoformat()

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    fields = list(data.dict().keys()) + ["helper", "fare", "timestamp"]
    values = list(data.dict().values()) + [helper, fare, timestamp]

    placeholders = ", ".join(["?"] * len(fields))
    columns = ", ".join(fields)

    c.execute(f"INSERT INTO bookings ({columns}) VALUES ({placeholders})", values)
    conn.commit()
    conn.close()

    return {
        "status": "success",
        **data.dict(),
        "helper": helper,
        "fare": fare,
        "timestamp": timestamp
    }

# ---------------------------   
# Fetch All Bookings
# ---------------------------
@app.get("/bookings")
def get_bookings():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("PRAGMA table_info(bookings)")
    cols = [col[1] for col in c.fetchall()]

    c.execute("SELECT * FROM bookings ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    return {
        "bookings": [dict(zip(cols, r)) for r in rows]
    }

# ---------------------------
# Translation Endpoint
# ---------------------------
@app.post("/translate")
def translate_text(req: TranslateRequest):
    try:
        translated = GoogleTranslator(source=req.source, target=req.target).translate(req.text)
        return {"translatedText": translated}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
