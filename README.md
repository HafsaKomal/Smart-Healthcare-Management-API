Smart Healthcare Management API

A scalable backend for a nationwide hospital network built with Flask + MongoDB. Supports patients, doctors, appointments, and prescriptions with secure auth, role-based access, advanced analytics (Mongo aggregation), and high availability (replica sets).

Table of Contents

Features

Architecture

Tech Stack

Quick Start

Configuration

Project Structure

Database Models

API Documentation

Auth

Patients

Doctors

Appointments

Prescriptions

Reports (Aggregation)

Indexing & Performance

Hybrid Query (Mongo + SQL)

Security

Replica Set & High Availability

Testing

Benchmarking Tips

Postman/Swagger

License

Features

RESTful APIs with Flask-RESTful + Blueprints

MongoDB document models (Patients, Doctors, Appointments, Prescriptions)

JWT Auth (patients, doctors, admins) + optional OAuth2 (Google/GitHub)

RBAC: Patient | Doctor | Admin

Advanced Reports via MongoDB Aggregation:

Top doctors by patient load

Disease-wise average treatment duration

Monthly cancellations vs completions

Avg prescription cost per disease (joins Mongo + SQL billing)

Indexing: compound & text indexes with performance comparison

Rate limiting for sensitive endpoints

Encryption: bcrypt for passwords; optional field-level encryption for PHI

Replica set ready (1 primary, 2 secondaries) + failover demo notes

Architecture
Client (Postman/Swagger) 
    -> Flask API (Blueprints, Flask-RESTful)
        -> MongoDB (MongoEngine ODM)
        -> SQL DB (Flask-SQLAlchemy) for Billing
        -> JWT/OAuth2, Rate Limiter, Marshmallow/Reqparse Validators

Tech Stack

Python 3.10+

Flask, Flask-RESTful, Flask-JWT-Extended, Flask-Limiter

MongoEngine (MongoDB)

Flask-SQLAlchemy (SQL layer for billing)

Marshmallow / reqparse (validation)

PyMongo (low-level ops / indexing if needed)

Swagger UI or Postman for API testing

Quick Start
1) Prerequisites

Python 3.10+

MongoDB (standalone or replica set)

(Optional) PostgreSQL/MySQL for billing

Node not required

2) Clone & create virtual env
git clone https://github.com/<you>/<repo>.git
cd <repo>
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

3) Install deps
pip install -r requirements.txt

4) Configure environment

Create .env (see Configuration
).

5) Run server
flask --app app run --debug
# or
python wsgi.py


API will be live at: http://127.0.0.1:5000

Configuration

Create a .env file:

# Flask
FLASK_ENV=development
SECRET_KEY=change_me

# JWT
JWT_SECRET_KEY=please_change_me
JWT_ACCESS_TOKEN_EXPIRES=3600

# MongoDB
MONGODB_URI=mongodb://localhost:27017/healthcare
MONGODB_DB=healthcare

# Optional replica set example:
# MONGODB_URI=mongodb://mongo1:27017,mongo2:27018,mongo3:27019/healthcare?replicaSet=rs0&readPreference=primaryPreferred

# SQL (for billing join)
SQLALCHEMY_DATABASE_URI=sqlite:///billing.db
SQLALCHEMY_TRACK_MODIFICATIONS=False

# OAuth2 (optional)
OAUTH_GOOGLE_CLIENT_ID=
OAUTH_GOOGLE_CLIENT_SECRET=
OAUTH_GITHUB_CLIENT_ID=
OAUTH_GITHUB_CLIENT_SECRET=

Project Structure
.
├─ app/
│  ├─ __init__.py
│  ├─ extensions/            # db, jwt, limiter init
│  ├─ models/                # mongoengine + sqlalchemy models
│  ├─ schemas/               # marshmallow schemas (optional)
│  ├─ resources/             # Flask-RESTful resources (blueprints)
│  │   ├─ auth.py
│  │   ├─ patients.py
│  │   ├─ doctors.py
│  │   ├─ appointments.py
│  │   ├─ prescriptions.py
│  │   └─ reports.py
│  ├─ services/              # domain logic (report builders, joins)
│  ├─ utils/                 # helpers (encryption, pagination)
│  └─ config.py
├─ tests/
├─ requirements.txt
├─ wsgi.py
└─ README.md

Database Models

Mongo (MongoEngine)

Patient: patient_id, name, age, diseases[], embedded appointments[], prescriptions[], user_id

Doctor: doctor_id, name, specialty, availability, user_id

Appointment: appointment_id, patient_id, doctor_id, date, status

Prescription: patient_id, doctor_id, drug, dosage, frequency, cost

SQL (SQLAlchemy)

Billing: id, patient_id, appointment_id, disease, total_cost, created_at

Tip: keep a small seeder to load sample data for demos.

API Documentation

Base URL: http://127.0.0.1:5000/api

Auth

POST /auth/register
POST /auth/login → returns {access_token} (JWT)

Example:

curl -X POST http://127.0.0.1:5000/api/auth/login \
 -H "Content-Type: application/json" \
 -d '{"email":"ali@example.com","password":"Passw0rd!"}'

Patients

GET /patients (Admin/Doctor)
POST /patients (Admin)
GET /patients/<patient_id> (Owner/Doctor/Admin)
PATCH /patients/<patient_id> (Owner/Admin)
DELETE /patients/<patient_id> (Admin)

Payload (create):

{
  "patient_id": "P123",
  "name": "Ali Raza",
  "age": 47,
  "diseases": ["Hypertension", "Diabetes"]
}

Doctors

GET /doctors?specialty=cardiology&available=true
POST /doctors (Admin)
GET /doctors/<doctor_id>
PATCH /doctors/<doctor_id>
DELETE /doctors/<doctor_id> (Admin)

Appointments

POST /appointments (Patient)

{
  "appointment_id": "A789",
  "patient_id": "P123",
  "doctor_id": "D456",
  "date": "2025-09-12",
  "status": "scheduled"
}


GET /appointments?doctor_id=D456&from=2025-09-01&to=2025-09-30
PATCH /appointments/<appointment_id> (status: completed/cancelled)
DELETE /appointments/<appointment_id> (Patient/Admin)

Prescriptions

POST /prescriptions (Doctor)

{
  "patient_id": "P123",
  "doctor_id": "D456",
  "drug": "Metformin",
  "dosage": "500mg",
  "frequency": "Daily",
  "cost": 12.5
}


GET /prescriptions?patient_id=P123
PATCH /prescriptions/<id>
DELETE /prescriptions/<id>

Reports (Aggregation)

GET /reports/top-doctors

Returns top 5 doctors by number of patients/appointments.

GET /reports/disease-trends

Disease-wise average treatment duration (derive from appointment lifecycle or prescription periods).

GET /reports/monthly-appointments-trend?year=2025

Monthly cancellations vs completions.

GET /reports/average-prescription-cost

Average prescription cost per disease (joins Mongo prescriptions/patient disease with SQL billing).

Indexing & Performance

Create indexes on startup or via a script:

Compound index on appointments(doctor_id, date)

Text index on patients.name, doctors.name

Example (PyMongo):

db.appointments.create_index([("doctor_id", 1), ("date", 1)])
db.patients.create_index([("name", "text")])
db.doctors.create_index([("name", "text")])


Include a simple benchmark script to compare:

query time with vs without indexes (log ms and explain plans).

Hybrid Query (Mongo + SQL)

Use patient_id / appointment_id as the join key.

Example service flow:

Aggregate Mongo prescriptions by disease.

For each disease/appointment, query SQL Billing to compute average total cost.

Return combined JSON.

Security

JWT with short-lived access tokens.

RBAC: enforce per-role access in decorators.

Rate limiting: e.g., /auth/login limited to 5/min.

Passwords: bcrypt hash + salt.

Sensitive data: optional MongoDB CSFLE (field-level encryption).

Validation: reqparse/Marshmallow for dates, dosage units, enums (scheduled|completed|cancelled).

Replica Set & High Availability

Configure a 3-node replica set (1 primary, 2 secondaries).

Connect with MONGODB_URI including replicaSet=rs0.

Failover demo: stop primary, observe driver auto-reconnect; test readConcern/writeConcern (e.g., majority) to show consistency vs performance trade-offs.

Testing
pytest -q
# or
python -m pytest -q


Include:

Unit tests for resources/services

Auth & RBAC tests

Aggregation pipelines (mock data)

Hybrid join tests (SQLite fixtures)

Benchmarking Tips

Use explain("executionStats") for Mongo queries.

Compare response times for /reports/* before/after indexes.

Plot monthly stats from /reports/monthly-appointments-trend to validate analytics.

Postman/Swagger

/docs (Swagger UI) if enabled, or include docs/openapi.yaml.

Postman collection: postman/SmartHealthcare.postman_collection.json.

