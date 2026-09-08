import os
from database.db_connection import get_connection

RESUME_FOLDER = "resumes"

def save_resume(student_id, uploaded_file):
    """
    Saves an uploaded resume file to disk and records it in the database.
    Overwrites any previous resume record for this student (keeps only the latest).
    """
    if not os.path.exists(RESUME_FOLDER):
        os.makedirs(RESUME_FOLDER)

    # Build a unique filename: student_<id>_<original filename>
    filename = f"student_{student_id}_{uploaded_file.name}"
    file_path = os.path.join(RESUME_FOLDER, filename)

    # Save file to disk
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    conn = get_connection()
    cursor = conn.cursor()

    # Remove old resume record(s) for this student (we only keep the latest, per blueprint's "replace resume" requirement)
    cursor.execute("DELETE FROM resumes WHERE student_id = %s", (student_id,))

    # Insert new resume record
    cursor.execute(
        "INSERT INTO resumes (student_id, file_path) VALUES (%s, %s)",
        (student_id, file_path)
    )
    conn.commit()
    cursor.close()
    conn.close()

    return file_path


def get_resume(student_id):
    """Returns the resume file_path for a student, or None if not uploaded yet."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM resumes WHERE student_id = %s", (student_id,))
    resume = cursor.fetchone()

    cursor.close()
    conn.close()
    return resume