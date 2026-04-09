# ClinicChart — COP 4710 Spring 2026
**Web-based Medical Charting & Appointment Scheduling System**
FSU Department of Computer Science

---

## Project Overview

ClinicChart is a lightweight, web-based medical charting platform built for small clinics.
It manages **Patients**, **Physicians**, **Appointments**, and **Patient–Physician relationships**,
backed by a normalized MySQL database with full referential integrity enforcement.

**Advanced Feature:** Smart Scheduling — finds and ranks the top 5 optimal appointment slots
for a physician given a date range, duration, and patient preference using interval overlap
detection, conflict avoidance, and a weighted scoring algorithm.

---

## Technology Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Backend   | Python 3.10+ / Flask              |
| Database  | MySQL 8.0+                        |
| Frontend  | HTML5 / CSS3 / Jinja2 templates   |
| DB Driver | mysql-connector-python            |

---

## Project Structure

```
clinic_app/
├── app.py                     # Flask routes (all pages)
├── config.py                  # DB credentials & business-hour settings
├── db.py                      # MySQL connection + parameterized query helpers
├── database/
│   ├── schema.sql             # CREATE TABLE statements
│   └── seed_data.sql          # Mock data (12 patients, 7 physicians, 21 appointments)
├── models/
│   ├── patient_model.py       # Patient CRUD + join queries
│   ├── physician_model.py     # Physician CRUD + aggregate queries
│   ├── appointment_model.py   # Appointment CRUD + conflict detection
│   └── provider_model.py      # Has_Provider (patient-physician) operations
├── services/
│   └── scheduling_service.py  # Smart Scheduling algorithm
├── templates/
│   ├── base.html              # Shared layout with navbar
│   ├── home.html              # Dashboard
│   ├── patients.html          # Patient list + search
│   ├── patient_form.html      # Add / edit patient
│   ├── patient_detail.html    # Patient detail with providers & appointments
│   ├── physicians.html        # Physician list + specialty filter
│   ├── physician_form.html    # Add / edit physician
│   ├── physician_detail.html  # Physician detail with patients & appointments
│   ├── appointments.html      # Appointments list + date filter
│   ├── appointment_form.html  # Schedule / edit appointment
│   ├── providers.html         # Patient–physician assignment management
│   └── smart_schedule.html    # Smart Scheduling UI
├── static/
│   └── style.css              # Responsive styling
└── README.md                  # This file
```

---

## Local Setup Instructions

### Prerequisites

- Python 3.10 or higher
- MySQL 8.0 or higher (running locally)
- pip

### Step 1 — Clone / Download the Project

```bash
cd your-workspace
# (copy the project folder here)
cd clinic_app
```

### Step 2 — Install Python Dependencies

```bash
pip install flask mysql-connector-python
```

Or create a virtual environment first (recommended):

```bash
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

pip install flask mysql-connector-python
```

### Step 3 — Configure the Database Connection

Open `config.py` and update the credentials:

```python
DB_HOST     = 'localhost'
DB_USER     = 'root'
DB_PASSWORD = 'your_mysql_password'   # ← change this
DB_NAME     = 'clinic_db'
```

You can also set these via environment variables:

```bash
export DB_PASSWORD=your_password
```

### Step 4 — Create and Seed the Database

Log into MySQL and run the two SQL files:

```bash
mysql -u root -p < database/schema.sql
mysql -u root -p < database/seed_data.sql
```

Or from inside the MySQL shell:

```sql
SOURCE /full/path/to/clinic_app/database/schema.sql;
SOURCE /full/path/to/clinic_app/database/seed_data.sql;
```

### Step 5 — Run the Flask Server

```bash
python app.py
```

Open your browser to: **http://localhost:5000**

---

## Database Schema

```
Patient(SSN PK, Name, Address)
Physician(License_Number PK, Name, Specialty)
Appointment(Appt_ID PK, Date, Time, Duration,
            Patient_SSN FK→Patient, Physician_License_Number FK→Physician)
Has_Provider(Patient_SSN PK/FK→Patient,
             Physician_License_Number PK/FK→Physician)
```

All tables are in **BCNF** — every determinant is a candidate key.

### Functional Dependencies

- `SSN → Name, Address`
- `License_Number → Name, Specialty`
- `Appt_ID → Date, Time, Duration, Patient_SSN, Physician_License_Number`
- `(Patient_SSN, Physician_License_Number)` → (uniquely identifies Has_Provider row)

---

## Integrity Constraints Enforced

| Constraint | Enforcement |
|---|---|
| Appointments require valid patient & physician | Foreign key constraints + CASCADE |
| No overlapping physician appointments | Interval overlap SQL check before INSERT/UPDATE |
| Business hours only (M–F, 8AM–5PM) | Python validation in `appointment_model.py` |
| Weekdays only | `date.weekday() < 5` check |
| No duplicate patient–physician relationships | `INSERT IGNORE` + `UNIQUE` composite PK |

---

## SQL Query Highlights

| Query Type | Location |
|---|---|
| Multi-table JOIN (appointments + patient + physician names) | `appointment_model.get_all_appointments()` |
| Aggregate COUNT per physician | `physician_model.get_appointment_count_per_physician()` |
| Three-way JOIN (patient → has_provider → physician) | `provider_model.get_all_relationships()` |
| Interval overlap conflict detection | `appointment_model._check_overlap()` |
| Date filtering | `appointment_model.get_appointments_by_date()` |
| Specialty search (LIKE) | `physician_model.search_by_specialty()` |

---

## Smart Scheduling — Advanced Feature

Located in `services/scheduling_service.py`.

**Algorithm:**
1. Pull all existing appointments for the physician over the date range (SQL query).
2. For each weekday, build a list of busy `(start_min, end_min)` intervals.
3. Iterate the day in 15-minute steps; test each slot against all busy intervals using interval overlap logic: `start < b AND a < end`.
4. Score valid slots: `score = 0.7 × preference_score + 0.3 × gap_efficiency_score`.
5. Sort ascending by score, return top 5.

**Why it's advanced:**
- Requires modeling time as intervals (not discrete points)
- Uses anti-join logic (finding slots that do *not* conflict)
- Multi-factor ranking/scoring
- Non-trivial SQL + Python integration
- Handles edge cases: weekends, business hours, back-to-back appointments

---

## Group Members

- Chloe Brady — Database design & schema implementation
- Olivia Anderson — Backend (Flask routes, CRUD)
- Annelise English — Frontend (HTML/CSS templates)
- Brendan Boedy — Smart Scheduling feature, testing & integration

---

## References

- Flask documentation: https://flask.palletsprojects.com
- MySQL Connector/Python: https://dev.mysql.com/doc/connector-python/en/
- Jinja2 templating: https://jinja.palletsprojects.com
- Interval overlap logic: Allen's Interval Algebra
