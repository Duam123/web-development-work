from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required

from extensions import db
from models import User, DoctorProfile, Appointment, Referral, ROLE_DOCTOR, ROLE_PATIENT
from utils import role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    stats = {
        "total_doctors": User.query.filter_by(role=ROLE_DOCTOR).count(),
        "total_patients": User.query.filter_by(role=ROLE_PATIENT).count(),
        "verified_doctors": DoctorProfile.query.filter_by(verified=True).count(),
        "pending_doctors": DoctorProfile.query.filter_by(verified=False).count(),
        "total_appointments": Appointment.query.count(),
        "total_referrals": Referral.query.count(),
    }
    return render_template("admin/dashboard.html", stats=stats)


@admin_bp.route("/doctors")
@login_required
@role_required("admin")
def manage_doctors():
    doctors = DoctorProfile.query.order_by(DoctorProfile.verified, DoctorProfile.id.desc()).all()
    return render_template("admin/doctors.html", doctors=doctors)


@admin_bp.route("/doctors/<int:doctor_id>/toggle-verify", methods=["POST"])
@login_required
@role_required("admin")
def toggle_verify(doctor_id):
    doctor = DoctorProfile.query.get_or_404(doctor_id)
    doctor.verified = not doctor.verified
    db.session.commit()
    flash(
        f"{doctor.user.name} is now {'verified' if doctor.verified else 'unverified'}.",
        "success",
    )
    return redirect(url_for("admin.manage_doctors"))


@admin_bp.route("/users")
@login_required
@role_required("admin")
def manage_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users)
