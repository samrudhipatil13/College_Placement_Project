import bcrypt
from database.db_connection import get_connection

def hash_password(plain_password):
    """Converts a plain text password into a secure bcrypt hash."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(plain_password, hashed_password):
    """Checks if a plain password matches the stored hash."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def register_user(email, plain_password, role='student'):
    """
    Inserts a new user into the users table.
    Returns (True, message) on success, (False, message) on failure.
    """
    conn = get_connection()
    if conn is None:
        return False, "Database connection failed."

    cursor = conn.cursor()

    # Check if email already exists
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    existing_user = cursor.fetchone()
    if existing_user:
        cursor.close()
        conn.close()
        return False, "Email already registered."

    # Hash the password before storing
    hashed_pw = hash_password(plain_password)

    # Insert new user
    query = "INSERT INTO users (email, password_hash, role) VALUES (%s, %s, %s)"
    cursor.execute(query, (email, hashed_pw, role))
    conn.commit()

    cursor.close()
    conn.close()
    return True, "Registration successful!"


import random
from datetime import datetime, timedelta

def generate_otp(user_id):
    """
    Generates a 6-digit OTP, stores it in the database with a 5-minute expiry,
    and returns the OTP (simulating what would be emailed to the user).
    """
    conn = get_connection()
    if conn is None:
        return None

    cursor = conn.cursor()

    otp_code = str(random.randint(100000, 999999))
    expires_at = datetime.now() + timedelta(minutes=5)

    query = "INSERT INTO otp_codes (user_id, otp_code, expires_at) VALUES (%s, %s, %s)"
    cursor.execute(query, (user_id, otp_code, expires_at))
    conn.commit()

    cursor.close()
    conn.close()
    return otp_code


def verify_otp(user_id, entered_otp):
    """
    Checks if the entered OTP matches a valid, unexpired, unused OTP for this user.
    If valid, marks it as used and activates the user's account.
    Returns (True, message) or (False, message).
    """
    conn = get_connection()
    if conn is None:
        return False, "Database connection failed."

    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT * FROM otp_codes
        WHERE user_id = %s AND otp_code = %s AND is_used = FALSE
        ORDER BY otp_id DESC LIMIT 1
    """
    cursor.execute(query, (user_id, entered_otp))
    record = cursor.fetchone()

    if not record:
        cursor.close()
        conn.close()
        return False, "Invalid OTP."

    if record['expires_at'] < datetime.now():
        cursor.close()
        conn.close()
        return False, "OTP has expired. Please request a new one."

    # Mark OTP as used
    cursor.execute("UPDATE otp_codes SET is_used = TRUE WHERE otp_id = %s", (record['otp_id'],))

    # Activate the user account
    cursor.execute("UPDATE users SET account_status = 'active' WHERE user_id = %s", (user_id,))

    conn.commit()
    cursor.close()
    conn.close()
    return True, "Account verified successfully!"


def get_user_by_email(email):
    """Fetches a user's full row by email. Returns None if not found."""
    conn = get_connection()
    if conn is None:
        return None

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()
    return user

def login_user(email, plain_password):
    """
    Verifies email + password against the database.
    Returns (True, user_dict, message) on success,
    or (False, None, message) on failure.
    """
    user = get_user_by_email(email)

    if not user:
        return False, None, "No account found with this email."

    if not check_password(plain_password, user['password_hash']):
        return False, None, "Incorrect password."

    if user['account_status'] == 'pending':
        return False, None, "Account not verified yet. Please complete OTP verification."

    if user['account_status'] == 'suspended':
        return False, None, "This account has been suspended. Contact TPO/Admin."

    return True, user, "Login successful!"