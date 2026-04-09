# models/appointment_model.py
# ============================================================
# All database operations for the Appointment entity.
# Enforces: business hours, physician conflict detection.
# ============================================================

from db import execute_query, execute_write
from config import Config
import datetime


# -------------------------------------------------------
# Helper: conflict detection (interval overlap logic)
# Two intervals [A_start, A_end) and [B_start, B_end) overlap
# when A_start < B_end AND B_start < A_end.
# -------------------------------------------------------
OVERLAP_CHECK_SQL = """
    SELECT COUNT(*) AS cnt
    FROM Appointment
    WHERE Physician_License_Number = %s
      AND Date = %s
      AND Appt_ID != %s
      AND TIME_TO_SEC(Time) < TIME_TO_SEC(%s) + (%s * 60)
      AND TIME_TO_SEC(Time) + (Duration * 60) > TIME_TO_SEC(%s)
"""


def _check_business_hours(time_str, duration_minutes):
    """
    Validate that the appointment falls within M-F 08:00-17:00.
    Returns an error message string or None if valid.
    Note: weekday check is done in the route layer using the date.
    """
    start = datetime.datetime.strptime(time_str, "%H:%M").time()
    end_dt = (
        datetime.datetime.combine(datetime.date.today(), start)
        + datetime.timedelta(minutes=int(duration_minutes))
    )
    end = end_dt.time()

    biz_start = datetime.time(Config.BUSINESS_START_HOUR, 0)
    biz_end   = datetime.time(Config.BUSINESS_END_HOUR, 0)

    if start < biz_start or end > biz_end:
        return (
            f"Appointment must be within business hours "
            f"({Config.BUSINESS_START_HOUR}:00 AM – "
            f"{Config.BUSINESS_END_HOUR - 12}:00 PM)."
        )
    return None


def _check_overlap(physician_license, date, time_str, duration, exclude_id=0):
    """
    Returns True if there is an existing overlapping appointment.
    exclude_id is used during updates to ignore the appointment being edited.
    """
    rows = execute_query(
        OVERLAP_CHECK_SQL,
        (physician_license, date, exclude_id, time_str, duration, time_str)
    )
    return rows[0]['cnt'] > 0


# -------------------------------------------------------
# Public CRUD functions
# -------------------------------------------------------

def get_all_appointments():
    """
    JOIN query: return all appointments with patient and physician names.
    """
    return execute_query(
        """
        SELECT a.Appt_ID, a.Date, a.Time, a.Duration,
               p.SSN AS Patient_SSN, p.Name AS Patient_Name,
               ph.License_Number AS Physician_License_Number,
               ph.Name AS Physician_Name, ph.Specialty
        FROM Appointment a
        JOIN Patient p   ON a.Patient_SSN = p.SSN
        JOIN Physician ph ON a.Physician_License_Number = ph.License_Number
        ORDER BY a.Date, a.Time
        """
    )


def get_appointment_by_id(appt_id):
    """Fetch a single appointment (raw row) by primary key."""
    rows = execute_query(
        "SELECT * FROM Appointment WHERE Appt_ID = %s", (appt_id,)
    )
    return rows[0] if rows else None


def get_appointments_by_date(date_str):
    """
    Filtering query: list all appointments for a given date with names.
    """
    return execute_query(
        """
        SELECT a.Appt_ID, a.Date, a.Time, a.Duration,
               p.Name AS Patient_Name,
               ph.Name AS Physician_Name, ph.Specialty
        FROM Appointment a
        JOIN Patient p   ON a.Patient_SSN = p.SSN
        JOIN Physician ph ON a.Physician_License_Number = ph.License_Number
        WHERE a.Date = %s
        ORDER BY a.Time
        """,
        (date_str,)
    )


def get_appointments_by_patient(patient_ssn):
    """Return appointments for a specific patient (with physician info)."""
    return execute_query(
        """
        SELECT a.Appt_ID, a.Date, a.Time, a.Duration,
               ph.Name AS Physician_Name, ph.Specialty
        FROM Appointment a
        JOIN Physician ph ON a.Physician_License_Number = ph.License_Number
        WHERE a.Patient_SSN = %s
        ORDER BY a.Date, a.Time
        """,
        (patient_ssn,)
    )


def get_appointments_by_physician(physician_license):
    """Return appointments for a specific physician (with patient info)."""
    return execute_query(
        """
        SELECT a.Appt_ID, a.Date, a.Time, a.Duration,
               p.Name AS Patient_Name
        FROM Appointment a
        JOIN Patient p ON a.Patient_SSN = p.SSN
        WHERE a.Physician_License_Number = %s
        ORDER BY a.Date, a.Time
        """,
        (physician_license,)
    )


def add_appointment(date_str, time_str, duration, patient_ssn, physician_license):
    """
    Insert a new appointment after validating business hours and conflicts.
    Returns (appt_id, error_message).
    """
    # Business hours check
    err = _check_business_hours(time_str, duration)
    if err:
        return None, err

    # Weekday check (date must be M-F)
    appt_date = datetime.date.fromisoformat(date_str)
    if appt_date.weekday() >= 5:  # 5=Saturday, 6=Sunday
        return None, "Appointments can only be scheduled Monday through Friday."

    # Overlap / conflict check
    if _check_overlap(physician_license, date_str, time_str, duration):
        return None, "This physician already has an overlapping appointment at that time."

    appt_id = execute_write(
        """
        INSERT INTO Appointment (Date, Time, Duration, Patient_SSN, Physician_License_Number)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (date_str, time_str, int(duration), patient_ssn, physician_license)
    )
    return appt_id, None


def update_appointment(appt_id, date_str, time_str, duration, patient_ssn, physician_license):
    """
    Update an appointment after re-validating constraints.
    Returns error message or None on success.
    """
    err = _check_business_hours(time_str, duration)
    if err:
        return err

    appt_date = datetime.date.fromisoformat(date_str)
    if appt_date.weekday() >= 5:
        return "Appointments can only be scheduled Monday through Friday."

    # Exclude the current appointment when checking overlaps (so editing doesn't self-conflict)
    if _check_overlap(physician_license, date_str, time_str, duration, exclude_id=appt_id):
        return "This physician already has an overlapping appointment at that time."

    execute_write(
        """
        UPDATE Appointment
        SET Date = %s, Time = %s, Duration = %s,
            Patient_SSN = %s, Physician_License_Number = %s
        WHERE Appt_ID = %s
        """,
        (date_str, time_str, int(duration), patient_ssn, physician_license, appt_id)
    )
    return None


def delete_appointment(appt_id):
    """Delete an appointment by primary key."""
    execute_write("DELETE FROM Appointment WHERE Appt_ID = %s", (appt_id,))
