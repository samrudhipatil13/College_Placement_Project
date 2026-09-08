import pandas as pd
from utils.applicant_utils import get_applicants_for_drive
from utils.drive_utils import get_all_drives

def export_applicants_to_excel(drive_id):
    """
    Generates an Excel file of applicants for a given drive.
    Returns the file path.
    """
    applicants = get_applicants_for_drive(drive_id)

    # Find company + job role for the filename
    drives = get_all_drives()
    drive_info = next((d for d in drives if d['drive_id'] == drive_id), None)

    if not applicants:
        return None, "No applicants to export."

    # Build a clean DataFrame with readable column names
    data = []
    for a in applicants:
        data.append({
            "Student Name": a['name'],
            "Email": a['email'],
            "Phone": a['phone'],
            "Branch": a['branch'],
            "CGPA": a['cgpa'],
            "SSC %": a['ssc_percentage'],
            "HSC %": a['hsc_percentage'],
            "Backlogs": a['backlogs'],
            "Application Status": a['status'],
            "Application Date": a['application_date'],
        })

    df = pd.DataFrame(data)

    # Build filename: CompanyName_JobRole_Applicants.xlsx
    company = drive_info['company_name'].replace(" ", "_")
    role = drive_info['job_role'].replace(" ", "_")
    filename = f"{company}_{role}_Applicants.xlsx"
    file_path = f"exports/{filename}"

    import os
    if not os.path.exists("exports"):
        os.makedirs("exports")

    df.to_excel(file_path, index=False, engine='openpyxl')

    return file_path, "Export successful!"