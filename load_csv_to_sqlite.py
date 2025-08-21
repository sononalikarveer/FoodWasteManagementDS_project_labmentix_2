# load_csv_to_sqlite.py
import os
import pandas as pd
from db import get_db_connection, init_db


def safe_load(df, expected_cols, table):
    """Ensure dataframe has expected columns (match schema)."""
    df = df.copy()
    for col in expected_cols:
        if col not in df.columns:
            df[col] = None
    return df[expected_cols]

def load_csv_if_exists(table, csv_name):
    if not os.path.exists(csv_name):
        print(f"[INFO] {csv_name} not found. Skipping seed for {table}.")
        return

    df = pd.read_csv(csv_name)
    print(f"[INFO] Loading {len(df)} rows into {table} from {csv_name}...")

    conn = get_db_connection()
    cur = conn.cursor()

    if table == 'providers':
        cols = ['Provider_ID','Name','Type','Address','City','Contact']
        df = safe_load(df, cols, table)
        rows = [tuple(x) for x in df.to_records(index=False)]
        cur.executemany("""
            INSERT OR REPLACE INTO providers(Provider_ID, Name, Type, Address, City, Contact)
            VALUES (?,?,?,?,?,?)
        """, rows)

    elif table == 'receivers':
        cols = ['Receiver_ID','Name','Type','City','Contact']
        df = safe_load(df, cols, table)
        rows = [tuple(x) for x in df.to_records(index=False)]
        cur.executemany("""
            INSERT OR REPLACE INTO receivers(Receiver_ID, Name, Type, City, Contact)
            VALUES (?,?,?,?,?)
        """, rows)

    elif table == 'food_listings':
        cols = ['Food_ID','Food_Name','Quantity','Expiry_Date','Provider_ID','Provider_Type','Location','Food_Type','Meal_Type']
        df = safe_load(df, cols, table)
        rows = [tuple(x) for x in df.to_records(index=False)]
        cur.executemany("""
            INSERT OR REPLACE INTO food_listings(Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, rows)

    elif table == 'claims':
        cols = ['Claim_ID','Food_ID','Receiver_ID','Status','Timestamp']
        df = safe_load(df, cols, table)
        rows = [tuple(x) for x in df.to_records(index=False)]
        cur.executemany("""
            INSERT OR REPLACE INTO claims(Claim_ID, Food_ID, Receiver_ID, Status, Timestamp)
            VALUES (?,?,?,?,?)
        """, rows)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    load_csv_if_exists("providers", r"C:\Users\sonal\Downloads\food-wastage-management-sqlite\food-wastage-management-sqlite\providers_clean.csv")
    load_csv_if_exists("receivers", r"C:\Users\sonal\Downloads\food-wastage-management-sqlite\food-wastage-management-sqlite\receivers_clean.csv")
    load_csv_if_exists("food_listings", r"C:\Users\sonal\Downloads\food-wastage-management-sqlite\food-wastage-management-sqlite\food_listings_clean.csv")
    load_csv_if_exists("claims", r"C:\Users\sonal\Downloads\food-wastage-management-sqlite\food-wastage-management-sqlite\claims_clean.csv")
    print("[INFO] All CSV data loaded successfully.")
