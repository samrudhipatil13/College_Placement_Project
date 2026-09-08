from database.db_connection import get_connection

def check_eligibility(student, drive, drive_branches):
    """
    Compares a student's profile dict against a drive's criteria dict.
    Returns (is_eligible: bool, reasons: list of strings)

    If eligible, reasons will be empty.
    If not eligible, reasons lists every rule that failed, in plain language.
    """
    reasons = []

    # 1. Branch check
    if student['branch'] not in drive_branches:
        reasons.append(
            f"Your branch ({student['branch']}) is not included in the eligibility criteria. "
            f"Eligible branches: {', '.join(drive_branches)}."
        )

    # 2. CGPA check
    if student['cgpa'] is None or float(student['cgpa']) < float(drive['min_cgpa']):
        reasons.append(
            f"CGPA is {student['cgpa']}, while the required minimum CGPA is {drive['min_cgpa']}."
        )

    # 3. SSC check
    if student['ssc_percentage'] is None or float(student['ssc_percentage']) < float(drive['min_ssc']):
        reasons.append(
            f"SSC percentage is {student['ssc_percentage']}%, while the required minimum is {drive['min_ssc']}%."
        )

    # 4. HSC check
    if student['hsc_percentage'] is None or float(student['hsc_percentage']) < float(drive['min_hsc']):
        reasons.append(
            f"HSC percentage is {student['hsc_percentage']}%, while the required minimum is {drive['min_hsc']}%."
        )

    # 5. Backlogs check
    if student['backlogs'] is None or int(student['backlogs']) > int(drive['max_backlogs']):
        reasons.append(
            f"You have {student['backlogs']} active backlog(s), but the maximum allowed is {drive['max_backlogs']}."
        )

    # 6. Gender check
    if drive['required_gender'] != 'Any' and student['gender'] != drive['required_gender']:
        reasons.append(
            f"This drive requires gender: {drive['required_gender']}."
        )

    is_eligible = len(reasons) == 0
    return is_eligible, reasons