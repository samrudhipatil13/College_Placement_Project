from database.db_connection import get_connection

def get_student_by_user_id(user_id):
    """Fetch a student's profile row using their user_id. Returns None if no profile exists yet."""
    conn = get_connection()
    if conn is None:
        return None

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE user_id = %s", (user_id,))
    student = cursor.fetchone()

    cursor.close()
    conn.close()
    return student


def create_or_update_profile(user_id, data):
    """
    Creates a student profile if it doesn't exist, or updates it if it does.
    'data' is a dictionary with keys matching the students table columns.
    """
    conn = get_connection()
    if conn is None:
        return False, "Database connection failed."

    cursor = conn.cursor()

    existing = get_student_by_user_id(user_id)

    if existing:
        # UPDATE existing profile
        query = """
            UPDATE students SET
                name=%s, phone=%s, gender=%s, dob=%s, address=%s,
                branch=%s, department=%s, cgpa=%s, ssc_percentage=%s,
                hsc_percentage=%s, diploma_percentage=%s, backlogs=%s,
                graduation_year=%s, certifications=%s, projects=%s, internships=%s
            WHERE user_id=%s
        """
        values = (
            data['name'], data['phone'], data['gender'], data['dob'], data['address'],
            data['branch'], data['department'], data['cgpa'], data['ssc_percentage'],
            data['hsc_percentage'], data['diploma_percentage'], data['backlogs'],
            data['graduation_year'], data['certifications'], data['projects'], data['internships'],
            user_id
        )
    else:
        # INSERT new profile
        query = """
            INSERT INTO students
                (user_id, name, phone, gender, dob, address, branch, department,
                 cgpa, ssc_percentage, hsc_percentage, diploma_percentage, backlogs,
                 graduation_year, certifications, projects, internships)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            user_id, data['name'], data['phone'], data['gender'], data['dob'], data['address'],
            data['branch'], data['department'], data['cgpa'], data['ssc_percentage'],
            data['hsc_percentage'], data['diploma_percentage'], data['backlogs'],
            data['graduation_year'], data['certifications'], data['projects'], data['internships']
        )

    cursor.execute(query, values)
    conn.commit()
    cursor.close()
    conn.close()
    return True, "Profile saved successfully!"


def add_skill(student_id, skill_name):
    """Adds a skill to the skills master table (if new) and links it to the student."""
    conn = get_connection()
    cursor = conn.cursor()

    # Insert skill into master list if it doesn't already exist
    cursor.execute("INSERT IGNORE INTO skills (skill_name) VALUES (%s)", (skill_name,))
    conn.commit()

    # Get the skill_id (whether it was just inserted or already existed)
    cursor.execute("SELECT skill_id FROM skills WHERE skill_name = %s", (skill_name,))
    skill_id = cursor.fetchone()[0]

    # Link student to skill (ignore if already linked)
    cursor.execute("INSERT IGNORE INTO student_skills (student_id, skill_id) VALUES (%s, %s)", (student_id, skill_id))
    conn.commit()

    cursor.close()
    conn.close()


def get_student_skills(student_id):
    """Returns a list of skill names for a given student."""
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT s.skill_name FROM skills s
        JOIN student_skills ss ON s.skill_id = ss.skill_id
        WHERE ss.student_id = %s
    """
    cursor.execute(query, (student_id,))
    skills = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return skills


def remove_skill(student_id, skill_name):
    """Removes a skill link from a student."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT skill_id FROM skills WHERE skill_name = %s", (skill_name,))
    result = cursor.fetchone()
    if result:
        skill_id = result[0]
        cursor.execute("DELETE FROM student_skills WHERE student_id=%s AND skill_id=%s", (student_id, skill_id))
        conn.commit()

    cursor.close()
    conn.close()