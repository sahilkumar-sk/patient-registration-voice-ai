# Patient Registration Voice AI Agent

A voice-powered patient registration and receptionist system built with **FastAPI**, **SQLite**, and **Vapi Voice AI**.

The system allows callers to interact with an AI receptionist that can:
- Register new patients through a natural voice conversation
- Find existing patient records using phone number lookup
- Validate patient information
- Confirm details before creating records
- Handle appointment-related requests safely

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

## Flow

### Existing Patient

```
Caller provides phone number
        |
        v
find_patient_by_phone
        |
        v
Patient found
        |
        v
Continue conversation
```

### New Patient Registration

```
Caller provides phone number
        |
        v
Patient lookup
        |
        v
No patient found
        |
        v
Collect patient information
        |
        v
Read information back
        |
        v
Caller confirms
        |
        v
create_patient
        |
        v
Patient created
```

---

# Features

## Voice Receptionist

The AI receptionist can:
- Welcome callers
- Collect caller information
- Find existing patient records
- Register new patients
- Confirm information before saving
- Handle corrections during registration

## Patient Lookup

Endpoint:

```
GET /patients/by-phone/{phone_number}
```

## Patient Registration

New patients are created only after:
1. Required information is collected
2. Information is read back
3. Caller explicitly confirms

---

# Technology Stack

## Voice AI
- Vapi Voice AI Platform

## Backend
- Python
- FastAPI
- Pydantic

## Database
- SQLite

---

# Patient Data Model

## Required Fields

| Field | Description |
|---|---|
| first_name | Patient first name |
| last_name | Patient last name |
| date_of_birth | Date of birth |
| sex | Patient sex |
| phone_number | US phone number |
| address_line_1 | Primary address |
| city | City |
| state | State abbreviation |
| zip_code | ZIP code |

## Optional Fields

| Field | Description |
|---|---|
| email | Email address |
| address_line_2 | Additional address |
| insurance_provider | Insurance company |
| insurance_member_id | Insurance member ID |
| preferred_language | Preferred language |
| emergency_contact_name | Emergency contact |
| emergency_contact_phone | Emergency contact phone |

---

# Validation Rules

- Phone number must be a valid 10-digit US number.
- Date of birth cannot be in the future.
- State names are converted to two-letter abbreviations.
- ZIP codes support 5 digits or ZIP+4.

---

# API Endpoints

## Create Patient

```
POST /patients
```

Example:

```json
{
  "first_name": "Joan",
  "last_name": "Smith",
  "date_of_birth": "2002-01-18",
  "sex": "Decline to Answer",
  "phone_number": "6465557890",
  "address_line_1": "742 Evergreen Terrace",
  "city": "New York",
  "state": "NY",
  "zip_code": "79100"
}
```

## Find Patient By Phone

```
GET /patients/by-phone/{phone_number}
```

Example:

```
GET /patients/by-phone/2125551234
```

---

# Vapi Tools

## find_patient_by_phone

Used to locate existing patients.

Input:

```json
{
  "phone_number": "2125551234"
}
```

## create_patient

Used to create a patient after confirmation.

Flow:

```
Collect details
      |
Read back details
      |
Caller confirms
      |
create_patient
```

---

# Local Setup

## Clone Repository

```bash
git clone <repository-url>
cd patient-registration
```

## Create Virtual Environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Run Application

```bash
uvicorn app.main:app --reload
```

---

# Environment Variables

Create:

```
.env
```

Example:

```env
DATABASE_URL=sqlite:///./patients.db
```

---

# Testing

## Existing Patient

Example:

```
Phone: 2125551234
```

Expected:

```
find_patient_by_phone
        |
Patient found
        |
Continue conversation
```

## New Patient

Example:

```
Phone: 6465557890
```

Expected:

```
find_patient_by_phone
        |
No patient found
        |
Collect information
        |
Confirm information
        |
create_patient
        |
Registration complete
```

---

# Safety Rules

The assistant:
- Never exposes internal tools
- Never creates patients without confirmation
- Never claims appointments are booked without a scheduling system
- Never invents patient information
- Uses only returned API information

---

# Known Limitations

## Appointment Scheduling

The assistant can collect appointment requests and preferences.

Actual scheduling requires a scheduling backend integration.

## Voice Transcription

Spoken phone numbers may occasionally require confirmation due to speech recognition variations.

---

# Future Improvements

- Appointment scheduling integration
- Patient update API
- Appointment availability lookup
- Authentication
- Admin dashboard
- Automated tests
- Multi-language support

---

# Demo Summary

## Existing Patient Flow

```
Caller
 |
Phone lookup
 |
Patient found
 |
Assistance provided
```

## New Patient Flow

```
Caller
 |
Phone lookup
 |
No record found
 |
Collect information
 |
Confirmation
 |
Create patient
 |
Registration complete
```

---