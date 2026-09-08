import streamlit as st
from database.db_connection import get_connection

st.set_page_config(page_title="TPO Dashboard", layout="centered")

# Guard: only logged-in admins can see this page
if "logged_in_user" not in st.session_state or st.session_state.logged_in_user is None:
    st.warning("Please log in first from the main page.")
    st.stop()

user = st.session_state.logged_in_user
if user['role'] != 'admin':
    st.warning("This page is for TPO/Admin only.")
    st.stop()

st.title("📊 TPO Dashboard")

conn = get_connection()
cursor = conn.cursor()

def count(table):
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    return cursor.fetchone()[0]

total_students = count("students")
total_companies = count("companies")
total_drives = count("drives")
total_applications = count("applications")

cursor.execute("SELECT COUNT(*) FROM drives WHERE drive_status = 'active'")
active_drives = cursor.fetchone()[0]

cursor.close()
conn.close()

col1, col2, col3 = st.columns(3)
col1.metric("Total Students", total_students)
col2.metric("Total Companies", total_companies)
col3.metric("Total Drives", total_drives)

col4, col5 = st.columns(2)
col4.metric("Total Applications", total_applications)
col5.metric("Active Drives", active_drives)

st.divider()
st.caption("Recent applications, company management, and drive management coming in upcoming modules.")