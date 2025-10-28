def init_db():
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
    print(f"Database {DB_NAME} initialized successfully")
