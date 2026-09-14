# Patient Registration Voice AI Agent

A voice-powered patient registration and receptionist system built using **FastAPI**, **SQLite**, and **Vapi Voice AI**.

The system provides a natural conversational experience where callers can:

- Register as new patients through a voice conversation
- Look up existing patient records
- Confirm information before saving
- Receive assistance with appointment-related requests
- Provide appointment rescheduling preferences

This project demonstrates a complete healthcare voice AI workflow connected to a backend patient management API with persistent storage.

---

# Live Demo

## AI Receptionist Phone Number

Call the AI receptionist:

```
+1 (815) 415 9016
```

Assistant:

```
Ava - Patient Registration Receptionist
```

Supported workflows:

- New patient registration
- Existing patient lookup
- Patient information collection
- Appointment request handling
- Appointment preference collection

---

# Production API

Base URL:

```
https://patient-registration-voice-ai.onrender.com
```

Swagger Documentation:

```
https://patient-registration-voice-ai.onrender.com/docs
```

Available endpoints:

```
POST /patients

GET /patients/by-phone/{phone_number}
```

---

# Architecture

```
Caller
 |
 v
Vapi Voice AI Assistant
(Ava - Patient Registration Receptionist)
 |
 v
FastAPI REST API
 |
 v
SQLite Database
```

---

# Workflow

## Existing Patient Flow

```
Caller
 |
Provides registered phone number
 |
Phone number confirmation
 |
find_patient_by_phone
 |
Patient record found
 |
Continue assistance
```

---

## New Patient Registration Flow

```
Caller
 |
Provides phone number
 |
Patient lookup
 |
No existing record found
 |
Collect patient information
 |
Validate information
 |
Read information back
 |
Caller confirms
 |
create_patient
 |
Patient record saved
```

---

# Features

## Voice Receptionist

The AI receptionist can:

- Greet callers professionally
- Understand caller intent
- Collect patient information
- Search existing patient records
- Register new patients
- Handle corrections
- Confirm information before saving
- Handle appointment-related requests safely

---

# Existing Patient Lookup

Existing patients are identified using their registered phone number.

Flow:

```
Phone Number
      |
      v
find_patient_by_phone
      |
      v
Patient Record
```

The assistant uses only information returned from the backend and never invents patient information.

---

# Patient Registration

New patients are created only after:

1. Required information is collected
2. Information is read back to the caller
3. Caller explicitly confirms

Flow:

```
Collect Information
        |
        v
Validate Information
        |
        v
Read Back Details
        |
        v
Caller Confirmation
        |
        v
Create Patient Record
```

---

# Appointment Handling

The assistant supports appointment-related requests.

Currently supported:

- Collect appointment reason
- Collect current appointment details
- Collect preferred date
- Collect preferred time
- Record scheduling preferences

Actual appointment booking is not implemented.

The assistant does not claim appointments are booked, changed, or confirmed.

Example response:

```
I'll note your preferences and the scheduling team can follow up with available options.
```

---

# Technology Stack

## Voice Layer

### Vapi Voice AI

Used for:

- Voice conversations
- Assistant behavior
- Tool execution
- Natural language interaction
- Telephony integration

---

## Backend

### FastAPI

Used for:

- REST API endpoints
- Request validation
- Business logic
- Patient management

---

## Database

### SQLite

Used for:

- Patient persistence
- Local development
- Demo environment

---

# Patient Data Model

## Required Fields

| Field | Description |
|---|---|
| first_name | Patient first name |
| last_name | Patient last name |
| date_of_birth | Date of birth |
| sex | Patient sex |
| phone_number | 10-digit US phone number |
| address_line_1 | Primary address |
| city | City |
| state | State abbreviation |
| zip_code | ZIP code |

---

## Optional Fields

| Field | Description |
|---|---|
| email | Email address |
| address_line_2 | Additional address |
| insurance_provider | Insurance provider |
| insurance_member_id | Insurance member ID |
| preferred_language | Preferred language |
| emergency_contact_name | Emergency contact name |
| emergency_contact_phone | Emergency contact phone |

---

# Validation Rules

## Phone Number

Requirements:

- Must contain exactly 10 digits

Example:

```
8154159016
```

The assistant confirms phone numbers before lookup.

---

## Date of Birth

Validation:

- Must be a valid date
- Cannot be in the future

---

## Sex

Allowed values:

```
Male
Female
Other
Decline to Answer
```

---

## State

State names are normalized.

Examples:

```
New York → NY

California → CA
```

---

## ZIP Code

Supported formats:

```
10001
```

or:

```
10001-1234
```

---

# API Endpoints

## Create Patient

```
POST /patients
```

Creates a new patient record.

Example request:

```json
{
  "first_name": "Joan",
  "last_name": "Smith",
  "date_of_birth": "2002-01-18",
  "sex": "Female",
  "phone_number": "6465557890",
  "address_line_1": "742 Evergreen Terrace",
  "city": "New York",
  "state": "NY",
  "zip_code": "10001",
  "email": "joan.smith@gmail.com"
}
```

---

## Find Patient By Phone

```
GET /patients/by-phone/{phone_number}
```

Example:

```
GET /patients/by-phone/8154159016
```

Example response:

```json
{
  "data": {
    "first_name": "Sahil",
    "last_name": "Kumar",
    "phone_number": "8154159016"
  },
  "error": null
}
```

---

# Vapi Tools

## find_patient_by_phone

Purpose:

Find an existing patient using their registered phone number.

Input:

```json
{
  "phone_number": "8154159016"
}
```

Behavior:

- Called after phone number confirmation
- Sends normalized 10-digit phone number
- Waits for backend response
- Uses only returned information

---

## create_patient

Purpose:

Create a patient after caller confirmation.

Flow:

```
Collect Information
        |
        v
Read Back Information
        |
        v
Caller Confirms
        |
        v
create_patient Tool
        |
        v
Patient Created
```

The assistant never creates a patient without confirmation.

---

# Local Development Setup

## Clone Repository

```bash
git clone https://github.com/sahilkumar-sk/patient-registration-voice-ai.git

cd patient-registration-voice-ai
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv .venv

.venv\Scripts\activate
```

### macOS/Linux

```bash
python -m venv .venv

source .venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create:

```
.env
```

Example:

```env
DATABASE_URL=sqlite:///./patients.db
```

---

## Run Application

```bash
uvicorn app.main:app --reload
```

API runs locally:

```
http://127.0.0.1:8000
```

---

# Deployment

The backend is deployed using Render.

Production URL:

```
https://patient-registration-voice-ai.onrender.com
```

The application starts using:

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Deployment configuration is provided through:

```
Procfile
```

---

# Testing Scenarios

## Scenario 1: Existing Patient Lookup

Example:

```
Phone:
8154159016
```

Expected:

```
Phone lookup
        |
Patient found
        |
Continue conversation
```

---

## Scenario 2: New Patient Registration

Example:

```
Caller:
I want to register as a new patient
```

Expected:

```
Collect information
        |
Validate information
        |
Confirm details
        |
Create patient record
        |
Registration completed
```

---

## Scenario 3: Appointment Request

Example:

```
Caller:
I want to reschedule my appointment
```

Expected:

```
Collect appointment details
        |
Collect preferred date/time
        |
Record preferences
        |
Scheduling team follow-up message
```

---

# Safety Rules

The assistant:

- Never exposes internal tools
- Never invents patient information
- Never creates patients without confirmation
- Never claims appointments are scheduled without scheduling access
- Uses only verified API responses
- Waits for tool responses before continuing

---

# Known Limitations

## Appointment Scheduling

Actual appointment booking is not implemented.

The assistant only collects:

- Appointment reason
- Current appointment information
- Preferred date
- Preferred time

---

## Voice Recognition

Speech recognition can occasionally misinterpret spoken digits.

The assistant handles this by:

- Normalizing phone numbers
- Confirming phone numbers
- Allowing corrections

---

# Future Improvements

Possible improvements:

- Appointment scheduling integration
- Patient update API
- Appointment availability lookup
- Authentication
- Admin dashboard
- Cloud database migration
- Automated test coverage
- Multi-language support

---

# Project Structure

```
patient-registration-voice-ai/

├── app/
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   └── routers/
│
├── tests/
│
├── voice/
│
├── requirements.txt
├── Procfile
├── README.md
└── .env.example
```

---

# Project Summary

This project demonstrates an end-to-end healthcare voice AI receptionist workflow.

```
Caller
 |
 v
Vapi Voice Assistant
 |
 v
FastAPI Backend
 |
 v
SQLite Database
```

The system supports:

- New patient registration
- Existing patient lookup
- Safe information confirmation
- Appointment request handling

---