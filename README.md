# Local Food Wastage Management System — **SQLite-only**

This is a **Streamlit** web app that connects surplus food **providers** with **receivers/NGOs** and helps track **food listings** and **claims** — using a simple **SQLite** database (no Docker, no MySQL).

## Features

- Browse & filter food **listings** by city, provider, food type, and expiry.
- View contact details for **providers** and **receivers**.
- Full **CRUD** for: Providers, Receivers, Listings, Claims.
- **Analytics** dashboard with a set of SQL-powered charts/tables.
- Single-file database: **`food_system.db`**.

## Quickstart

```bash
# 1) (Recommended) use a virtual env, then:
pip install -r requirements.txt

# 2) Create & seed the SQLite DB from CSVs (optional; you can also start empty)
python load_csv_to_sqlite.py

# 3) Run the app
streamlit run main.py
```

> **Note:** If you already have `providers_clean.csv`, `receivers_clean.csv`, `food_listings_clean.csv`, and `claims_clean.csv` in the project root, step (2) will create `food_system.db` and load them. If the CSVs are missing, the script creates an empty DB with the right schema.

## Project Structure

```
food-wastage-management-sqlite/
├─ main.py
├─ db.py
├─ load_csv_to_sqlite.py
├─ requirements.txt
├─ README.md
├─ sample_csvs/
│  ├─ providers_clean.csv
│  ├─ receivers_clean.csv
│  ├─ food_listings_clean.csv
│  └─ claims_clean.csv
└─ food_system.db   # created after running the loader (or at first run)
```

## Tables (SQLite)

- **providers**: id, name, type, city, contact_name, phone, email
- **receivers**: id, name, type, city, contact_name, phone, email
- **food_listings**: id, provider_id, food_type, meal_type, quantity_kg, listed_at, expires_at, city, notes
- **claims**: id, listing_id, receiver_id, status, claimed_at, fulfilled_at, notes

### Status values
- `claims.status` ∈ {`pending`, `approved`, `picked_up`, `cancelled`}

## Environment

- Python 3.9+
- Streamlit 1.36+
- SQLite 3.x

## Migrations
If you need to reset the database, simply delete `food_system.db` and re-run `python load_csv_to_sqlite.py`.

## License
MIT
