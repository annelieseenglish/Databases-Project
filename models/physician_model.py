# models/physician_model.py
# ============================================================
# All database operations related to the Physician entity.
# ============================================================

from db import execute_query, execute_write


def get_all_physicians():
    """Return every physician ordered by name."""
    return execute_query("SELECT * FROM Physician ORDER BY Name")


def get_physician_by_license(license_number):
    """Fetch a single physician by primary key."""
    rows = execute_query(
        "SELECT * FROM Physician WHERE License_Number = %s", (license_number,)
    )
    return rows[0] if rows else None


def search_by_specialty(specialty):
    """Filter physicians by specialty (partial match, case-insensitive)."""
    return execute_query(
        "SELECT * FROM Physician WHERE Specialty LIKE %s ORDER BY Name",
        (f"%{specialty}%",)
    )


def get_all_specialties():
    """Return distinct specialty values for filter dropdowns."""
    return execute_query("SELECT DISTINCT Specialty FROM Physician ORDER BY Specialty")


def add_physician(license_number, name, specialty):
    """Insert a new physician record."""
    execute_write(
        "INSERT INTO Physician (License_Number, Name, Specialty) VALUES (%s, %s, %s)",
        (license_number, name, specialty)
    )


def update_physician(license_number, name, specialty):
    """Update physician name and specialty."""
    execute_write(
        "UPDATE Physician SET Name = %s, Specialty = %s WHERE License_Number = %s",
        (name, specialty, license_number)
    )


def delete_physician(license_number):
    """Delete a physician (cascades to Appointment and Has_Provider)."""
    execute_write(
        "DELETE FROM Physician WHERE License_Number = %s", (license_number,)
    )


def get_physician_patients(license_number):
    """
    Multi-table JOIN: list all patients assigned to a given physician.
    """
    return execute_query(
        """
        SELECT p.SSN, p.Name AS Patient_Name, p.Address
        FROM Patient p
        JOIN Has_Provider hp ON p.SSN = hp.Patient_SSN
        WHERE hp.Physician_License_Number = %s
        ORDER BY p.Name
        """,
        (license_number,)
    )


def get_appointment_count_per_physician():
    """
    Aggregate query: COUNT appointments grouped by physician.
    Demonstrates: GROUP BY + aggregate function.
    """
    return execute_query(
        """
        SELECT ph.License_Number, ph.Name, ph.Specialty,
               COUNT(a.Appt_ID) AS Appointment_Count
        FROM Physician ph
        LEFT JOIN Appointment a ON ph.License_Number = a.Physician_License_Number
        GROUP BY ph.License_Number, ph.Name, ph.Specialty
        ORDER BY Appointment_Count DESC
        """
    )
