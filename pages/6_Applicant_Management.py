import streamlit as st
from utils.drive_utils import get_all_drives
from utils.applicant_utils import get_applicants_for_drive, update_application_status
from utils.export_utils import export_applicants_to_excel

st.set_page_config(page_title="Applicant Management", layout="wide")

if "logged_in_user" not in st.session_state or st.session_state.logged_in_user is None:
    st.warning("Please log in first from the main page.")
    st.stop()

user = st.session_state.logged_in_user
if user['role'] != 'admin':
    st.warning("This page is for TPO/Admin only.")
    st.stop()

st.title("👥 Applicant Management")

drives = get_all_drives()

if not drives:
    st.caption("No drives available yet.")
    st.stop()

drive_options = {f"{d['company_name']} — {d['job_role']}": d['drive_id'] for d in drives}
selected_label = st.selectbox("Select a Placement Drive", list(drive_options.keys()))
selected_drive_id = drive_options[selected_label]

applicants = get_applicants_for_drive(selected_drive_id)

if applicants:
    if st.button("📥 Download Applicants Excel"):
        file_path, message = export_applicants_to_excel(selected_drive_id)
        if file_path:
            with open(file_path, "rb") as f:
                st.download_button(
                    label="Click to Download",
                    data=f,
                    file_name=file_path.split("/")[-1],
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            st.success(message)
        else:
            st.warning(message)

if not applicants:
    st.caption("No applicants for this drive yet.")
else:
    st.write(f"**Total Applicants:** {len(applicants)}")

    for app in applicants:
        with st.expander(f"{app['name']} — {app['branch']} — CGPA: {app['cgpa']}"):
            st.write(f"**Email:** {app['email']}")
            st.write(f"**Phone:** {app['phone']}")
            st.write(f"**SSC:** {app['ssc_percentage']}% | **HSC:** {app['hsc_percentage']}% | **Backlogs:** {app['backlogs']}")
            st.write(f"**Application Date:** {app['application_date']}")

            new_status = st.selectbox(
                "Status",
                ["applied", "shortlisted", "rejected", "selected"],
                index=["applied", "shortlisted", "rejected", "selected"].index(app['status']),
                key=f"status_{app['application_id']}"
            )
            if st.button("Update Status", key=f"btn_{app['application_id']}"):
                update_application_status(app['application_id'], new_status)
                st.success("Status updated!")
                st.rerun()