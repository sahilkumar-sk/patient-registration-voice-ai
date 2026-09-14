# Patient Registration Voice AI Agent

A voice-powered patient registration receptionist system built using **FastAPI**, **SQLite**, and **Vapi Voice AI**.

The system provides a natural voice interaction experience where callers can:
- Register as new patients
- Look up existing patient records
- Confirm and validate information before saving
- Receive assistance with appointment-related requests

The goal of this project is to demonstrate a complete voice AI workflow connected to a backend patient management API.

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

## High-Level Flow

### Existing Patient Flow

```
Caller
  |
Provides phone number
  |
Patient lookup
  |
Existing record found
  |
Continue assistance
```

### New Patient Registration Flow

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
Read information back
  |
Caller confirms
  |
Create patient record
  |
Registration completed
```

---

# Features

## Voice Receptionist

The AI receptionist can:

- Greet callers naturally
- Understand caller intent
- Collect patient information
- Search existing patients
- Register new patients
- Handle corrections during registration
- Confirm information before saving

---

## Existing Patient Lookup

The assistant can identify existing patients using their registered phone number.

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

---

## New Patient Registration

New patients are only created after:

1. Required information is collected
2. Information is read back to the caller
3. Caller explicitly confirms

This prevents accidental or incorrect registrations.

---

# Technology Stack

## Voice Layer

**Vapi Voice AI**

Used for:
- Voice conversations
- Assistant behavior
- Tool execution
- Natural language interaction

---

## Backend

**FastAPI**

Used for:
- REST API endpoints
- Request validation
- Business logic
- Patient management

---

## Database

**SQLite**

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
| state | US state abbreviation |
| zip_code | ZIP code |

---

## Optional Fields

| Field | Description |
|---|---|
| email | Email address |
| address_line_2 | Additional address information |
| insurance_provider | Insurance provider |
| insurance_member_id | Insurance member ID |
| preferred_language | Preferred language |
| emergency_contact_name | Emergency contact name |
| emergency_contact_phone | Emergency contact phone |

---

# Validation Rules

The backend validates:

## Phone Number

- Must contain a valid 10-digit US phone number

Example:

```
2125551234
```

---

## Date of Birth

- Must be a valid date
- Cannot be in the future

---

## State

State names are normalized into two-letter abbreviations.

Example:

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
  "sex": "Decline to Answer",
  "phone_number": "6465557890",
  "address_line_1": "742 Evergreen Terrace",
  "city": "New York",
  "state": "NY",
  "zip_code": "79100"
}
```

---

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

Purpose:

Find an existing patient using their phone number.

Input:

```json
{
  "phone_number": "2125551234"
}
```

---

## create_patient

Purpose:

Create a new patient after caller confirmation.

The assistant follows this flow:

```
Collect information
        |
Read information back
        |
Caller confirms
        |
create_patient tool
        |
Patient created
```

---

# Local Development Setup

## 1. Clone Repository

Clone this GitHub repository and enter the project directory:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd patient-registration
```

---

## 2. Create Virtual Environment

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

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables

Create:

```
.env
```

Example:

```env
DATABASE_URL=sqlite:///./patients.db
```

---

## 5. Run Application

```bash
uvicorn app.main:app --reload
```

The API will start locally:

```
http://127.0.0.1:8000
```

---

# Testing Scenarios

## Scenario 1: Existing Patient

Example:

```
Phone:
2125551234
```

Expected flow:

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
Phone:
6465557890
```

Expected flow:

```
Phone lookup
      |
No patient found
      |
Collect information
      |
Confirm information
      |
Create patient
      |
Registration completed
```

---

# Assistant Safety Rules

The assistant:

- Never exposes internal tools
- Never creates patients without confirmation
- Never invents patient information
- Never claims appointments are booked without scheduling integration
- Uses only verified API responses

---

# Known Limitations

## Appointment Scheduling

The assistant currently collects appointment requests and preferences.

Actual appointment booking requires a scheduling backend integration.

---

## Voice Recognition

Voice transcription can occasionally misinterpret spoken digits.

The assistant handles this by:
- Normalizing phone numbers
- Asking for confirmation
- Allowing corrections

---

# Future Improvements

Possible improvements:

- Appointment scheduling integration
- Patient update API
- Appointment availability lookup
- Authentication
- Admin dashboard
- Automated test coverage
- Multi-language support

---

# Project Summary

This project demonstrates an end-to-end voice AI healthcare receptionist workflow:

```
Voice Caller
     |
     v
Vapi Assistant
     |
     v
FastAPI Backend
     |
     v
SQLite Database
```

The system supports both:
- Existing patient assistance
- New patient registration

---

# Author

Built as part of the Patient Registration Voice AI Coding Challenge.