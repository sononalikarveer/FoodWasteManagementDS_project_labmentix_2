import sqlite3

DB_NAME = "food_donation.db"

def get_db_connection():
    return sqlite3.connect(DB_NAME)

def execute(sql, params=()):
    """Execute INSERT/UPDATE/DELETE queries."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    conn.close()

def fetchall(sql, params=()):
    """Execute SELECT queries and return all rows."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # Providers table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS providers (
            Provider_ID TEXT PRIMARY KEY,
            Name TEXT,
            Type TEXT,
            Address TEXT,
            City TEXT,
            Contact TEXT
        )
    """)

    # Receivers table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS receivers (
            Receiver_ID TEXT PRIMARY KEY,
            Name TEXT,
            Type TEXT,
            City TEXT,
            Contact TEXT
        )
    """)

    # Food listings table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS food_listings (
            Food_ID TEXT PRIMARY KEY,
            Food_Name TEXT,
            Quantity INTEGER,
            Expiry_Date TEXT,
            Provider_ID TEXT,
            Provider_Type TEXT,
            Location TEXT,
            Food_Type TEXT,
            Meal_Type TEXT,
            FOREIGN KEY (Provider_ID) REFERENCES providers(Provider_ID)
        )
    """)

    # Claims table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS claims (
            Claim_ID TEXT PRIMARY KEY,
            Food_ID TEXT,
            Receiver_ID TEXT,
            Status TEXT,
            Timestamp TEXT,
            FOREIGN KEY (Food_ID) REFERENCES food_listings(Food_ID),
            FOREIGN KEY (Receiver_ID) REFERENCES receivers(Receiver_ID)
        )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("[INFO] Database initialized successfully.")
