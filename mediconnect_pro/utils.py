from datetime import datetime, timedelta, date as date_cls
from functools import wraps

from flask import abort
from flask_login import current_user

from extensions import db
from models import Appointment, DoctorAvailability, APPT_CANCELLED


def role_required(*roles):
    """Decorator restricting a view to one or more user roles."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                abort(403)
            return view_func(*args, **kwargs)

        return wrapped

    return decorator


def generate_available_slots(doctor_id, target_date, booking_window_days=14):
    """Returns a list of (start_time, end_time) datetime.time tuples that are
    still free for a doctor on a given date, based on their weekly
    availability minus any non-cancelled appointments already booked."""

    today = date_cls.today()
    if target_date < today or target_date > today + timedelta(days=booking_window_days):
        return []

    weekday = target_date.weekday()  # 0=Monday
    windows = DoctorAvailability.query.filter_by(doctor_id=doctor_id, weekday=weekday).all()
    if not windows:
        return []

    booked = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == target_date,
        Appointment.status != APPT_CANCELLED,
    ).all()
    booked_starts = {b.start_time for b in booked}

    slots = []
    for window in windows:
        cursor = datetime.combine(target_date, window.start_time)
        window_end = datetime.combine(target_date, window.end_time)
        step = timedelta(minutes=window.slot_minutes or 30)

        while cursor + step <= window_end:
            start_t = cursor.time()
            end_t = (cursor + step).time()
            if start_t not in booked_starts:
                # Don't offer slots that have already passed today.
                if target_date > today or datetime.combine(target_date, start_t) > datetime.now():
                    slots.append((start_t, end_t))
            cursor += step

    return slots


def is_slot_still_free(doctor_id, target_date, start_time):
    existing = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.date == target_date,
        Appointment.start_time == start_time,
        Appointment.status != APPT_CANCELLED,
    ).first()
    return existing is None
