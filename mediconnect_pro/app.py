import os
from datetime import date, datetime

from flask import Flask, redirect, url_for
from flask_login import current_user, login_required

from config import Config
from extensions import db, login_manager


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from blueprints.auth import auth_bp
    from blueprints.patient import patient_bp
    from blueprints.doctor import doctor_bp
    from blueprints.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(patient_bp)
    app.register_blueprint(doctor_bp)
    app.register_blueprint(admin_bp)

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            if current_user.role == "doctor":
                return redirect(url_for("doctor.dashboard"))
            if current_user.role == "admin":
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("patient.dashboard"))
        return redirect(url_for("auth.login"))

    @app.template_filter("time12")
    def time12_filter(value):
        if value is None:
            return ""
        return value.strftime("%I:%M %p").lstrip("0")

    @app.template_filter("nice_date")
    def nice_date_filter(value):
        if value is None:
            return ""
        return value.strftime("%a, %d %b %Y")

    @app.context_processor
    def inject_globals():
        return {"today": date.today(), "now": datetime.utcnow()}

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
