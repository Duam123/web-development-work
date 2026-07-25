from datetime import datetime, date as date_cls, timedelta

from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from extensions import db
from models import DoctorProfile, Appointment, APPT_PENDING, APPT_CANCELLED
from utils import role_required, generate_available_slots, is_slot_still_free

patient_bp = Blueprint("patient", __name__, url_prefix="/patient")


@patient_bp.route("/dashboard")
@login_required
@role_required("patient")
def dashboard():
    upcoming = (
        Appointment.query.filter(
            Appointment.patient_id == current_user.id,
            Appointment.date >= date_cls.today(),
            Appointment.status != APPT_CANCELLED,
        )
        .order_by(Appointment.date, Appointment.start_time)
        .limit(5)
        .all()
    )
    total_appointments = Appointment.query.filter_by(patient_id=current_user.id).count()
    return render_template(
        "patient/dashboard.html", upcoming=upcoming, total_appointments=total_appointments
    )


@patient_bp.route("/doctors")
@login_required
@role_required("patient")
def search_doctors():
    specialty = request.args.get("specialty", "").strip()
    city = request.args.get("city", "").strip()

    query = DoctorProfile.query.filter_by(verified=True)
    if specialty:
        query = query.filter(DoctorProfile.specialty.ilike(f"%{specialty}%"))
    if city:
        query = query.filter(DoctorProfile.city.ilike(f"%{city}%"))

    doctors = query.order_by(DoctorProfile.rating.desc()).all()
    specialties = [
        s[0] for s in db.session.query(DoctorProfile.specialty).distinct().all() if s[0]
    ]

    return render_template(
        "patient/search_doctors.html",
        doctors=doctors,
        specialties=specialties,
        current_specialty=specialty,
        current_city=city,
    )


@patient_bp.route("/doctors/<int:doctor_id>/book", methods=["GET", "POST"])
@login_required
@role_required("patient")
def book_appointment(doctor_id):
    doctor = DoctorProfile.query.get_or_404(doctor_id)

    selected_date_str = request.values.get("date", "")
    try:
        selected_date = (
            datetime.strptime(selected_date_str, "%Y-%m-%d").date()
            if selected_date_str
            else date_cls.today()
        )
    except ValueError:
        selected_date = date_cls.today()

    if request.method == "POST":
        start_time_str = request.form.get("start_time")
        mode = request.form.get("mode", "physical")
        reason = request.form.get("reason", "").strip()

        slots = generate_available_slots(doctor.id, selected_date)
        slot_map = {s.strftime("%H:%M"): e for s, e in slots}

        if start_time_str not in slot_map:
            flash("That slot is no longer available. Please pick another time.", "danger")
            return redirect(url_for("patient.book_appointment", doctor_id=doctor.id, date=selected_date_str))

        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        end_time = slot_map[start_time_str]

        if not is_slot_still_free(doctor.id, selected_date, start_time):
            flash("Someone just booked that slot. Please pick another time.", "danger")
            return redirect(url_for("patient.book_appointment", doctor_id=doctor.id, date=selected_date_str))

        appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=doctor.id,
            date=selected_date,
            start_time=start_time,
            end_time=end_time,
            mode=mode,
            status=APPT_PENDING,
            reason=reason,
        )
        db.session.add(appointment)
        db.session.commit()
        flash("Appointment requested! The doctor will confirm it shortly.", "success")
        return redirect(url_for("patient.my_appointments"))

    slots = generate_available_slots(doctor.id, selected_date)
    date_options = [date_cls.today() + timedelta(days=i) for i in range(14)]

    return render_template(
        "patient/book_appointment.html",
        doctor=doctor,
        slots=slots,
        selected_date=selected_date,
        date_options=date_options,
    )


@patient_bp.route("/appointments")
@login_required
@role_required("patient")
def my_appointments():
    appointments = (
        Appointment.query.filter_by(patient_id=current_user.id)
        .order_by(Appointment.date.desc(), Appointment.start_time.desc())
        .all()
    )
    return render_template("patient/my_appointments.html", appointments=appointments)


@patient_bp.route("/appointments/<int:appointment_id>/cancel", methods=["POST"])
@login_required
@role_required("patient")
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.patient_id != current_user.id:
        flash("You can only cancel your own appointments.", "danger")
        return redirect(url_for("patient.my_appointments"))

    appointment.status = APPT_CANCELLED
    db.session.commit()
    flash("Appointment cancelled.", "info")
    return redirect(url_for("patient.my_appointments"))
