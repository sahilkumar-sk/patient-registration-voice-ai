```markdown
# Patient Registration Voice AI Agent

A voice-powered patient registration and receptionist system built using **FastAPI**, **PostgreSQL**, and **Vapi Voice AI**.

The system provides a natural conversational experience where callers can:

- Register as new patients through a voice conversation
- Look up existing patient records
- Confirm information before saving
- Receive assistance with appointment-related requests
- Provide appointment scheduling preferences

This project demonstrates a complete healthcare voice AI workflow connected to a backend patient management API with persistent storage that survives server restarts and redeploys.

---

# Live Demo

## AI Receptionist Phone Number

Call the AI receptionist:

```
+1 (815) 415 9016
```

Ask for:

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

Health check:

```
GET /health
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
PostgreSQL Database (Render managed instance)
```

**Separation of concerns:**
- **Telephony + LLM behavior** — owned entirely by Vapi (call handling, STT/TTS, conversation flow, tool invocation). The system prompt defines *what* Ava says and *when* she calls tools; Vapi handles *how* the call itself works.
- **Data layer** — SQLAlchemy models (`app/models.py`) define schema and constraints at the database level.
- **API layer** — FastAPI routers (`app/routers/patients.py`) expose REST endpoints; Pydantic schemas (`app/schemas.py`) validate and normalize every input server-side, independent of whatever the voice agent sends.
- **Business logic** — `app/crud.py` isolates database operations from route handling.

This means the voice agent and the REST API both go through the exact same validation and persistence layer — the API is not a thin wrapper that trusts the voice agent's formatting.

---

# Tech Stack & Justification

| Layer | Choice | Why |
|---|---|---|
| Telephony + Voice AI | **Vapi** | Abstracts STT/TTS/telephony entirely, letting development time go into prompt engineering and tool design rather than reimplementing speech infrastructure — the fastest path to a working, natural-sounding agent within a tight time budget. |
| Backend | **FastAPI** | Async-first, built-in request validation via Pydantic, automatic OpenAPI docs (`/docs`), and minimal boilerplate for a small REST surface like this. |
| Validation | **Pydantic field validators** | Centralizes every normalization/validation rule (phone digits, date bounds, state abbreviations, ZIP format) in one place, shared by both the API and any future client — not duplicated in the voice prompt. |
| Database | **PostgreSQL (Render managed)** | Originally built against SQLite for local simplicity, but migrated to managed Postgres for production — see "Known Limitations & Trade-offs" below for why this mattered. |
| Hosting | **Render** | Zero-config deploys from GitHub, free-tier friendly for a take-home assessment, built-in managed Postgres in the same region as the web service. |

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
Patient record found → continue assistance
   OR
No record found → offer new registration
```

## New Patient Registration Flow

```
Caller
 |
States intent to register
 |
Collect required + optional information
 |
Validate information (server-side, via Pydantic)
 |
Read information back
 |
Caller confirms
 |
create_patient
 |
Success → reference ID given
   OR
Failure → exact error relayed, no fabricated success
```

## Duplicate Detection (Bonus)

If a caller tries to register a phone number that's already on file, `create_patient` rejects it server-side. Ava recognizes this specific failure and offers to look up the existing record instead of just relaying a raw error:

> "It looks like you may already be registered with us. Would you like me to look up your existing record instead?"

---

# Features

- Natural, non-IVR conversation flow — one question at a time, allows corrections mid-flow
- Existing patient lookup by phone number
- New patient registration with full field collection
- Server-side validation independent of the voice agent (phone format, DOB bounds, state/ZIP normalization)
- Explicit confirmation read-back before any write
- Deterministic tool-outcome messaging — the caller hears success/failure based on the actual API response, not an LLM guess (see "Known Limitations" for why this was specifically hardened)
- Graceful duplicate-phone handling
- Appointment preference collection (booking itself is out of scope — see below)
- Persistent storage across restarts and redeploys

---

# Appointment Handling

The assistant supports appointment-related requests but does **not** book appointments — this was intentionally out of scope for the assessment window.

Currently supported:

- Collect appointment reason
- Collect current appointment details
- Collect preferred date
- Collect preferred time
- Record scheduling preferences

The assistant never claims an appointment is booked, changed, or confirmed. Example response:

> "I'll note your preferences and the scheduling team can follow up with available options."

---

# Patient Data Model

## Required Fields

| Field | Type | Validation |
|---|---|---|
| first_name | string | 1–50 chars, letters/hyphens/apostrophes |
| last_name | string | 1–50 chars, letters/hyphens/apostrophes |
| date_of_birth | date | Valid date, not in the future, stored as `YYYY-MM-DD` |
| sex | enum | Male, Female, Other, Decline to Answer |
| phone_number | string | Exactly 10 digits (formatting stripped server-side) |
| address_line_1 | string | Street address |
| city | string | 1–100 characters |
| state | string | Valid 2-letter U.S. abbreviation |
| zip_code | string | 5-digit or ZIP+4 |

## Optional Fields

| Field | Type |
|---|---|
| email | string (validated email format) |
| address_line_2 | string |
| insurance_provider | string |
| insurance_member_id | string |
| preferred_language | string (default: "English") |
| emergency_contact_name | string |
| emergency_contact_phone | string (10-digit if provided; empty/omitted is treated as not provided, not invalid) |

## Auto-generated Fields

| Field | Type |
|---|---|
| patient_id | UUID |
| created_at | timestamp (UTC) |
| updated_at | timestamp (UTC) |
| deleted_at | timestamp (UTC, nullable — used for soft delete) |

---

# API Endpoints

All responses use a consistent envelope: `{ "data": {...}, "error": null }` (except `POST /patients`, which returns the created record directly for compatibility with the voice tool's response mapping — see Known Limitations).

| Method | Endpoint | Description |
|---|---|---|
| GET | `/patients` | List all patients. Supports `?last_name=`, `?date_of_birth=`, `?phone_number=` |
| GET | `/patients/{patient_id}` | Retrieve a single patient by UUID |
| GET | `/patients/by-phone/{phone_number}` | Look up a patient by phone number (used by the voice agent) |
| POST | `/patients` | Create a new patient. Rejects duplicate phone numbers with a 400. |
| PUT | `/patients/{patient_id}` | Update an existing patient. Partial updates allowed. |
| DELETE | `/patients/{patient_id}` | Soft-delete (sets `deleted_at`, does not hard-delete) |
| GET | `/health` | Health check |

### Example: Create Patient

```
POST /patients
```

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

### Example: Find Patient By Phone

```
GET /patients/by-phone/8154159016
```

```json
{
  "first_name": "Sahil",
  "last_name": "Kumar",
  "phone_number": "8154159016"
}
```
(Returns `null` if no record matches.)

---

# Vapi Tools

## find_patient_by_phone

- **Method:** GET
- **Path:** `/patients/by-phone/{phone_number}` (bound as a path parameter)
- Called only after the caller confirms their phone number
- Sends a normalized 10-digit string, no formatting characters
- Uses only what the tool returns — never invents patient data

## create_patient

- **Method:** POST
- **Path:** `/patients`
- Called only after all information is read back and the caller explicitly confirms
- Success/failure messaging is handled deterministically at the tool level (Vapi's Request Complete/Request Failed conditions check for `patient_id` vs `error` directly in the response), not left to the LLM to interpret loosely — this was a specific fix made after testing surfaced a mismatch (see Known Limitations)

---

# System Prompt

The full system prompt is included at [`voice/system_prompt.txt`](./voice/system_prompt.txt) (or pasted directly into the Vapi assistant config — see that file for the authoritative version). It is commented by section and covers:

- Call opening and intent identification
- Phone number normalization and confirmation
- Existing-patient lookup, including the distinction between "not found" (normal) and a genuine tool error (needs a retry/fallback)
- Registration field collection and confirmation-before-write
- Explicit instruction to defer to the tool's own success/failure message rather than the model narrating its own outcome
- Duplicate-phone graceful handling
- Appointment scope limits (never claims a booking was made)

---

# Local Development Setup

## Clone Repository

```bash
git clone https://github.com/sahilkumar-sk/patient-registration-voice-ai.git
cd patient-registration-voice-ai
```

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

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | No (defaults to local SQLite) | Postgres connection string in production. Falls back to `sqlite:///./patients.db` if unset, so local dev needs no external database. |

Example `.env` for local development:
```env
DATABASE_URL=sqlite:///./patients.db
```

No API keys are hardcoded anywhere in the codebase — the only secret in play is `DATABASE_URL`, which is set as an environment variable on Render, not committed.

## Run Application

```bash
uvicorn app.main:app --reload
```

API runs locally at:
```
http://127.0.0.1:8000
```

---

# Deployment

- **Backend:** FastAPI app deployed on Render, auto-deploying from GitHub on push to `main`.
- **Database:** Render-managed PostgreSQL instance, same region (Virginia) as the web service for low-latency private networking.
- **Start command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Voice layer:** Vapi assistant configured with `find_patient_by_phone` and `create_patient` as REST tools pointing at the deployed API.

---

# Known Limitations & Trade-offs

This section documents real issues found and fixed during development and testing, in the interest of transparency about the actual engineering process rather than presenting a fictionalized "it just worked" narrative.

**Database engine — SQLite → PostgreSQL migration.**
The system was initially built against local SQLite for simplicity. During testing, this surfaced a real persistence bug: Render's free-tier web service filesystem is ephemeral, so the SQLite file was wiped on every redeploy — meaning a patient registered before a redeploy would silently vanish. This was caught during testing (a caller who had "already registered" got a false "not found"), root-caused to the ephemeral disk, and fixed by migrating to a managed Postgres instance with the connection selected via a `DATABASE_URL` environment variable (falling back to SQLite for local dev, where ephemeral storage isn't an issue). This is the single most important trade-off decision in the project: SQLite was the right shortcut for local development speed, but wrong for the "must survive restarts" requirement in production.

**Tool URL parameter binding.**
An early version of the `find_patient_by_phone` Vapi tool had its path parameter templated incorrectly, causing it to send the literal string `phone_number` instead of the caller's actual digits. This was caught via a repeating, identical validation error across multiple test calls regardless of caller input — diagnosed by comparing backend logs (which showed zero incoming requests matching the caller's real number) against the tool's raw outgoing request, and fixed by correcting the URL template.

**Tool-response message ambiguity.**
Initially, Vapi's Request Complete/Request Failed messages for `create_patient` were left as unconditioned "AI-generated" messages, meaning the LLM had to *infer* success or failure from the raw API response rather than being told deterministically. This caused a real failure mode: a successful `create_patient` call was once narrated by the agent as a failure. Fixed by adding explicit conditions (`patient_id != null` for success, `error != null` for failure) so the spoken outcome is driven directly by the API response shape, not model inference.

**Optional field validation edge case.**
When a caller skipped the optional emergency contact phone field, Vapi sent an empty string rather than omitting the field, which the backend's phone validator incorrectly treated as an invalid (rather than absent) value — blocking the entire registration over a field the caller never intended to provide. Fixed by treating empty strings the same as `null` in the validator.

**No update-flow in the voice agent.**
The bonus "recognize returning caller and offer to update" flow is implemented for phone-number collisions during *registration* (the agent offers to look up the existing record), but the agent does not currently walk a caller through *editing* an existing record's fields over voice — `PUT /patients/{id}` exists and is tested via the API, but isn't wired into a voice conversation flow. This was a scope cut to keep the core registration and lookup flows solid within the time budget.

**No appointment booking.**
As scoped, the agent collects appointment preferences but does not book against any calendar/scheduling system — there is no real scheduling backend to integrate with.

**No automated test suite.**
All verification during development was done via direct `curl` requests against the deployed API and manual end-to-end voice calls, rather than a committed test suite. Given more time, request/response contract tests for each endpoint (particularly around the validation edge cases above) would be the first addition.

**Voice recognition edge cases.**
Spoken digit sequences are occasionally misheard by STT (e.g., digits merged or split unexpectedly). The system prompt handles this by requiring explicit confirmation of the normalized phone number before any lookup or write, and allows the caller to restate it — but a caller providing digits very quickly or with background noise may still need to repeat themselves more than once.

---

# Testing Scenarios

## Scenario 1: Existing Patient Lookup
```
Caller provides a previously registered phone number
→ Phone confirmed
→ find_patient_by_phone called
→ Record found → conversation continues using only returned data
```

## Scenario 2: New Patient Registration
```
Caller states intent to register
→ Required + optional fields collected
→ Information validated server-side
→ Information read back and confirmed
→ create_patient called
→ Deterministic success message with reference ID, or exact failure message if the write fails
```

## Scenario 3: Duplicate Registration
```
Caller attempts to register a phone number already on file
→ create_patient rejects with a 400
→ Agent recognizes the specific failure and offers to look up the existing record instead
```

## Scenario 4: Appointment Request
```
Caller asks to book or reschedule an appointment
→ Reason, current details, preferred date/time collected
→ Agent explicitly states preferences were recorded, never claims a booking was made
```

---

# Safety Rules

The assistant:

- Never exposes internal tools, APIs, or backend systems
- Never invents patient information
- Never creates a patient record without explicit caller confirmation
- Never claims an appointment is scheduled — booking is out of scope
- Uses only verified API responses, never assumes an outcome
- Defers to the tool's own deterministic success/failure signal rather than narrating its own guess at the outcome

---

# Future Improvements

- Voice-driven record update flow (`PUT /patients/{id}` is already implemented on the API side)
- Real appointment scheduling integration
- Multi-language support
- Automated request/response contract tests
- Admin dashboard for viewing registered patients
- Call transcript storage linked to patient records

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
│       └── patients.py
├── voice/
│   └── system_prompt.txt
├── requirements.txt
├── Procfile
├── README.md
└── .env.example
```

---

# Project Summary

This project demonstrates an end-to-end healthcare voice AI receptionist workflow, integrating telephony, an LLM-driven conversational agent, server-side validation, and persistent storage:

```
Caller
 |
 v
Vapi Voice Assistant (Ava)
 |
 v
FastAPI Backend (validation + business logic)
 |
 v
PostgreSQL Database (persistent across restarts/redeploys)
```

The system supports new patient registration, existing patient lookup, safe information confirmation, graceful duplicate handling, and appointment request collection — with the specific bugs found and fixed during development documented above rather than glossed over.
```
