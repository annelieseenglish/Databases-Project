# models/provider_model.py
# ============================================================
# Operations on the Has_Provider associative table.
# ============================================================

from db import execute_query, execute_write


def get_all_relationships():
    """
    Multi-table JOIN: return all patient-physician relationships with names.
    Demonstrates: three-way join across Patient, Has_Provider, Physician.
    """
    return execute_query(
        """
        SELECT p.SSN AS Patient_SSN, p.Name AS Patient_Name,
               ph.License_Number, ph.Name AS Physician_Name, ph.Specialty
        FROM Has_Provider hp
        JOIN Patient p   ON hp.Patient_SSN = p.SSN
        JOIN Physician ph ON hp.Physician_License_Number = ph.License_Number
        ORDER BY p.Name, ph.Name
        """
    )


def assign_provider(patient_ssn, physician_license):
    """
    Assign a physician to a patient.
    INSERT IGNORE avoids duplicate key errors gracefully.
    """
    execute_write(
        """
        INSERT IGNORE INTO Has_Provider (Patient_SSN, Physician_License_Number)
        VALUES (%s, %s)
        """,
        (patient_ssn, physician_license)
    )


def remove_provider(patient_ssn, physician_license):
    """Remove a patient-physician assignment."""
    execute_write(
        """
        DELETE FROM Has_Provider
        WHERE Patient_SSN = %s AND Physician_License_Number = %s
        """,
        (patient_ssn, physician_license)
    )


def relationship_exists(patient_ssn, physician_license):
    """Check whether a specific relationship already exists."""
    rows = execute_query(
        """
        SELECT 1 FROM Has_Provider
        WHERE Patient_SSN = %s AND Physician_License_Number = %s
        """,
        (patient_ssn, physician_license)
    )
    return len(rows) > 0
