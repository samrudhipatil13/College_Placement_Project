from utils.auth_utils import hash_password
from database.db_connection import get_connection

def create_admin(email, password):
    conn = get_connection()
    cursor = conn.cursor()

    hashed_pw = hash_password(password)

    cursor.execute(
        "INSERT INTO users (email, password_hash, role, account_status) VALUES (%s, %s, %s, %s)",
        (email, hashed_pw, 'admin', 'active')
    )
    conn.commit()
    cursor.close()
    conn.close()
    print(f"Admin account created for {email}")

# Run this once to create your TPO account
create_admin("tpo@college.edu", "AdminPass123")