"""
seed.py - populates the database with a demo admin, doctors, patients,
and doctor availability so the app is immediately usable after setup.

Run with:  python seed.py
"""

from datetime import time

from app import create_app
from extensions import db
from models import User, DoctorProfile, PatientProfile, DoctorAvailability, ROLE_ADMIN, ROLE_DOCTOR, ROLE_PATIENT

app = create_app()


def get_or_create_user(name, email, password, role):
    user = User.query.filter_by(email=email).first()
    if user:
        return user
    user = User(name=name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    return user


def seed():
    with app.app_context():
        # ---- Admin ----
        admin = get_or_create_user("System Admin", "admin@mediconnect.pro", "admin123", ROLE_ADMIN)

        # ---- Doctors ----
        doctors_data = [
            ("Dr. Ayesha Raza", "ayesha.raza@mediconnect.pro", "Cardiologist", "Karachi", 12),
            ("Dr. Bilal Ahmed", "bilal.ahmed@mediconnect.pro", "General Physician", "Karachi", 6),
            ("Dr. Sara Khan", "sara.khan@mediconnect.pro", "Dermatologist", "Lahore", 9),
            ("Dr. Usman Tariq", "usman.tariq@mediconnect.pro", "Neurologist", "Islamabad", 15),
        ]

        doctor_profiles = []
        for name, email, specialty, city, years in doctors_data:
            user = get_or_create_user(name, email, "doctor123", ROLE_DOCTOR)
            profile = DoctorProfile.query.filter_by(user_id=user.id).first()
            if profile is None:
                profile = DoctorProfile(
                    user_id=user.id,
                    specialty=specialty,
                    city=city,
                    experience_years=years,
                    bio=f"{name} is a verified {specialty.lower()} with {years} years of experience.",
                    consultation_fee=1500 + years * 100,
                    verified=True,
                    rating=4.6,
                )
                db.session.add(profile)
                db.session.flush()
            doctor_profiles.append(profile)

        db.session.commit()

        # ---- Availability: Mon-Fri 9am-1pm and 5pm-8pm, 30 min slots ----
        for profile in doctor_profiles:
            if DoctorAvailability.query.filter_by(doctor_id=profile.id).first():
                continue
            for weekday in range(0, 5):  # Monday..Friday
                db.session.add(
                    DoctorAvailability(
                        doctor_id=profile.id,
                        weekday=weekday,
                        start_time=time(9, 0),
                        end_time=time(13, 0),
                        slot_minutes=30,
                    )
                )
                db.session.add(
                    DoctorAvailability(
                        doctor_id=profile.id,
                        weekday=weekday,
                        start_time=time(17, 0),
                        end_time=time(20, 0),
                        slot_minutes=30,
                    )
                )
        db.session.commit()

        # ---- Patients ----
        patients_data = [
            ("Ahmed Malik", "ahmed.malik@example.com", "Karachi"),
            ("Fatima Noor", "fatima.noor@example.com", "Lahore"),
        ]
        for name, email, city in patients_data:
            user = get_or_create_user(name, email, "patient123", ROLE_PATIENT)
            if PatientProfile.query.filter_by(user_id=user.id).first() is None:
                db.session.add(PatientProfile(user_id=user.id, city=city))
        db.session.commit()

        print("Seed complete.\n")
        print("Login credentials:")
        print("  Admin:    admin@mediconnect.pro / admin123")
        print("  Doctor:   ayesha.raza@mediconnect.pro / doctor123  (also bilal.ahmed / sara.khan / usman.tariq)")
        print("  Patient:  ahmed.malik@example.com / patient123  (also fatima.noor)")


if __name__ == "__main__":
    seed()
