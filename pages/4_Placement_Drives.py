import streamlit as st
from utils.drive_utils import add_drive, get_all_drives, get_drive_branches, update_drive_status, update_drive, delete_drive
from utils.company_utils import get_all_companies

st.set_page_config(page_title="Placement Drives", layout="centered")

# Guard: only admins
if "logged_in_user" not in st.session_state or st.session_state.logged_in_user is None:
    st.warning("Please log in first from the main page.")
    st.stop()

user = st.session_state.logged_in_user
if user['role'] != 'admin':
    st.warning("This page is for TPO/Admin only.")
    st.stop()

st.title("📋 Placement Drive Management")

companies = get_all_companies()

if not companies:
    st.warning("Please add at least one company first (Company Management page) before creating a drive.")
    st.stop()

tab1, tab2 = st.tabs(["Create New Drive", "View / Manage Drives"])

# ---------------- CREATE DRIVE ----------------
with tab1:
    st.subheader("Create a New Placement Drive")

    company_names = {c['company_name']: c['company_id'] for c in companies}

    with st.form("add_drive_form", clear_on_submit=True):
        selected_company = st.selectbox("Company", list(company_names.keys()))
        job_role = st.text_input("Job Role")
        job_description = st.text_area("Job Description")
        package_ctc = st.number_input("Package / CTC (in LPA)", min_value=0.0, step=0.1)
        drive_date = st.date_input("Drive Date")
        venue = st.text_input("Venue")
        registration_deadline = st.date_input("Registration Deadline")
        vacancies = st.number_input("Number of Vacancies", min_value=1, step=1, value=1)

        st.markdown("**Eligibility Criteria**")
        min_cgpa = st.number_input("Minimum CGPA", min_value=0.0, max_value=10.0, step=0.1, value=6.0)
        min_ssc = st.number_input("Minimum SSC %", min_value=0.0, max_value=100.0, step=1.0, value=50.0)
        min_hsc = st.number_input("Minimum HSC %", min_value=0.0, max_value=100.0, step=1.0, value=50.0)
        max_backlogs = st.number_input("Maximum Allowed Backlogs", min_value=0, step=1, value=0)
        required_gender = st.selectbox("Required Gender", ["Any", "Male", "Female"])
        branches_input = st.text_input("Eligible Branches (comma-separated, e.g. Computer, IT, ENTC)")

        submitted = st.form_submit_button("Create Drive")
        if submitted:
            if not job_role or not branches_input:
                st.error("Job role and eligible branches are required.")
            else:
                branches_list = [b.strip() for b in branches_input.split(",") if b.strip()]
                company_id = company_names[selected_company]
                add_drive(company_id, job_role, job_description, package_ctc, drive_date,
                          venue, registration_deadline, vacancies, min_cgpa, min_ssc, min_hsc,
                          max_backlogs, required_gender, branches_list)
                st.success(f"Drive for '{job_role}' at {selected_company} created!")
                st.rerun()

# ---------------- VIEW / MANAGE DRIVES ----------------
with tab2:
    st.subheader("All Placement Drives")
    drives = get_all_drives()

    if not drives:
        st.caption("No drives created yet.")
    else:
        for drive in drives:
            branches = get_drive_branches(drive['drive_id'])
            with st.expander(f"{drive['company_name']} — {drive['job_role']} ({drive['drive_status']})"):
                st.write(f"**Package:** {drive['package_ctc']} LPA")
                st.write(f"**Drive Date:** {drive['drive_date']}")
                st.write(f"**Venue:** {drive['venue']}")
                st.write(f"**Registration Deadline:** {drive['registration_deadline']}")
                st.write(f"**Vacancies:** {drive['vacancies']}")
                st.write(f"**Min CGPA:** {drive['min_cgpa']} | **Min SSC:** {drive['min_ssc']}% | **Min HSC:** {drive['min_hsc']}%")
                st.write(f"**Max Backlogs:** {drive['max_backlogs']} | **Required Gender:** {drive['required_gender']}")
                st.write(f"**Eligible Branches:** {', '.join(branches)}")

                # ---------------- EDIT DRIVE ----------------
                edit_key = f"editing_drive_{drive['drive_id']}"
                if st.button("Edit Drive", key=f"edit_btn_{drive['drive_id']}"):
                    st.session_state[edit_key] = True

                if st.session_state.get(edit_key, False):
                    with st.form(f"edit_drive_form_{drive['drive_id']}"):
                        new_job_role = st.text_input("Job Role", value=drive['job_role'])
                        new_description = st.text_area("Job Description", value=drive['job_description'] or "")
                        new_package = st.number_input("Package (LPA)", min_value=0.0, step=0.1, value=float(drive['package_ctc'] or 0))
                        new_date = st.date_input("Drive Date", value=drive['drive_date'])
                        new_venue = st.text_input("Venue", value=drive['venue'] or "")
                        new_deadline = st.date_input("Registration Deadline", value=drive['registration_deadline'])
                        new_vacancies = st.number_input("Vacancies", min_value=1, step=1, value=int(drive['vacancies'] or 1))
                        new_min_cgpa = st.number_input("Min CGPA", min_value=0.0, max_value=10.0, step=0.1, value=float(drive['min_cgpa'] or 0))
                        new_min_ssc = st.number_input("Min SSC %", min_value=0.0, max_value=100.0, step=1.0, value=float(drive['min_ssc'] or 0))
                        new_min_hsc = st.number_input("Min HSC %", min_value=0.0, max_value=100.0, step=1.0, value=float(drive['min_hsc'] or 0))
                        new_max_backlogs = st.number_input("Max Backlogs", min_value=0, step=1, value=int(drive['max_backlogs'] or 0))
                        new_gender = st.selectbox("Required Gender", ["Any", "Male", "Female"],
                                                    index=["Any", "Male", "Female"].index(drive['required_gender']))
                        new_branches_input = st.text_input("Eligible Branches (comma-separated)",
                                                            value=", ".join(branches))

                        save_edit = st.form_submit_button("Save Drive Changes")
                        if save_edit:
                            new_branches_list = [b.strip() for b in new_branches_input.split(",") if b.strip()]
                            update_drive(drive['drive_id'], new_job_role, new_description, new_package,
                                        new_date, new_venue, new_deadline, new_vacancies, new_min_cgpa,
                                        new_min_ssc, new_min_hsc, new_max_backlogs, new_gender, new_branches_list)
                            st.session_state[edit_key] = False
                            st.success("Drive updated!")
                            st.rerun()

                # ---------------- STATUS UPDATE ----------------
                new_status = st.selectbox(
                    "Status", ["upcoming", "active", "closed"],
                    index=["upcoming", "active", "closed"].index(drive['drive_status']),
                    key=f"status_{drive['drive_id']}"
                )
                if st.button("Update Status", key=f"update_{drive['drive_id']}"):
                    update_drive_status(drive['drive_id'], new_status)
                    st.success("Status updated!")
                    st.rerun()

                if st.button("Delete Drive", key=f"delete_{drive['drive_id']}"):
                    delete_drive(drive['drive_id'])
                    st.success("Drive deleted.")
                    st.rerun()