from database.db_connection import get_connection
from datetime import date

def apply_to_drive(student_id, drive_id):
    """
    Applies a student to a drive, with protection against:
    - duplicate applications
    - applying after the registration deadline
    Returns (True, message) or (False, message).
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Check deadline
    cursor.execute("SELECT registration_deadline FROM drives WHERE drive_id = %s", (drive_id,))
    drive = cursor.fetchone()
    if not drive:
        cursor.close()
        conn.close()
        return False, "Drive not found."

    if drive['registration_deadline'] and drive['registration_deadline'] < date.today():
        cursor.close()
        conn.close()
        return False, "Registration deadline has passed for this drive."

    # Check duplicate
    cursor.execute(
        "SELECT * FROM applications WHERE student_id = %s AND drive_id = %s",
        (student_id, drive_id)
    )
    existing = cursor.fetchone()
    if existing:
        cursor.close()
        conn.close()
        return False, "You have already applied to this drive."

    # Insert application
    cursor.execute(
        "INSERT INTO applications (student_id, drive_id) VALUES (%s, %s)",
        (student_id, drive_id)
    )
    conn.commit()

    cursor.close()
    conn.close()
    return True, "Application submitted successfully!"


def get_my_applications(student_id):
    """Returns all applications for a student, with company/drive info joined in."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT a.application_id, a.application_date, a.status,
               c.company_name, d.job_role, d.package_ctc, d.drive_id
        FROM applications a
        JOIN drives d ON a.drive_id = d.drive_id
        JOIN companies c ON d.company_id = c.company_id
        WHERE a.student_id = %s
        ORDER BY a.application_date DESC
    """
    cursor.execute(query, (student_id,))
    applications = cursor.fetchall()

    cursor.close()
    conn.close()
    return applications


def has_applied(student_id, drive_id):
    """Quick check used to disable the Apply button if already applied."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM applications WHERE student_id = %s AND drive_id = %s",
        (student_id, drive_id)
    )
    result = cursor.fetchone()

    cursor.close()
    conn.close()
    return result is not None