from database.db_connection import get_connection

def add_drive(company_id, job_role, job_description, package_ctc, drive_date,
              venue, registration_deadline, vacancies, min_cgpa, min_ssc, min_hsc,
              max_backlogs, required_gender, branches):
    """
    Creates a new placement drive along with its eligible branches.
    'branches' is a list of branch name strings, e.g. ["Computer", "IT"].
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO drives
            (company_id, job_role, job_description, package_ctc, drive_date,
             venue, registration_deadline, vacancies, min_cgpa, min_ssc, min_hsc,
             max_backlogs, required_gender, drive_status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'upcoming')
    """
    cursor.execute(query, (company_id, job_role, job_description, package_ctc, drive_date,
                            venue, registration_deadline, vacancies, min_cgpa, min_ssc, min_hsc,
                            max_backlogs, required_gender))
    conn.commit()

    drive_id = cursor.lastrowid

    for branch in branches:
        cursor.execute(
            "INSERT INTO drive_branches (drive_id, branch) VALUES (%s, %s)",
            (drive_id, branch.strip())
        )
    conn.commit()

    cursor.close()
    conn.close()
    return drive_id


def get_all_drives():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT d.*, c.company_name
        FROM drives d
        JOIN companies c ON d.company_id = c.company_id
        ORDER BY d.drive_id DESC
    """
    cursor.execute(query)
    drives = cursor.fetchall()

    cursor.close()
    conn.close()
    return drives


def get_drive_branches(drive_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT branch FROM drive_branches WHERE drive_id = %s", (drive_id,))
    branches = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return branches


def update_drive_status(drive_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE drives SET drive_status = %s WHERE drive_id = %s", (new_status, drive_id))
    conn.commit()

    cursor.close()
    conn.close()


def update_drive(drive_id, job_role, job_description, package_ctc, drive_date,
                  venue, registration_deadline, vacancies, min_cgpa, min_ssc, min_hsc,
                  max_backlogs, required_gender, branches):
    """
    Updates an existing drive's details and replaces its eligible branches.
    """
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        UPDATE drives SET
            job_role=%s, job_description=%s, package_ctc=%s, drive_date=%s,
            venue=%s, registration_deadline=%s, vacancies=%s, min_cgpa=%s,
            min_ssc=%s, min_hsc=%s, max_backlogs=%s, required_gender=%s
        WHERE drive_id=%s
    """
    cursor.execute(query, (job_role, job_description, package_ctc, drive_date,
                            venue, registration_deadline, vacancies, min_cgpa,
                            min_ssc, min_hsc, max_backlogs, required_gender, drive_id))
    conn.commit()

    cursor.execute("DELETE FROM drive_branches WHERE drive_id = %s", (drive_id,))
    for branch in branches:
        cursor.execute(
            "INSERT INTO drive_branches (drive_id, branch) VALUES (%s, %s)",
            (drive_id, branch.strip())
        )
    conn.commit()

    cursor.close()
    conn.close()


def delete_drive(drive_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM drives WHERE drive_id = %s", (drive_id,))
    conn.commit()

    cursor.close()
    conn.close()