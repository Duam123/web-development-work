from datetime import datetime, date as date_cls

from flask import Blueprint, render_template, redirect, url_for, request, flash, abort
from flask_login import login_required, current_user

from extensions import db
from models import (
    User,
    DoctorProfile,
    DoctorAvailability,
    Appointment,
    Referral,
    CaseNote,
    APPT_PENDING,
    APPT_CONFIRMED,
    APPT_COMPLETED,
    APPT_CANCELLED,
    REFERRAL_PENDING,
    REFERRAL_ACCEPTED,
    REFERRAL_DECLINED,
    ROLE_DOCTOR,
)
from utils import role_required

doctor_bp = Blueprint("doctor", __name__, url_prefix="/doctor")

WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def _current_doctor_profile():
    profile = DoctorProfile.query.filter_by(user_id=current_user.id).first()
    if profile is None:
        abort(404)
    return profile


@doctor_bp.route("/dashboard")
@login_required
@role_required("doctor")
def dashboard():
    profile = _current_doctor_profile()
    today = date_cls.today()

    todays_appointments = (
        Appointment.query.filter(
            Appointment.doctor_id == profile.id,
            Appointment.date == today,
            Appointment.status != APPT_CANCELLED,
        )
        .order_by(Appointment.start_time)
        .all()
    )
    pending_count = Appointment.query.filter_by(doctor_id=profile.id, status=APPT_PENDING).count()
    incoming_referrals = Referral.query.filter_by(
        to_doctor_id=profile.id, status=REFERRAL_PENDING
    ).count()

    return render_template(
        "doctor/dashboard.html",
        profile=profile,
        todays_appointments=todays_appointments,
        pending_count=pending_count,
        incoming_referrals=incoming_referrals,
    )


@doctor_bp.route("/profile", methods=["GET", "POST"])
@login_required
@role_required("doctor")
def profile():
    doctor_profile = _current_doctor_profile()

    if request.method == "POST":
        doctor_profile.specialty = request.form.get("specialty", "").strip() or doctor_profile.specialty
        doctor_profile.city = request.form.get("city", "").strip()
        doctor_profile.bio = request.form.get("bio", "").strip()
        try:
            doctor_profile.experience_years = int(request.form.get("experience_years", 0))
        except ValueError:
            doctor_profile.experience_years = 0
        try:
            doctor_profile.consultation_fee = int(request.form.get("consultation_fee", 0))
        except ValueError:
            doctor_profile.consultation_fee = 0

        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("doctor.profile"))

    return render_template("doctor/profile.html", profile=doctor_profile)


@doctor_bp.route("/availability", methods=["GET", "POST"])
@login_required
@role_required("doctor")
def availability():
    doctor_profile = _current_doctor_profile()

    if request.method == "POST":
        weekday = int(request.form.get("weekday"))
        start_time = datetime.strptime(request.form.get("start_time"), "%H:%M").time()
        end_time = datetime.strptime(request.form.get("end_time"), "%H:%M").time()
        slot_minutes = int(request.form.get("slot_minutes", 30))

        if start_time >= end_time:
            flash("End time must be after start time.", "danger")
        else:
            slot = DoctorAvailability(
                doctor_id=doctor_profile.id,
                weekday=weekday,
                start_time=start_time,
                end_time=end_time,
                slot_minutes=slot_minutes,
            )
            db.session.add(slot)
            db.session.commit()
            flash("Availability window added.", "success")
        return redirect(url_for("doctor.availability"))

    windows = (
        DoctorAvailability.query.filter_by(doctor_id=doctor_profile.id)
        .order_by(DoctorAvailability.weekday, DoctorAvailability.start_time)
        .all()
    )
    return render_template(
        "doctor/availability.html", windows=windows, weekday_names=WEEKDAY_NAMES
    )


@doctor_bp.route("/availability/<int:window_id>/delete", methods=["POST"])
@login_required
@role_required("doctor")
def delete_availability(window_id):
    doctor_profile = _current_doctor_profile()
    window = DoctorAvailability.query.get_or_404(window_id)
    if window.doctor_id != doctor_profile.id:
        abort(403)
    db.session.delete(window)
    db.session.commit()
    flash("Availability window removed.", "info")
    return redirect(url_for("doctor.availability"))


@doctor_bp.route("/appointments")
@login_required
@role_required("doctor")
def appointments():
    doctor_profile = _current_doctor_profile()
    status_filter = request.args.get("status", "")

    query = Appointment.query.filter_by(doctor_id=doctor_profile.id)
    if status_filter:
        query = query.filter_by(status=status_filter)

    appts = query.order_by(Appointment.date.desc(), Appointment.start_time.desc()).all()
    return render_template("doctor/appointments.html", appointments=appts, status_filter=status_filter)


@doctor_bp.route("/appointments/<int:appointment_id>/update", methods=["POST"])
@login_required
@role_required("doctor")
def update_appointment(appointment_id):
    doctor_profile = _current_doctor_profile()
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.doctor_id != doctor_profile.id:
        abort(403)

    action = request.form.get("action")
    if action == "confirm":
        appointment.status = APPT_CONFIRMED
        flash("Appointment confirmed.", "success")
    elif action == "reject":
        appointment.status = APPT_CANCELLED
        flash("Appointment rejected.", "info")
    elif action == "complete":
        appointment.status = APPT_COMPLETED
        appointment.prescription = request.form.get("prescription", "").strip()
        flash("Appointment marked complete and prescription saved.", "success")

    db.session.commit()
    return redirect(url_for("doctor.appointments"))


@doctor_bp.route("/patients/<int:patient_id>/history")
@login_required
@role_required("doctor")
def patient_history(patient_id):
    doctor_profile = _current_doctor_profile()
    patient = User.query.get_or_404(patient_id)

    # Only allow viewing history if this doctor has (or had) a real
    # relationship with the patient via an appointment or a referral.
    has_relationship = (
        Appointment.query.filter_by(doctor_id=doctor_profile.id, patient_id=patient_id).first()
        or Referral.query.filter(
            db.or_(
                db.and_(Referral.to_doctor_id == doctor_profile.id, Referral.patient_id == patient_id),
                db.and_(Referral.from_doctor_id == doctor_profile.id, Referral.patient_id == patient_id),
            )
        ).first()
    )
    if not has_relationship:
        abort(403)

    history = (
        Appointment.query.filter_by(patient_id=patient_id)
        .filter(Appointment.status == APPT_COMPLETED)
        .order_by(Appointment.date.desc())
        .all()
    )
    other_doctors = DoctorProfile.query.filter(DoctorProfile.id != doctor_profile.id, DoctorProfile.verified == True).all()  # noqa: E712

    return render_template(
        "doctor/patient_history.html", patient=patient, history=history, other_doctors=other_doctors
    )


@doctor_bp.route("/patients/<int:patient_id>/refer", methods=["POST"])
@login_required
@role_required("doctor")
def refer_patient(patient_id):
    doctor_profile = _current_doctor_profile()
    to_doctor_id = request.form.get("to_doctor_id")
    reason = request.form.get("reason", "").strip()

    if not to_doctor_id or not reason:
        flash("Please choose a doctor and give a reason for the referral.", "danger")
        return redirect(url_for("doctor.patient_history", patient_id=patient_id))

    referral = Referral(
        patient_id=patient_id,
        from_doctor_id=doctor_profile.id,
        to_doctor_id=int(to_doctor_id),
        reason=reason,
        status=REFERRAL_PENDING,
    )
    db.session.add(referral)
    db.session.commit()
    flash("Referral sent. The other doctor will see it in their Referrals tab.", "success")
    return redirect(url_for("doctor.patient_history", patient_id=patient_id))


@doctor_bp.route("/referrals")
@login_required
@role_required("doctor")
def referrals():
    doctor_profile = _current_doctor_profile()
    incoming = (
        Referral.query.filter_by(to_doctor_id=doctor_profile.id)
        .order_by(Referral.created_at.desc())
        .all()
    )
    outgoing = (
        Referral.query.filter_by(from_doctor_id=doctor_profile.id)
        .order_by(Referral.created_at.desc())
        .all()
    )
    return render_template("doctor/referrals.html", incoming=incoming, outgoing=outgoing)


@doctor_bp.route("/referrals/<int:referral_id>/respond", methods=["POST"])
@login_required
@role_required("doctor")
def respond_referral(referral_id):
    doctor_profile = _current_doctor_profile()
    referral = Referral.query.get_or_404(referral_id)
    if referral.to_doctor_id != doctor_profile.id:
        abort(403)

    action = request.form.get("action")
    if action == "accept":
        referral.status = REFERRAL_ACCEPTED
        flash("Referral accepted. You can now book an appointment with this patient.", "success")
    elif action == "decline":
        referral.status = REFERRAL_DECLINED
        flash("Referral declined.", "info")

    db.session.commit()
    return redirect(url_for("doctor.case_thread", referral_id=referral.id))


@doctor_bp.route("/referrals/<int:referral_id>/case", methods=["GET", "POST"])
@login_required
@role_required("doctor")
def case_thread(referral_id):
    doctor_profile = _current_doctor_profile()
    referral = Referral.query.get_or_404(referral_id)

    if doctor_profile.id not in (referral.from_doctor_id, referral.to_doctor_id):
        abort(403)

    if request.method == "POST":
        message = request.form.get("message", "").strip()
        if message:
            note = CaseNote(referral_id=referral.id, author_id=current_user.id, message=message)
            db.session.add(note)
            db.session.commit()
        return redirect(url_for("doctor.case_thread", referral_id=referral.id))

    return render_template("doctor/case_thread.html", referral=referral)
