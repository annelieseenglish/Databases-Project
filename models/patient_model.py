# models/patient_model.py
# ============================================================
# All database operations related to the Patient entity.
# ============================================================

from db import execute_query, execute_write


def get_all_patients():
    """Return every patient ordered by name."""
    return execute_query("SELECT * FROM Patient ORDER BY Name")


def get_patient_by_ssn(ssn):
    """Fetch a single patient by primary key (SSN)."""
    rows = execute_query("SELECT * FROM Patient WHERE SSN = %s", (ssn,))
    return rows[0] if rows else None


def search_patients(term):
    """Search by name or partial SSN (LIKE query with parameterized wildcard)."""
    like = f"%{term}%"
    return execute_query(
        "SELECT * FROM Patient WHERE Name LIKE %s OR SSN LIKE %s ORDER BY Name",
        (like, like)
    )


def add_patient(ssn, name, address):
    """Insert a new patient record."""
    execute_write(
        "INSERT INTO Patient (SSN, Name, Address) VALUES (%s, %s, %s)",
        (ssn, name, address)
    )


def update_patient(ssn, name, address):
    """Update name and address for an existing patient."""
    execute_write(
        "UPDATE Patient SET Name = %s, Address = %s WHERE SSN = %s",
        (name, address, ssn)
    )


def delete_patient(ssn):
    """Delete a patient (cascades to Appointment and Has_Provider)."""
    execute_write("DELETE FROM Patient WHERE SSN = %s", (ssn,))


def get_patient_with_providers(ssn):
    """
    Multi-table JOIN: return a patient with all their assigned physicians.
    Demonstrates: JOIN across Patient, Has_Provider, Physician.
    """
    return execute_query(
        """
        SELECT p.SSN, p.Name AS Patient_Name, p.Address,
               ph.License_Number, ph.Name AS Physician_Name, ph.Specialty
        FROM Patient p
        JOIN Has_Provider hp ON p.SSN = hp.Patient_SSN
        JOIN Physician ph ON hp.Physician_License_Number = ph.License_Number
        WHERE p.SSN = %s
        ORDER BY ph.Name
        """,
        (ssn,)
    )
