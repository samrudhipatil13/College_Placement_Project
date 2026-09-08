from database.db_connection import get_connection

def get_applicants_for_drive(drive_id):
    """Returns all applicants for a specific drive, with full student + application info."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT a.application_id, a.application_date, a.status,
               s.student_id, s.name, s.branch, s.cgpa, s.ssc_percentage,
               s.hsc_percentage, s.backlogs,
               u.email, s.phone
        FROM applications a
        JOIN students s ON a.student_id = s.student_id
        JOIN users u ON s.user_id = u.user_id
        WHERE a.drive_id = %s
        ORDER BY a.application_date ASC
    """
    cursor.execute(query, (drive_id,))
    applicants = cursor.fetchall()

    cursor.close()
    conn.close()
    return applicants


def update_application_status(application_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE applications SET status = %s WHERE application_id = %s",
        (new_status, application_id)
    )
    conn.commit()

    cursor.close()
    conn.close()