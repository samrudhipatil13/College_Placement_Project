import streamlit as st
import os
import datetime
from utils.profile_utils import (
    get_student_by_user_id, create_or_update_profile,
    add_skill, get_student_skills, remove_skill
)
from utils.resume_utils import save_resume, get_resume

st.set_page_config(page_title="Student Profile", layout="centered")

# Guard: only logged-in students can see this page
if "logged_in_user" not in st.session_state or st.session_state.logged_in_user is None:
    st.warning("Please log in first from the main page.")
    st.stop()

user = st.session_state.logged_in_user
if user['role'] != 'student':
    st.warning("This page is for students only.")
    st.stop()

st.title("👤 My Profile")

existing = get_student_by_user_id(user['user_id'])
existing_resume = get_resume(existing['student_id']) if existing else None

# Pre-fill fields if profile already exists
def pre(field, default=""):
    return existing[field] if existing and existing.get(field) is not None else default

# NOTE: This page no longer uses st.form(). Skills need buttons that react
# immediately (Remove/Add), which don't work inside a form — so to place
# Skills in the middle of the page (between Additional Details and Resume),
# every field here is now a plain widget instead. The only visible change
# for you: typing in a field refreshes the page slightly on each keystroke,
# same as the Skills section already did before.

st.subheader("Personal Details")
name = st.text_input("Full Name", value=pre('name'))
phone = st.text_input("Phone Number", value=pre('phone'))
gender = st.selectbox("Gender", ["Male", "Female", "Other"],
                       index=["Male", "Female", "Other"].index(pre('gender', 'Male')))
dob = st.date_input(
    "Date of Birth",
    value=pre('dob', None),
    min_value=datetime.date(2000, 1, 1),
    max_value=datetime.date.today(),
    format="DD/MM/YYYY",
)
address = st.text_area("Address", value=pre('address'))

st.subheader("Academic Details")

BRANCH_DEPARTMENTS = {
    "Computer": ["CSE", "Data Science"],
    "Civil": ["Civil Engineering"],
    "Mechanical": ["Mechanical Engineering"],
    "Electrical": ["Electrical Engineering"],
    "Electronics & Telecommunication": ["E&TC Engineering"],
}

branch = st.selectbox(
    "Branch",
    list(BRANCH_DEPARTMENTS.keys()),
    index=list(BRANCH_DEPARTMENTS.keys()).index(pre('branch', 'Computer'))
    if pre('branch', 'Computer') in BRANCH_DEPARTMENTS else 0,
)

dept_options = BRANCH_DEPARTMENTS[branch]
current_dept = pre('department', dept_options[0])
department = st.selectbox(
    "Department",
    dept_options,
    index=dept_options.index(current_dept) if current_dept in dept_options else 0,
)

cgpa = st.number_input("CGPA", min_value=0.0, max_value=10.0, step=0.01, value=float(pre('cgpa', 0.0)))
ssc = st.number_input("SSC %", min_value=0.0, max_value=100.0, step=0.01, value=float(pre('ssc_percentage', 0.0)))
hsc = st.number_input("HSC %", min_value=0.0, max_value=100.0, step=0.01, value=float(pre('hsc_percentage', 0.0)))
diploma = st.number_input("Diploma % (if applicable)", min_value=0.0, max_value=100.0, step=0.01, value=float(pre('diploma_percentage', 0.0)))
backlogs = st.number_input("Number of Backlogs", min_value=0, step=1, value=int(pre('backlogs', 0)))
grad_year = st.number_input("Graduation Year", min_value=2020, max_value=2035, step=1, value=int(pre('graduation_year', 2026)))

st.subheader("Additional Details")
certifications = st.text_area("Certifications", value=pre('certifications'))
projects = st.text_area("Projects", value=pre('projects'))
internships = st.text_area("Internships", value=pre('internships'))

# ---------------- SKILLS ----------------
st.subheader("Skills")
if existing:
    student_id = existing['student_id']
    current_skills = get_student_skills(student_id)

    if current_skills:
        for skill in current_skills:
            col1, col2 = st.columns([4, 1])
            col1.write(f"• {skill}")
            if col2.button("Remove", key=f"remove_{skill}"):
                remove_skill(student_id, skill)
                st.rerun()
    else:
        st.caption("No skills added yet.")

    new_skill = st.text_input("Add a new skill", key="new_skill_input")
    if st.button("Add Skill"):
        if new_skill.strip():
            add_skill(student_id, new_skill.strip())
            st.rerun()
        else:
            st.warning("Enter a skill name first.")
else:
    st.caption("Save your profile below first, then you can add skills.")

# ---------------- RESUME ----------------
st.subheader("Resume")
if existing_resume:
    st.caption(f"📄 Current resume on file: `{existing_resume['file_path'].split(os.sep)[-1]}` "
                f"(uploaded {existing_resume['uploaded_at']}). Upload a new file below only if you want to replace it.")
else:
    st.caption("Required — please upload your resume before you can save your profile.")
uploaded_file = st.file_uploader("Upload Resume (PDF only, max 5 MB)", type=["pdf"])

# ---------------- SAVE PROFILE — always the very last thing on the page ----------------
st.divider()

resume_ready = (uploaded_file is not None) or (existing_resume is not None)

if not resume_ready:
    st.info("⬆️ Upload your resume above to unlock the Save Profile button.")
else:
    if st.button("💾 Save Profile", type="primary"):
        if not name:
            st.error("Name is required.")
        elif dob is None:
            st.error("Please select your Date of Birth.")
        else:
            data = {
                'name': name, 'phone': phone, 'gender': gender, 'dob': dob, 'address': address,
                'branch': branch, 'department': department, 'cgpa': cgpa, 'ssc_percentage': ssc,
                'hsc_percentage': hsc, 'diploma_percentage': diploma, 'backlogs': backlogs,
                'graduation_year': grad_year, 'certifications': certifications,
                'projects': projects, 'internships': internships
            }
            success, message = create_or_update_profile(user['user_id'], data)
            if success:
                if uploaded_file is not None:
                    saved_student = get_student_by_user_id(user['user_id'])
                    save_resume(saved_student['student_id'], uploaded_file)
                st.success(message)
                st.rerun()
            else:
                st.error(message)