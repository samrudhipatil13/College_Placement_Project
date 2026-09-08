from database.db_connection import get_connection

def add_company(name, industry, website, location, hr_contact, description):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        INSERT INTO companies (company_name, industry, website, location, hr_contact, description)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, (name, industry, website, location, hr_contact, description))
    conn.commit()

    cursor.close()
    conn.close()


def get_all_companies():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM companies ORDER BY company_id DESC")
    companies = cursor.fetchall()

    cursor.close()
    conn.close()
    return companies


def get_company_by_id(company_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM companies WHERE company_id = %s", (company_id,))
    company = cursor.fetchone()

    cursor.close()
    conn.close()
    return company


def update_company(company_id, name, industry, website, location, hr_contact, description):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        UPDATE companies SET
            company_name=%s, industry=%s, website=%s, location=%s, hr_contact=%s, description=%s
        WHERE company_id=%s
    """
    cursor.execute(query, (name, industry, website, location, hr_contact, description, company_id))
    conn.commit()

    cursor.close()
    conn.close()


def delete_company(company_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM companies WHERE company_id = %s", (company_id,))
    conn.commit()

    cursor.close()
    conn.close()