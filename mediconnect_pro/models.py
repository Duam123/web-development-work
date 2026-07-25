from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db

ROLE_PATIENT = "patient"
ROLE_DOCTOR = "doctor"
ROLE_ADMIN = "admin"

APPT_PENDING = "pending"
APPT_CONFIRMED = "confirmed"
APPT_COMPLETED = "completed"
APPT_CANCELLED = "cancelled"

REFERRAL_PENDING = "pending"
REFERRAL_ACCEPTED = "accepted"
REFERRAL_DECLINED = "declined"


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(160), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default=ROLE_PATIENT)
    phone = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    doctor_profile = db.relationship(
        "DoctorProfile", backref="user", uselist=False, cascade="all, delete-orphan"
    )
    patient_profile = db.relationship(
        "PatientProfile", backref="user", uselist=False, cascade="all, delete-orphan"
    )

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def is_patient(self):
        return self.role == ROLE_PATIENT

    def is_doctor(self):
        return self.role == ROLE_DOCTOR

    def is_admin(self):
        return self.role == ROLE_ADMIN

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"


class DoctorProfile(db.Model):
    __tablename__ = "doctor_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    specialty = db.Column(db.String(120), nullable=False, default="General Physician")
    city = db.Column(db.String(120), nullable=False, default="")
    experience_years = db.Column(db.Integer, default=0)
    bio = db.Column(db.Text, default="")
    consultation_fee = db.Column(db.Integer, default=0)
    verified = db.Column(db.Boolean, default=False)
    rating = db.Column(db.Float, default=4.5)

    availability_slots = db.relationship(
        "DoctorAvailability", backref="doctor", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<DoctorProfile {self.user.name if self.user else self.id} - {self.specialty}>"


class PatientProfile(db.Model):
    __tablename__ = "patient_profiles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)

    city = db.Column(db.String(120), default="")
    dob = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(20), default="")


class DoctorAvailability(db.Model):
    """A recurring weekly working window for a doctor.
    weekday: 0=Monday ... 6=Sunday (Python's date.weekday() convention)."""

    __tablename__ = "doctor_availability"

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor_profiles.id"), nullable=False)
    weekday = db.Column(db.Integer, nullable=False)  # 0-6
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    slot_minutes = db.Column(db.Integer, default=30)


class Referral(db.Model):
    """A doctor referring a patient's case to another doctor, plus the
    private case-discussion thread attached to it."""

    __tablename__ = "referrals"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    from_doctor_id = db.Column(db.Integer, db.ForeignKey("doctor_profiles.id"), nullable=False)
    to_doctor_id = db.Column(db.Integer, db.ForeignKey("doctor_profiles.id"), nullable=False)

    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default=REFERRAL_PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("User", foreign_keys=[patient_id])
    from_doctor = db.relationship("DoctorProfile", foreign_keys=[from_doctor_id])
    to_doctor = db.relationship("DoctorProfile", foreign_keys=[to_doctor_id])

    notes = db.relationship(
        "CaseNote", backref="referral", cascade="all, delete-orphan",
        order_by="CaseNote.created_at",
    )


class CaseNote(db.Model):
    """A single message in the private doctor-to-doctor case discussion
    thread attached to a referral."""

    __tablename__ = "case_notes"

    id = db.Column(db.Integer, primary_key=True)
    referral_id = db.Column(db.Integer, db.ForeignKey("referrals.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship("User", foreign_keys=[author_id])


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor_profiles.id"), nullable=False)
    referral_id = db.Column(db.Integer, db.ForeignKey("referrals.id"), nullable=True)

    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    mode = db.Column(db.String(20), default="physical")  # physical | online
    status = db.Column(db.String(20), default=APPT_PENDING)
    reason = db.Column(db.Text, default="")
    prescription = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship("User", foreign_keys=[patient_id])
    doctor = db.relationship("DoctorProfile", foreign_keys=[doctor_id])
    referral = db.relationship("Referral", foreign_keys=[referral_id])

    def __repr__(self):
        return f"<Appointment {self.date} {self.start_time} - {self.status}>"
