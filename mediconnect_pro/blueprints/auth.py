from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models import User, DoctorProfile, PatientProfile, ROLE_PATIENT, ROLE_DOCTOR

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _redirect_to_dashboard(user):
    if user.role == "doctor":
        return redirect(url_for("doctor.dashboard"))
    if user.role == "admin":
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("patient.dashboard"))


@auth_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return _redirect_to_dashboard(current_user)

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", ROLE_PATIENT)
        specialty = request.form.get("specialty", "").strip()
        city = request.form.get("city", "").strip()

        if role not in (ROLE_PATIENT, ROLE_DOCTOR):
            role = ROLE_PATIENT

        if not name or not email or not password:
            flash("Please fill in your name, email, and password.", "danger")
            return render_template("auth/signup.html")

        if User.query.filter_by(email=email).first():
            flash("An account with that email already exists. Please log in instead.", "danger")
            return render_template("auth/signup.html")

        user = User(name=name, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # get user.id before commit

        if role == ROLE_DOCTOR:
            profile = DoctorProfile(
                user_id=user.id,
                specialty=specialty or "General Physician",
                city=city or "",
                verified=False,
            )
            db.session.add(profile)
        else:
            profile = PatientProfile(user_id=user.id, city=city or "")
            db.session.add(profile)

        db.session.commit()
        login_user(user)

        if role == ROLE_DOCTOR:
            flash(
                "Account created! Your profile is pending admin verification, "
                "but you can start setting up your availability now.",
                "success",
            )
        else:
            flash("Welcome to MediConnect Pro!", "success")

        return _redirect_to_dashboard(user)

    return render_template("auth/signup.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return _redirect_to_dashboard(current_user)

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html")

        login_user(user)
        flash(f"Welcome back, {user.name.split(' ')[0]}!", "success")
        return _redirect_to_dashboard(user)

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
