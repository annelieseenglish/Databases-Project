-- ============================================================
-- seed_data.sql: Realistic mock data for development/demo
-- ============================================================
USE clinic_db;

-- -------------------------------------------------------
-- Patients (12 records)
-- -------------------------------------------------------
INSERT INTO Patient (SSN, Name, Address) VALUES
('123-45-6789', 'Alice Johnson',     '142 Maple St, Tallahassee, FL 32301'),
('234-56-7890', 'Robert Martinez',   '88 Oak Ave, Tallahassee, FL 32303'),
('345-67-8901', 'Carol Williams',    '7 Pine Rd, Tallahassee, FL 32304'),
('456-78-9012', 'David Brown',       '33 Elm Blvd, Tallahassee, FL 32305'),
('567-89-0123', 'Emily Davis',       '219 Birch Ln, Tallahassee, FL 32306'),
('678-90-1234', 'Frank Thompson',    '501 Cedar Dr, Tallahassee, FL 32307'),
('789-01-2345', 'Grace Lee',         '18 Walnut Ct, Tallahassee, FL 32308'),
('890-12-3456', 'Henry Wilson',      '405 Spruce St, Tallahassee, FL 32309'),
('901-23-4567', 'Isabella Moore',    '67 Chestnut Ave, Tallahassee, FL 32310'),
('012-34-5678', 'James Taylor',      '300 Willow Way, Tallahassee, FL 32311'),
('111-22-3333', 'Karen Anderson',    '99 Redwood Rd, Tallahassee, FL 32312'),
('444-55-6666', 'Luis Hernandez',    '250 Magnolia Dr, Tallahassee, FL 32313');

-- -------------------------------------------------------
-- Physicians (7 records)
-- -------------------------------------------------------
INSERT INTO Physician (License_Number, Name, Specialty) VALUES
('FL-MD-10001', 'Dr. Sarah Chen',        'Family Medicine'),
('FL-MD-10002', 'Dr. James Patel',       'Cardiology'),
('FL-MD-10003', 'Dr. Maria Gonzalez',    'Pediatrics'),
('FL-MD-10004', 'Dr. Kevin O\'Brien',    'Orthopedics'),
('FL-MD-10005', 'Dr. Linda Park',        'Dermatology'),
('FL-MD-10006', 'Dr. Thomas Reed',       'Neurology'),
('FL-MD-10007', 'Dr. Angela Foster',     'Internal Medicine');

-- -------------------------------------------------------
-- Has_Provider (patient-physician assignments)
-- -------------------------------------------------------
INSERT INTO Has_Provider (Patient_SSN, Physician_License_Number) VALUES
('123-45-6789', 'FL-MD-10001'),
('123-45-6789', 'FL-MD-10002'),
('234-56-7890', 'FL-MD-10001'),
('234-56-7890', 'FL-MD-10004'),
('345-67-8901', 'FL-MD-10003'),
('456-78-9012', 'FL-MD-10002'),
('456-78-9012', 'FL-MD-10006'),
('567-89-0123', 'FL-MD-10005'),
('567-89-0123', 'FL-MD-10007'),
('678-90-1234', 'FL-MD-10001'),
('789-01-2345', 'FL-MD-10003'),
('789-01-2345', 'FL-MD-10007'),
('890-12-3456', 'FL-MD-10004'),
('901-23-4567', 'FL-MD-10006'),
('012-34-5678', 'FL-MD-10001'),
('012-34-5678', 'FL-MD-10005'),
('111-22-3333', 'FL-MD-10002'),
('444-55-6666', 'FL-MD-10007');

-- -------------------------------------------------------
-- Appointments (21 records, spread across future dates)
-- All within M-F 08:00-17:00 business hours
-- -------------------------------------------------------
INSERT INTO Appointment (Date, Time, Duration, Patient_SSN, Physician_License_Number) VALUES
-- Dr. Sarah Chen (FL-MD-10001)
('2026-04-14', '08:00:00', 30, '123-45-6789', 'FL-MD-10001'),
('2026-04-14', '09:00:00', 60, '234-56-7890', 'FL-MD-10001'),
('2026-04-14', '11:00:00', 30, '678-90-1234', 'FL-MD-10001'),
('2026-04-15', '09:30:00', 30, '012-34-5678', 'FL-MD-10001'),

-- Dr. James Patel (FL-MD-10002) - Cardiology
('2026-04-14', '08:30:00', 45, '456-78-9012', 'FL-MD-10002'),
('2026-04-14', '10:30:00', 60, '111-22-3333', 'FL-MD-10002'),
('2026-04-15', '14:00:00', 45, '123-45-6789', 'FL-MD-10002'),

-- Dr. Maria Gonzalez (FL-MD-10003) - Pediatrics
('2026-04-14', '09:00:00', 30, '345-67-8901', 'FL-MD-10003'),
('2026-04-14', '10:00:00', 30, '789-01-2345', 'FL-MD-10003'),
('2026-04-16', '08:00:00', 30, '345-67-8901', 'FL-MD-10003'),

-- Dr. Kevin O'Brien (FL-MD-10004) - Orthopedics
('2026-04-15', '10:00:00', 60, '234-56-7890', 'FL-MD-10004'),
('2026-04-15', '13:00:00', 45, '890-12-3456', 'FL-MD-10004'),
('2026-04-17', '09:00:00', 60, '890-12-3456', 'FL-MD-10004'),

-- Dr. Linda Park (FL-MD-10005) - Dermatology
('2026-04-14', '13:00:00', 30, '567-89-0123', 'FL-MD-10005'),
('2026-04-14', '14:00:00', 30, '012-34-5678', 'FL-MD-10005'),
('2026-04-16', '10:00:00', 30, '567-89-0123', 'FL-MD-10005'),

-- Dr. Thomas Reed (FL-MD-10006) - Neurology
('2026-04-15', '08:00:00', 60, '456-78-9012', 'FL-MD-10006'),
('2026-04-15', '11:00:00', 45, '901-23-4567', 'FL-MD-10006'),

-- Dr. Angela Foster (FL-MD-10007) - Internal Medicine
('2026-04-14', '10:00:00', 45, '567-89-0123', 'FL-MD-10007'),
('2026-04-14', '14:30:00', 30, '789-01-2345', 'FL-MD-10007'),
('2026-04-16', '13:00:00', 60, '444-55-6666', 'FL-MD-10007');
