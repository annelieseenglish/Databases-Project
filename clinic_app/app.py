# app.py
# ============================================================
# Main Flask application — registers all routes.
# Run with: python app.py
# ============================================================

from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config

import models.patient_model       as patient_model
import models.physician_model     as physician_model
import models.appointment_model   as appointment_model
import models.provider_model      as provider_model
from services.scheduling_service  import find_available_slots

import datetime

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY


# ============================================================
# HOME
# ============================================================

@app.route('/')
def home():
    """Dashboard with summary counts."""
    patients    = patient_model.get_all_patients()
    physicians  = physician_model.get_all_physicians()
    appointments = appointment_model.get_all_appointments()
    return render_template(
        'home.html',
        patient_count=len(patients),
        physician_count=len(physicians),
        appointment_count=len(appointments)
    )


# ============================================================
# PATIENTS
# ============================================================

@app.route('/patients')
def patients():
    term = request.args.get('search', '').strip()
    if term:
        patient_list = patient_model.search_patients(term)
    else:
        patient_list = patient_model.get_all_patients()
    return render_template('patients.html', patients=patient_list, search=term)


@app.route('/patients/add', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        ssn     = request.form['ssn'].strip()
        name    = request.form['name'].strip()
        address = request.form['address'].strip()
        try:
            patient_model.add_patient(ssn, name, address)
            flash(f"Patient '{name}' added successfully.", 'success')
            return redirect(url_for('patients'))
        except Exception as e:
            flash(f"Error adding patient: {e}", 'danger')
    return render_template('patient_form.html', action='Add', patient=None)


@app.route('/patients/edit/<ssn>', methods=['GET', 'POST'])
def edit_patient(ssn):
    patient = patient_model.get_patient_by_ssn(ssn)
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('patients'))

    if request.method == 'POST':
        name    = request.form['name'].strip()
        address = request.form['address'].strip()
        try:
            patient_model.update_patient(ssn, name, address)
            flash(f"Patient updated.", 'success')
            return redirect(url_for('patients'))
        except Exception as e:
            flash(f"Error updating patient: {e}", 'danger')
    return render_template('patient_form.html', action='Edit', patient=patient)


@app.route('/patients/delete/<ssn>', methods=['POST'])
def delete_patient(ssn):
    try:
        patient_model.delete_patient(ssn)
        flash('Patient deleted.', 'success')
    except Exception as e:
        flash(f"Error: {e}", 'danger')
    return redirect(url_for('patients'))


@app.route('/patients/<ssn>/providers')
def patient_providers(ssn):
    patient = patient_model.get_patient_by_ssn(ssn)
    if not patient:
        flash('Patient not found.', 'danger')
        return redirect(url_for('patients'))
    providers = patient_model.get_patient_with_providers(ssn)
    appointments = appointment_model.get_appointments_by_patient(ssn)
    return render_template('patient_detail.html',
                           patient=patient,
                           providers=providers,
                           appointments=appointments)


# ============================================================
# PHYSICIANS
# ============================================================

@app.route('/physicians')
def physicians():
    specialty = request.args.get('specialty', '').strip()
    if specialty:
        physician_list = physician_model.search_by_specialty(specialty)
    else:
        physician_list = physician_model.get_appointment_count_per_physician()
    specialties = physician_model.get_all_specialties()
    return render_template('physicians.html',
                           physicians=physician_list,
                           specialties=specialties,
                           selected_specialty=specialty)


@app.route('/physicians/add', methods=['GET', 'POST'])
def add_physician():
    if request.method == 'POST':
        license_num = request.form['license_number'].strip()
        name        = request.form['name'].strip()
        specialty   = request.form['specialty'].strip()
        try:
            physician_model.add_physician(license_num, name, specialty)
            flash(f"Physician '{name}' added.", 'success')
            return redirect(url_for('physicians'))
        except Exception as e:
            flash(f"Error: {e}", 'danger')
    return render_template('physician_form.html', action='Add', physician=None)


@app.route('/physicians/edit/<license_number>', methods=['GET', 'POST'])
def edit_physician(license_number):
    physician = physician_model.get_physician_by_license(license_number)
    if not physician:
        flash('Physician not found.', 'danger')
        return redirect(url_for('physicians'))

    if request.method == 'POST':
        name      = request.form['name'].strip()
        specialty = request.form['specialty'].strip()
        try:
            physician_model.update_physician(license_number, name, specialty)
            flash('Physician updated.', 'success')
            return redirect(url_for('physicians'))
        except Exception as e:
            flash(f"Error: {e}", 'danger')
    return render_template('physician_form.html', action='Edit', physician=physician)


@app.route('/physicians/delete/<license_number>', methods=['POST'])
def delete_physician(license_number):
    try:
        physician_model.delete_physician(license_number)
        flash('Physician deleted.', 'success')
    except Exception as e:
        flash(f"Error: {e}", 'danger')
    return redirect(url_for('physicians'))


@app.route('/physicians/<license_number>/patients')
def physician_patients(license_number):
    physician = physician_model.get_physician_by_license(license_number)
    if not physician:
        flash('Physician not found.', 'danger')
        return redirect(url_for('physicians'))
    patients_list = physician_model.get_physician_patients(license_number)
    appointments  = appointment_model.get_appointments_by_physician(license_number)
    return render_template('physician_detail.html',
                           physician=physician,
                           patients=patients_list,
                           appointments=appointments)


# ============================================================
# APPOINTMENTS
# ============================================================

@app.route('/appointments')
def appointments():
    date_filter = request.args.get('date', '').strip()
    if date_filter:
        appt_list = appointment_model.get_appointments_by_date(date_filter)
    else:
        appt_list = appointment_model.get_all_appointments()
    return render_template('appointments.html',
                           appointments=appt_list,
                           date_filter=date_filter)


@app.route('/appointments/add', methods=['GET', 'POST'])
def add_appointment():
    patients_list  = patient_model.get_all_patients()
    physicians_list = physician_model.get_all_physicians()

    if request.method == 'POST':
        date          = request.form['date'].strip()
        time          = request.form['time'].strip()
        duration      = request.form['duration'].strip()
        patient_ssn   = request.form['patient_ssn'].strip()
        physician_lic = request.form['physician_license'].strip()

        appt_id, err = appointment_model.add_appointment(
            date, time, duration, patient_ssn, physician_lic
        )
        if err:
            flash(err, 'danger')
        else:
            flash(f"Appointment #{appt_id} scheduled successfully.", 'success')
            return redirect(url_for('appointments'))

    return render_template('appointment_form.html',
                           action='Schedule',
                           appt=None,
                           patients=patients_list,
                           physicians=physicians_list)


@app.route('/appointments/edit/<int:appt_id>', methods=['GET', 'POST'])
def edit_appointment(appt_id):
    appt = appointment_model.get_appointment_by_id(appt_id)
    if not appt:
        flash('Appointment not found.', 'danger')
        return redirect(url_for('appointments'))

    patients_list   = patient_model.get_all_patients()
    physicians_list = physician_model.get_all_physicians()

    if request.method == 'POST':
        date          = request.form['date'].strip()
        time          = request.form['time'].strip()
        duration      = request.form['duration'].strip()
        patient_ssn   = request.form['patient_ssn'].strip()
        physician_lic = request.form['physician_license'].strip()

        err = appointment_model.update_appointment(
            appt_id, date, time, duration, patient_ssn, physician_lic
        )
        if err:
            flash(err, 'danger')
        else:
            flash('Appointment updated.', 'success')
            return redirect(url_for('appointments'))

    return render_template('appointment_form.html',
                           action='Edit',
                           appt=appt,
                           patients=patients_list,
                           physicians=physicians_list)


@app.route('/appointments/delete/<int:appt_id>', methods=['POST'])
def delete_appointment(appt_id):
    try:
        appointment_model.delete_appointment(appt_id)
        flash('Appointment deleted.', 'success')
    except Exception as e:
        flash(f"Error: {e}", 'danger')
    return redirect(url_for('appointments'))


# ============================================================
# PROVIDERS (Has_Provider)
# ============================================================

@app.route('/providers')
def providers():
    relationships = provider_model.get_all_relationships()
    patients_list  = patient_model.get_all_patients()
    physicians_list = physician_model.get_all_physicians()
    return render_template('providers.html',
                           relationships=relationships,
                           patients=patients_list,
                           physicians=physicians_list)


@app.route('/providers/assign', methods=['POST'])
def assign_provider():
    patient_ssn   = request.form['patient_ssn'].strip()
    physician_lic = request.form['physician_license'].strip()
    try:
        if provider_model.relationship_exists(patient_ssn, physician_lic):
            flash('This patient-physician relationship already exists.', 'warning')
        else:
            provider_model.assign_provider(patient_ssn, physician_lic)
            flash('Provider assigned successfully.', 'success')
    except Exception as e:
        flash(f"Error: {e}", 'danger')
    return redirect(url_for('providers'))


@app.route('/providers/remove', methods=['POST'])
def remove_provider():
    patient_ssn   = request.form['patient_ssn'].strip()
    physician_lic = request.form['physician_license'].strip()
    try:
        provider_model.remove_provider(patient_ssn, physician_lic)
        flash('Provider relationship removed.', 'success')
    except Exception as e:
        flash(f"Error: {e}", 'danger')
    return redirect(url_for('providers'))


# ============================================================
# SMART SCHEDULING (Advanced Feature)
# ============================================================

@app.route('/smart-schedule', methods=['GET', 'POST'])
def smart_schedule():
    physicians_list = physician_model.get_all_physicians()
    slots = []
    form_data = {}

    if request.method == 'POST':
        physician_lic = request.form['physician_license'].strip()
        start_date    = request.form['start_date'].strip()
        end_date      = request.form['end_date'].strip()
        duration      = int(request.form['duration'].strip())
        preference    = request.form.get('preference', 'earliest')

        form_data = {
            'physician_license': physician_lic,
            'start_date': start_date,
            'end_date': end_date,
            'duration': duration,
            'preference': preference
        }

        try:
            sd = datetime.date.fromisoformat(start_date)
            ed = datetime.date.fromisoformat(end_date)
            if ed < sd:
                flash('End date must be on or after start date.', 'danger')
            elif (ed - sd).days > 60:
                flash('Date range cannot exceed 60 days.', 'warning')
            elif duration < 15 or duration > 120:
                flash('Duration must be between 15 and 120 minutes.', 'warning')
            else:
                slots = find_available_slots(
                    physician_lic, sd, ed, duration, preference
                )
                if not slots:
                    flash('No available slots found in this range. Try widening the date range.', 'info')
        except ValueError as e:
            flash(f"Invalid input: {e}", 'danger')

    return render_template('smart_schedule.html',
                           physicians=physicians_list,
                           slots=slots,
                           form_data=form_data)


# ============================================================
# Run
# ============================================================
if __name__ == '__main__':
    app.run(debug=True, port=5001, host = '127.0.0.1')
