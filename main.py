# main.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from db import get_db_connection, init_db

st.set_page_config(page_title="Food Wastage Management", layout="wide")

@st.cache_data
def get_df(sql, params=()):
    """Run SQL query and return DataFrame"""
    conn = get_db_connection()
    cur = conn.execute(sql, params)
    rows = cur.fetchall()
    cols = [desc[0] for desc in cur.description]
    conn.close()
    return pd.DataFrame(rows, columns=cols)


def main():
    st.title("🍽️ Food Wastage Management System")
    init_db()

    menu = ["Dashboard","Providers", "Receivers", "Food Listings", "Claims", "SQL Insights"]
    choice = st.sidebar.selectbox("📌 Menu", menu)

    # ---------------- Dashboard ----------------
    if choice == "Dashboard":
        st.header("📊 Dashboard Overview")

        total_providers = get_df("SELECT COUNT(*) as c FROM providers")["c"].iloc[0]
        total_receivers = get_df("SELECT COUNT(*) as c FROM receivers")["c"].iloc[0]
        total_food = get_df("SELECT COUNT(*) as c FROM food_listings")["c"].iloc[0]
        total_claims = get_df("SELECT COUNT(*) as c FROM claims")["c"].iloc[0]

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Providers", total_providers)
        col2.metric("Receivers", total_receivers)
        col3.metric("Food Listings", total_food)
        col4.metric("Claims", total_claims)
    
    
    
    # ---------------- Providers ----------------
    elif choice == "Providers":
        st.header("🏢 Providers")
        df = get_df("SELECT * FROM providers")
        st.dataframe(df)

    # ---------------- Receivers ----------------
    elif choice == "Receivers":
        st.header("🤝 Receivers")
        df = get_df("SELECT * FROM receivers")
        st.dataframe(df)

    # ---------------- Food Listings ----------------
    elif choice == "Food Listings":
        st.header("🥗 Food Listings")
        df = get_df("SELECT * FROM food_listings")
        st.dataframe(df)

    # ---------------- Claims ----------------
    elif choice == "Claims":
        st.header("📦 Claims")
        df = get_df("SELECT * FROM claims")
        st.dataframe(df)

    # ---------------- SQL Insights ----------------
    elif choice == "SQL Insights":
        st.header("📈 SQL Insights & Analysis")

        # 1. Providers and Receivers per City
        st.subheader("1️⃣ Providers & Receivers per City")
        df = get_df("""
            SELECT City, 
                   (SELECT COUNT(*) FROM providers p WHERE p.City = c.City) AS Providers,
                   (SELECT COUNT(*) FROM receivers r WHERE r.City = c.City) AS Receivers
            FROM (SELECT City FROM providers UNION SELECT City FROM receivers) c
        """)
        st.dataframe(df)

        # 2. Provider Type contributing most food
        st.subheader("2️⃣ Provider Type contributing most food")
        df = get_df("""
            SELECT Provider_Type, COUNT(*) as Total_Listings
            FROM food_listings
            GROUP BY Provider_Type
            ORDER BY Total_Listings DESC
        """)
        st.bar_chart(df.set_index("Provider_Type"))

        # 3. Contact info of providers in specific city
        st.subheader("3️⃣ Provider Contact Info by City")
        city = st.selectbox("Select City", get_df("SELECT DISTINCT City FROM providers")["City"].tolist())
        df = get_df("SELECT Name, Contact FROM providers WHERE City = ?", (city,))
        st.dataframe(df)

        # 4. Receivers with most claims
        st.subheader("4️⃣ Top Receivers by Claims")
        df = get_df("""
            SELECT r.Name, COUNT(c.Claim_ID) as Total_Claims
            FROM receivers r
            JOIN claims c ON r.Receiver_ID = c.Receiver_ID
            GROUP BY r.Name
            ORDER BY Total_Claims DESC
        """)
        st.bar_chart(df.set_index("Name"))

        # 5. Total quantity of food
        st.subheader("5️⃣ Total Food Quantity Available")
        df = get_df("SELECT SUM(Quantity) as Total_Quantity FROM food_listings")
        st.metric("Total Quantity Available", df["Total_Quantity"].iloc[0])

        # 6. City with most food listings
        st.subheader("6️⃣ City with Most Food Listings")
        df = get_df("""
            SELECT Location, COUNT(*) as Listings
            FROM food_listings
            GROUP BY Location
            ORDER BY Listings DESC
        """)
        st.bar_chart(df.set_index("Location"))

        # 7. Most common food types
        st.subheader("7️⃣ Most Common Food Types")
        df = get_df("""
            SELECT Food_Type, COUNT(*) as Count
            FROM food_listings
            GROUP BY Food_Type
            ORDER BY Count DESC
        """)
        st.bar_chart(df.set_index("Food_Type"))

        # 8. Claims per food item
        st.subheader("8️⃣ Claims per Food Item")
        df = get_df("""
            SELECT f.Food_Name, COUNT(c.Claim_ID) as Claims
            FROM food_listings f
            LEFT JOIN claims c ON f.Food_ID = c.Food_ID
            GROUP BY f.Food_Name
            ORDER BY Claims DESC
        """)
        st.bar_chart(df.set_index("Food_Name"))

        # 9. Provider with highest successful claims
        st.subheader("9️⃣ Provider with Most Successful Claims")
        df = get_df("""
            SELECT p.Name, COUNT(c.Claim_ID) as Successful_Claims
            FROM providers p
            JOIN food_listings f ON p.Provider_ID = f.Provider_ID
            JOIN claims c ON f.Food_ID = c.Food_ID
            WHERE c.Status = 'Completed'
            GROUP BY p.Name
            ORDER BY Successful_Claims DESC
        """)
        st.bar_chart(df.set_index("Name"))

        # 10. Percentage of claim statuses
        st.subheader("🔟 Claim Status Distribution")
        df = get_df("""
            SELECT Status, COUNT(*) as Count
            FROM claims
            GROUP BY Status
        """)
        fig, ax = plt.subplots()
        ax.pie(df["Count"], labels=df["Status"], autopct="%1.1f%%")
        st.pyplot(fig)

        # 11. Avg quantity claimed per receiver
        st.subheader("1️⃣1️⃣ Average Quantity Claimed per Receiver")
        df = get_df("""
            SELECT r.Name, AVG(f.Quantity) as Avg_Claimed
            FROM receivers r
            JOIN claims c ON r.Receiver_ID = c.Receiver_ID
            JOIN food_listings f ON c.Food_ID = f.Food_ID
            GROUP BY r.Name
        """)
        st.bar_chart(df.set_index("Name"))

        # 12. Most claimed meal type
        st.subheader("1️⃣2️⃣ Most Claimed Meal Type")
        df = get_df("""
            SELECT f.Meal_Type, COUNT(c.Claim_ID) as Claims
            FROM food_listings f
            JOIN claims c ON f.Food_ID = c.Food_ID
            GROUP BY f.Meal_Type
            ORDER BY Claims DESC
        """)
        st.bar_chart(df.set_index("Meal_Type"))

        # 13. Total quantity donated per provider
        st.subheader("1️⃣3️⃣ Total Quantity Donated per Provider")
        df = get_df("""
            SELECT p.Name, SUM(f.Quantity) as Total_Quantity
            FROM providers p
            JOIN food_listings f ON p.Provider_ID = f.Provider_ID
            GROUP BY p.Name
            ORDER BY Total_Quantity DESC
        """)
        st.bar_chart(df.set_index("Name"))


if __name__ == "__main__":
    main()




















########### 2nd code start #############

# import streamlit as st
# import pandas as pd
# from db import get_db_connection, init_db

# st.set_page_config(page_title="Food Wastage Management", layout="wide")

# @st.cache_data
# def get_df(sql, params=()):
#     """Run SQL and return a pandas DataFrame."""
#     conn = get_db_connection()
#     cur = conn.execute(sql, params)
#     rows = cur.fetchall()
#     cols = [desc[0] for desc in cur.description]
#     conn.close()
#     return pd.DataFrame(rows, columns=cols)


# def main():
#     st.title("🍽️ Food Wastage Management System")

#     # Initialize DB once
#     init_db()

#     # Sidebar navigation
#     menu = ["Dashboard", "Providers", "Receivers", "Food Listings", "Claims"]
#     choice = st.sidebar.selectbox("Menu", menu)

#     # ---------------- Dashboard ----------------
#     if choice == "Dashboard":
#         st.header("📊 Dashboard")

#         total_providers = (
#             get_df("SELECT COUNT(*) c FROM providers")["c"].iloc[0]
#             if not get_df("SELECT COUNT(*) c FROM providers").empty else 0
#         )
#         total_receivers = (
#             get_df("SELECT COUNT(*) c FROM receivers")["c"].iloc[0]
#             if not get_df("SELECT COUNT(*) c FROM receivers").empty else 0
#         )
#         total_food_items = (
#             get_df("SELECT COUNT(*) c FROM food_listings")["c"].iloc[0]
#             if not get_df("SELECT COUNT(*) c FROM food_listings").empty else 0
#         )
#         total_claims = (
#             get_df("SELECT COUNT(*) c FROM claims")["c"].iloc[0]
#             if not get_df("SELECT COUNT(*) c FROM claims").empty else 0
#         )

#         col1, col2, col3, col4 = st.columns(4)
#         col1.metric("Providers", total_providers)
#         col2.metric("Receivers", total_receivers)
#         col3.metric("Food Items", total_food_items)
#         col4.metric("Claims", total_claims)

#     # ---------------- Providers ----------------
#     elif choice == "Providers":
#         st.header("🏢 Providers")
#         df = get_df("SELECT * FROM providers")
#         st.dataframe(df)

#     # ---------------- Receivers ----------------
#     elif choice == "Receivers":
#         st.header("🤝 Receivers")
#         df = get_df("SELECT * FROM receivers")
#         st.dataframe(df)

#     # ---------------- Food Listings ----------------
#     elif choice == "Food Listings":
#         st.header("🥗 Food Listings")
#         df = get_df("SELECT * FROM food_listings")
#         st.dataframe(df)

#     # ---------------- Claims ----------------
#     elif choice == "Claims":
#         st.header("📦 Claims")
#         df = get_df("SELECT * FROM claims")
#         st.dataframe(df)


# if __name__ == "__main__":
#     main()







#########       1st code start        ########


# import streamlit as st
# import pandas as pd
# import matplotlib.pyplot as plt
# from datetime import datetime, timedelta
# # from db import query, execute, init_db
# from db import  fetchall,execute, init_db

# st.set_page_config(page_title="Food Wastage Management", layout="wide")

# @st.cache_data
# def get_df(sql, params=()):
#     rows =fetchall(sql, params)
#     return pd.DataFrame(rows, columns=rows[0].keys() if rows else None)

# def ensure_schema():
#     init_db()

# def spacer(h=10):
#     st.write("""<div style='height:%dpx'></div>""" % h, unsafe_allow_html=True)

# def crud_providers():
#     st.subheader("Providers")
#     # Create
#     with st.expander("➕ Add Provider"):
#         with st.form("add_provider"):
#             cols = st.columns(3)
#             name = cols[0].text_input("Name")
#             ptype = cols[1].selectbox("Type", ["restaurant","retail","individual","caterer","ngo","other"])
#             city = cols[2].text_input("City")
#             cols2 = st.columns(3)
#             contact_name = cols2[0].text_input("Contact Name")
#             phone = cols2[1].text_input("Phone")
#             email = cols2[2].text_input("Email")
#             submitted = st.form_submit_button("Create")
#             if submitted and name:
#                 execute("INSERT INTO providers(name,type,city,contact_name,phone,email) VALUES (?,?,?,?,?,?)",
#                         (name, ptype, city, contact_name, phone, email))
#                 st.success("Provider created.")
#     # List
#     df = get_df("SELECT * FROM providers ORDER BY id DESC")
#     st.dataframe(df, use_container_width=True)

#     # Edit / Delete
#     if not df.empty:
#         st.markdown("**Edit or Delete**")
#         selected_id = st.selectbox("Select Provider ID", df["id"])
#         provider = df[df["id"] == selected_id].iloc[0]

#         with st.form("edit_provider"):
#             cols = st.columns(3)
#             name = cols[0].text_input("Name", provider["name"]) 
#             ptype = cols[1].selectbox("Type", ["restaurant","retail","individual","caterer","ngo","other"], index=["restaurant","retail","individual","caterer","ngo","other"].index(provider["type"]) if provider["type"] in ["restaurant","retail","individual","caterer","ngo","other"] else 0)
#             city = cols[2].text_input("City", provider["city"]) 
#             cols2 = st.columns(3)
#             contact_name = cols2[0].text_input("Contact Name", provider["contact_name"]) 
#             phone = cols2[1].text_input("Phone", provider["phone"]) 
#             email = cols2[2].text_input("Email", provider["email"]) 
#             colsb = st.columns(2)
#             update_btn = colsb[0].form_submit_button("Update")
#             delete_btn = colsb[1].form_submit_button("Delete", type="secondary" )

#         if update_btn:
#             execute("UPDATE providers SET name=?, type=?, city=?, contact_name=?, phone=?, email=? WHERE id=?",
#                     (name, ptype, city, contact_name, phone, email, int(selected_id)))
#             st.success("Provider updated.")
#         if delete_btn:
#             execute("DELETE FROM providers WHERE id=?", (int(selected_id),))
#             st.warning("Provider deleted.")

# def crud_receivers():
#     st.subheader("Receivers")
#     with st.expander("➕ Add Receiver"):
#         with st.form("add_receiver"):
#             cols = st.columns(3)
#             name = cols[0].text_input("Name")
#             rtype = cols[1].selectbox("Type", ["ngo","shelter","community","individual","other"])
#             city = cols[2].text_input("City")
#             cols2 = st.columns(3)
#             contact_name = cols2[0].text_input("Contact Name")
#             phone = cols2[1].text_input("Phone")
#             email = cols2[2].text_input("Email")
#             submitted = st.form_submit_button("Create")
#             if submitted and name:
#                 execute("INSERT INTO receivers(name,type,city,contact_name,phone,email) VALUES (?,?,?,?,?,?)",
#                         (name, rtype, city, contact_name, phone, email))
#                 st.success("Receiver created.")
#     df = get_df("SELECT * FROM receivers ORDER BY id DESC")
#     st.dataframe(df, use_container_width=True)
#     if not df.empty:
#         st.markdown("**Edit or Delete**")
#         selected_id = st.selectbox("Select Receiver ID", df["id"])
#         r = df[df["id"] == selected_id].iloc[0]

#         with st.form("edit_receiver"):
#             cols = st.columns(3)
#             name = cols[0].text_input("Name", r["name"]) 
#             rtype = cols[1].selectbox("Type", ["ngo","shelter","community","individual","other"], index=["ngo","shelter","community","individual","other"].index(r["type"]) if r["type"] in ["ngo","shelter","community","individual","other"] else 0)
#             city = cols[2].text_input("City", r["city"]) 
#             cols2 = st.columns(3)
#             contact_name = cols2[0].text_input("Contact Name", r["contact_name"]) 
#             phone = cols2[1].text_input("Phone", r["phone"]) 
#             email = cols2[2].text_input("Email", r["email"]) 
#             colsb = st.columns(2)
#             update_btn = colsb[0].form_submit_button("Update")
#             delete_btn = colsb[1].form_submit_button("Delete", type="secondary" )

#         if update_btn:
#             execute("UPDATE receivers SET name=?, type=?, city=?, contact_name=?, phone=?, email=? WHERE id=?",
#                     (name, rtype, city, contact_name, phone, email, int(selected_id)))
#             st.success("Receiver updated.")
#         if delete_btn:
#             execute("DELETE FROM receivers WHERE id=?", (int(selected_id),))
#             st.warning("Receiver deleted.")

# def crud_listings():
#     st.subheader("Food Listings")
#     # Create
#     prov = get_df("SELECT id, name FROM providers ORDER BY name")
#     with st.expander("➕ Add Listing"):
#         with st.form("add_listing"):
#             cols = st.columns(4)
#             provider_id = cols[0].selectbox("Provider", prov["name"].tolist() if not prov.empty else ["-- create provider first --"]) 
#             food_type = cols[1].text_input("Food Type", placeholder="Veg curry, bread, rice...")
#             meal_type = cols[2].selectbox("Meal Type", ["breakfast","lunch","dinner","snacks","other"]) 
#             quantity_kg = cols[3].number_input("Quantity (kg)", min_value=0.0, step=0.5) 
#             cols2 = st.columns(3)
#             listed_at = cols2[0].date_input("Listed At", value=pd.to_datetime("today").date())
#             expires_at = cols2[1].date_input("Expires At", value=pd.to_datetime("today").date() + pd.Timedelta(days=1))
#             city = cols2[2].text_input("City")
#             notes = st.text_area("Notes", placeholder="Any additional info...")
#             submitted = st.form_submit_button("Create")
#             if submitted:
#                 if prov.empty:
#                     st.error("Create a provider first.")
#                 else:
#                     # map provider name back to id
#                     pid = int(prov[prov["name"] == provider_id]["id"].iloc[0]) if not prov.empty else None
#                     execute("""
#                         INSERT INTO food_listings(provider_id, food_type, meal_type, quantity_kg, listed_at, expires_at, city, notes)
#                         VALUES (?,?,?,?,?,?,?,?)
#                     """, (pid, food_type, meal_type, float(quantity_kg), str(listed_at), str(expires_at), city, notes))
#                     st.success("Listing created.")
#     # Filter & view
#     colf = st.columns(4)
#     f_city = colf[0].text_input("Filter City")
#     f_food = colf[1].text_input("Filter Food Type")
#     f_meal = colf[2].selectbox("Meal", ["","breakfast","lunch","dinner","snacks","other"]) 
#     f_expiring = colf[3].selectbox("Expiring", ["","today","next_3_days","next_7_days"]) 
#     sql = """
#         SELECT l.id, p.name AS provider, l.food_type, l.meal_type, l.quantity_kg, l.city, l.listed_at, l.expires_at, l.notes
#         FROM food_listings l
#         JOIN providers p ON p.id = l.provider_id
#         WHERE 1=1
#     """
#     params = []
#     if f_city:
#         sql += " AND l.city LIKE ?"; params.append(f"%{f_city}%")
#     if f_food:
#         sql += " AND l.food_type LIKE ?"; params.append(f"%{f_food}%")
#     if f_meal:
#         sql += " AND l.meal_type = ?"; params.append(f_meal)
#     if f_expiring == "today":
#         sql += " AND date(l.expires_at) = date('now')"
#     elif f_expiring == "next_3_days":
#         sql += " AND date(l.expires_at) <= date('now','+3 day')"
#     elif f_expiring == "next_7_days":
#         sql += " AND date(l.expires_at) <= date('now','+7 day')"
#     df = get_df(sql + " ORDER BY l.expires_at ASC", tuple(params))
#     st.dataframe(df, use_container_width=True)

# def crud_claims():
#     st.subheader("Claims")
#     listings = get_df("SELECT id FROM food_listings ORDER BY id DESC")
#     receivers = get_df("SELECT id, name FROM receivers ORDER BY name")
#     with st.expander("➕ Add Claim"):
#         with st.form("add_claim"):
#             cols = st.columns(4)
#             listing_id = cols[0].selectbox("Listing ID", listings["id"].tolist() if not listings.empty else ["-- no listings --"]) 
#             receiver_name = cols[1].selectbox("Receiver", receivers["name"].tolist() if not receivers.empty else ["-- create receiver first --"]) 
#             status = cols[2].selectbox("Status", ["pending","approved","picked_up","cancelled"]) 
#             notes = cols[3].text_input("Notes", value="") 
#             submitted = st.form_submit_button("Create")
#             if submitted:
#                 if listings.empty or receivers.empty:
#                     st.error("Need at least one listing and receiver.")
#                 else:
#                     rid = int(receivers[receivers["name"] == receiver_name]["id"].iloc[0])
#                     execute("INSERT INTO claims(listing_id, receiver_id, status, notes) VALUES (?,?,?,?)",
#                             (int(listing_id), rid, status, notes))
#                     st.success("Claim created.")

#     # View & status update
#     df = get_df("""
#         SELECT c.id, c.listing_id, r.name AS receiver, c.status, c.claimed_at, c.fulfilled_at, c.notes
#         FROM claims c JOIN receivers r ON r.id = c.receiver_id
#         ORDER BY c.id DESC
#     """)
#     st.dataframe(df, use_container_width=True)

#     if not df.empty:
#         st.markdown("**Update Claim Status**")
#         claim_id = st.selectbox("Claim ID", df["id"])
#         new_status = st.selectbox("New Status", ["pending","approved","picked_up","cancelled"]) 
#         done = st.button("Update Status")
#         if done:
#             if new_status == "picked_up":
#                 execute("UPDATE claims SET status=?, fulfilled_at=datetime('now') WHERE id=?", (new_status, int(claim_id)))
#             else:
#                 execute("UPDATE claims SET status=? WHERE id=?", (new_status, int(claim_id)))
#             st.success("Claim updated.")

# def analytics():
#     st.subheader("Analytics")    
#     # 1) Claim status distribution
#     df = get_df("SELECT status, COUNT(*) as n FROM claims GROUP BY status ORDER BY n DESC")
#     if not df.empty:
#         st.markdown("**Claim Status Distribution**")
#         fig, ax = plt.subplots()
#         ax.bar(df["status"], df["n"])
#         ax.set_xlabel("Status"); ax.set_ylabel("Count")
#         st.pyplot(fig)

#     # 2) Top providers by total quantity listed
#     df2 = get_df("""
#         SELECT p.name AS provider, SUM(l.quantity_kg) as total_kg
#         FROM food_listings l JOIN providers p ON p.id = l.provider_id
#         GROUP BY p.name ORDER BY total_kg DESC LIMIT 10
#     """)
#     if not df2.empty:
#         st.markdown("**Top Providers by Quantity (kg)**")
#         fig2, ax2 = plt.subplots()
#         ax2.bar(df2["provider"], df2["total_kg"]) 
#         ax2.set_xticks(range(len(df2["provider"])))
#         ax2.set_xticklabels(df2["provider"], rotation=45, ha='right')
#         ax2.set_ylabel("kg")
#         st.pyplot(fig2)

#     # 3) Listings nearing expiry
#     df3 = get_df("""
#         SELECT id, food_type, city, expires_at
#         FROM food_listings
#         WHERE date(expires_at) <= date('now','+2 day')
#         ORDER BY date(expires_at)
#     """)
#     st.markdown("**Listings Nearing Expiry (≤ 2 days)**")
#     st.dataframe(df3, use_container_width=True)

#     # 4) Quantity distribution by meal type
#     df4 = get_df("SELECT meal_type, SUM(quantity_kg) as kg FROM food_listings GROUP BY meal_type ORDER BY kg DESC")
#     if not df4.empty:
#         st.markdown("**Quantity by Meal Type (kg)**")
#         fig4, ax4 = plt.subplots()
#         ax4.bar(df4["meal_type"], df4["kg"]) 
#         st.pyplot(fig4)

# def main():
#     ensure_schema()
#     st.title("🍛 Food Wastage Management — SQLite")    
#     tab = st.sidebar.radio("Sections", ["Dashboard","Providers","Receivers","Listings","Claims","Analytics"]) 

#     if tab == "Dashboard":
#         col = st.columns(3)
#         total_providers = get_df("SELECT COUNT(*) c FROM providers")["c"].iloc[0] if not get_df("SELECT COUNT(*) c FROM providers").empty else 0
#         total_receivers = get_df("SELECT COUNT(*) c FROM receivers")["c"].iloc[0] if not get_df("SELECT COUNT(*) c FROM receivers").empty else 0
#         total_listings = get_df("SELECT COUNT(*) c FROM food_listings")["c"].iloc[0] if not get_df("SELECT COUNT(*) c FROM food_listings").empty else 0
#         total_claims = get_df("SELECT COUNT(*) c FROM claims")["c"].iloc[0] if not get_df("SELECT COUNT(*) c FROM claims").empty else 0
#         col[0].metric("Providers", total_providers)
#         col[1].metric("Receivers", total_receivers)
#         col[2].metric("Listings", total_listings)
#         spacer(8)
#         st.info("Use the sidebar to manage data and view analytics.")
#     elif tab == "Providers":
#         crud_providers()
#     elif tab == "Receivers":
#         crud_receivers()
#     elif tab == "Listings":
#         crud_listings()
#     elif tab == "Claims":
#         crud_claims()
#     elif tab == "Analytics":
#         analytics()

# if __name__ == "__main__":
#     main()
# main.py


