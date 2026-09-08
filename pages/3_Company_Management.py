import streamlit as st
from utils.company_utils import (
    add_company, get_all_companies, get_company_by_id,
    update_company, delete_company
)

st.set_page_config(page_title="Company Management", layout="centered")

# Guard: only admins
if "logged_in_user" not in st.session_state or st.session_state.logged_in_user is None:
    st.warning("Please log in first from the main page.")
    st.stop()

user = st.session_state.logged_in_user
if user['role'] != 'admin':
    st.warning("This page is for TPO/Admin only.")
    st.stop()

st.title("🏢 Company Management")

tab1, tab2 = st.tabs(["Add New Company", "View / Edit Companies"])

# ---------------- ADD COMPANY ----------------
with tab1:
    st.subheader("Add a New Company")
    with st.form("add_company_form", clear_on_submit=True):
        name = st.text_input("Company Name")
        industry = st.text_input("Industry")
        website = st.text_input("Website")
        location = st.text_input("Location")
        hr_contact = st.text_input("HR / Contact Info")
        description = st.text_area("Description")

        submitted = st.form_submit_button("Add Company")
        if submitted:
            if not name:
                st.error("Company name is required.")
            else:
                add_company(name, industry, website, location, hr_contact, description)
                st.success(f"Company '{name}' added successfully!")
                st.rerun()

# ---------------- VIEW / EDIT COMPANIES ----------------
with tab2:
    st.subheader("All Companies")
    companies = get_all_companies()

    if not companies:
        st.caption("No companies added yet.")
    else:
        for company in companies:
            with st.expander(f"{company['company_name']} ({company['industry'] or 'N/A'})"):
                st.write(f"**Location:** {company['location'] or 'N/A'}")
                st.write(f"**Website:** {company['website'] or 'N/A'}")
                st.write(f"**HR Contact:** {company['hr_contact'] or 'N/A'}")
                st.write(f"**Description:** {company['description'] or 'N/A'}")

                edit_key = f"edit_{company['company_id']}"
                if st.button("Edit", key=edit_key):
                    st.session_state[f"editing_{company['company_id']}"] = True

                if st.session_state.get(f"editing_{company['company_id']}", False):
                    with st.form(f"edit_form_{company['company_id']}"):
                        new_name = st.text_input("Company Name", value=company['company_name'])
                        new_industry = st.text_input("Industry", value=company['industry'] or "")
                        new_website = st.text_input("Website", value=company['website'] or "")
                        new_location = st.text_input("Location", value=company['location'] or "")
                        new_hr = st.text_input("HR Contact", value=company['hr_contact'] or "")
                        new_desc = st.text_area("Description", value=company['description'] or "")

                        save_edit = st.form_submit_button("Save Changes")
                        if save_edit:
                            update_company(company['company_id'], new_name, new_industry,
                                            new_website, new_location, new_hr, new_desc)
                            st.session_state[f"editing_{company['company_id']}"] = False
                            st.success("Company updated!")
                            st.rerun()

                if st.button("Delete", key=f"delete_{company['company_id']}"):
                    delete_company(company['company_id'])
                    st.success("Company deleted.")
                    st.rerun()