-- ============================================================
-- Medical Charting & Appointment Scheduling System
-- COP 4710 - Spring 2026
-- schema.sql: Create all tables with keys and constraints
-- ============================================================

DROP DATABASE IF EXISTS clinic_db;
CREATE DATABASE clinic_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE clinic_db;

-- -------------------------------------------------------
-- Patient table
-- SSN is the primary key (stored as VARCHAR for formatting)
-- Functional Dependency: SSN → Name, Address
-- -------------------------------------------------------
CREATE TABLE Patient (
    SSN         VARCHAR(11)     NOT NULL,   -- format: XXX-XX-XXXX
    Name        VARCHAR(100)    NOT NULL,
    Address     VARCHAR(255)    NOT NULL,
    PRIMARY KEY (SSN)
);

-- -------------------------------------------------------
-- Physician table
-- License_Number is the primary key
-- Functional Dependency: License_Number → Name, Specialty
-- -------------------------------------------------------
CREATE TABLE Physician (
    License_Number  VARCHAR(20)     NOT NULL,
    Name            VARCHAR(100)    NOT NULL,
    Specialty       VARCHAR(100)    NOT NULL,
    PRIMARY KEY (License_Number)
);

-- -------------------------------------------------------
-- Appointment table
-- Appt_ID is the primary key (auto-increment)
-- FKs enforce referential integrity to Patient and Physician
-- Functional Dependency: Appt_ID → Date, Time, Duration, Patient_SSN, Physician_License_Number
-- -------------------------------------------------------
CREATE TABLE Appointment (
    Appt_ID                 INT             NOT NULL AUTO_INCREMENT,
    Date                    DATE            NOT NULL,
    Time                    TIME            NOT NULL,
    Duration                INT             NOT NULL,   -- duration in minutes
    Patient_SSN             VARCHAR(11)     NOT NULL,
    Physician_License_Number VARCHAR(20)    NOT NULL,
    PRIMARY KEY (Appt_ID),
    FOREIGN KEY (Patient_SSN)
        REFERENCES Patient(SSN)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (Physician_License_Number)
        REFERENCES Physician(License_Number)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- -------------------------------------------------------
-- Has_Provider (associative/junction table)
-- Represents the many-to-many relationship between Patients and Physicians
-- Composite PK: (Patient_SSN, Physician_License_Number)
-- -------------------------------------------------------
CREATE TABLE Has_Provider (
    Patient_SSN             VARCHAR(11)     NOT NULL,
    Physician_License_Number VARCHAR(20)    NOT NULL,
    PRIMARY KEY (Patient_SSN, Physician_License_Number),
    FOREIGN KEY (Patient_SSN)
        REFERENCES Patient(SSN)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (Physician_License_Number)
        REFERENCES Physician(License_Number)
        ON DELETE CASCADE ON UPDATE CASCADE
);
