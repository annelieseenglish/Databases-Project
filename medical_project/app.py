from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Smt@srmf1",
        database="medical_db"
    )

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/patients')
def patients():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Patient")
    patients = cursor.fetchall()
    conn.close()
    return render_template('patients.html', patients=patients)

@app.route('/add_patient', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        ssn = request.form['ssn']
        name = request.form['name']
        address = request.form['address']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Patient (SSN, Name, Address) VALUES (%s, %s, %s)",
            (ssn, name, address)
        )
        conn.commit()
        conn.close()
        return redirect('/patients')

    return render_template('add_patient.html')

if __name__ == '__main__':
    app.run(debug=True)