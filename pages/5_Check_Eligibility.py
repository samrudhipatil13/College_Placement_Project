import streamlit as st
from utils.profile_utils import get_student_by_user_id
from utils.drive_utils import get_all_drives, get_drive_branches
from utils.eligibility_utils import check_eligibility
from utils.application_utils import apply_to_drive, get_my_applications, has_applied

st.set_page_config(page_title="Drives & Applications", layout="centered")

if "logged_in_user" not in st.session_state or st.session_state.logged_in_user is None:
    st.warning("Please log in first from the main page.")
    st.stop()

user = st.session_state.logged_in_user
if user['role'] != 'student':
    st.warning("This page is for students only.")
    st.stop()

st.title("✅ Placement Drives & Applications")

student = get_student_by_user_id(user['user_id'])

if not student:
    st.warning("Please complete your profile first (Student Profile page) before checking eligibility.")
    st.stop()

tab1, tab2 = st.tabs(["Available Drives", "My Applications"])

# ---------------- AVAILABLE DRIVES ----------------
with tab1:
    drives = get_all_drives()

    if not drives:
        st.caption("No placement drives available yet.")
    else:
        for drive in drives:
            branches = get_drive_branches(drive['drive_id'])
            is_eligible, reasons = check_eligibility(student, drive, branches)
            already_applied = has_applied(student['student_id'], drive['drive_id'])

            with st.expander(f"{drive['company_name']} — {drive['job_role']} ({drive['drive_status']})"):
                st.write(f"**Package:** {drive['package_ctc']} LPA")
                st.write(f"**Drive Date:** {drive['drive_date']}")
                st.write(f"**Registration Deadline:** {drive['registration_deadline']}")
                st.write(f"**Eligible Branches:** {', '.join(branches)}")
                st.write(f"**Min CGPA:** {drive['min_cgpa']} | **Min SSC:** {drive['min_ssc']}% | **Min HSC:** {drive['min_hsc']}%")

                st.divider()

                if is_eligible:
                    st.success("✅ Eligible")
                    if already_applied:
                        st.info("You have already applied to this drive.")
                    else:
                        if st.button("Apply Now", key=f"apply_{drive['drive_id']}"):
                            success, message = apply_to_drive(student['student_id'], drive['drive_id'])
                            if success:
                                st.success(message)
                                st.rerun()
                            else:
                                st.error(message)
                else:
                    st.error("❌ Not Eligible")
                    for reason in reasons:
                        st.write(f"- {reason}")

# ---------------- MY APPLICATIONS ----------------
with tab2:
    st.subheader("My Applications")
    applications = get_my_applications(student['student_id'])

    if not applications:
        st.caption("You haven't applied to any drives yet.")
    else:
        for app in applications:
            st.write(f"**{app['company_name']}** — {app['job_role']}")
            st.caption(
                f"Package: {app['package_ctc']} LPA | Applied on: {app['application_date']} | "
                f"Status: **{app['status'].capitalize()}**"
            )
            st.divider()