# MediConnect Pro — MVP

A Flask + SQLite web app for multi-specialty doctor collaboration and
appointment booking, covering the three core pillars of the v1 scope:

- **Auth + roles** — Patient / Doctor / Admin, session-based via Flask-Login
- **Appointment booking** — search doctors, real-time slot availability,
  no double-booking, pending → confirmed → completed lifecycle
- **Doctor collaboration/referrals** — a doctor can refer a patient to
  another doctor, with a private doctor-to-doctor case discussion thread
  attached to each referral

## 1. Install

```bash
cd mediconnect_pro
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Seed demo data (recommended for first run)

```bash
python seed.py
```

This creates:

| Role    | Email                          | Password    |
|---------|---------------------------------|-------------|
| Admin   | admin@mediconnect.pro            | admin123    |
| Doctor  | ayesha.raza@mediconnect.pro (Cardiologist) | doctor123 |
| Doctor  | bilal.ahmed@mediconnect.pro (General Physician) | doctor123 |
| Doctor  | sara.khan@mediconnect.pro (Dermatologist) | doctor123 |
| Doctor  | usman.tariq@mediconnect.pro (Neurologist) | doctor123 |
| Patient | ahmed.malik@example.com           | patient123  |
| Patient | fatima.noor@example.com           | patient123  |

All demo doctors are pre-verified and have Mon–Fri availability
(9am–1pm and 5pm–8pm, 30-minute slots) so booking works immediately.

## 3. Run

```bash
python app.py
```

Visit **http://localhost:5000** — you'll land on the login page.

## 4. Try the core flow

1. **Log in as a patient** → *Find a Doctor* → filter by specialty/city →
   *Book Appointment* → pick a date and open slot.
2. **Log in as that doctor** → *Appointments* → *Confirm* the request →
   later mark it *Completed* with a prescription.
3. Still as that doctor, open the patient's name (or *Appointments* →
   patient link) to reach their **history page**, and send a **referral**
   to another doctor with a reason.
4. **Log in as the receiving doctor** → *Referrals* → *Accept* → open
   **Case Discussion** to leave private notes only doctors can see.
5. **Log in as admin** to see platform-wide stats and verify/unverify
   doctors.

## Project structure

```
mediconnect_pro/
├── app.py                  # Flask app factory, blueprint registration
├── config.py                # App configuration (SQLite path, etc.)
├── extensions.py             # Shared db / login_manager instances
├── models.py                 # User, DoctorProfile, PatientProfile,
│                              # DoctorAvailability, Appointment,
│                              # Referral, CaseNote
├── utils.py                  # role_required decorator + slot-generation logic
├── seed.py                   # Demo data seeding script
├── requirements.txt
├── blueprints/
│   ├── auth.py               # signup / login / logout
│   ├── patient.py            # dashboard, doctor search, booking, appointments
│   ├── doctor.py             # profile, availability, appointments,
│   │                          # patient history, referrals, case discussion
│   └── admin.py               # dashboard, doctor verification, user list
├── templates/                # Jinja2 + Bootstrap 5 templates
└── static/css/custom.css     # App styling
```

## How key pieces work

- **Slot generation** (`utils.generate_available_slots`): a doctor sets
  recurring weekly windows (e.g. "Monday 9am–1pm, 30-min slots"). When a
  patient picks a date, the app expands that window into individual slots
  and removes any that already have a non-cancelled appointment.
- **Referrals & case discussion**: `Referral` links a patient to a
  `from_doctor` and `to_doctor`; `CaseNote` rows are messages in the
  thread attached to that referral, visible only to the two doctors
  involved — this is the "private doctor panel" from the brief.
- **Roles**: `role_required("doctor")` (etc.) in `utils.py` guards every
  route; a logged-in patient can't hit doctor/admin URLs and vice versa.

## What's not in this MVP (next steps)

These were in your full spec but intentionally left out of v1 per your
feature picks — the structure below makes each one a natural add-on:

- AI symptom triage (would slot in as a new blueprint + a `/patient/triage` page)
- Telemedicine chat/video (WebRTC/Agora integration point: `Appointment.mode == "online"`)
- Payments (Stripe/JazzCash/Easypaisa) on top of the appointment lifecycle
- Report/file uploads (patient reports, e-prescription PDF export)
- Notifications (email/SMS) on booking/confirm/referral events
- Swapping SQLite → PostgreSQL is a one-line change in `config.py`
  (`DATABASE_URL` env var), since everything goes through SQLAlchemy ORM.
