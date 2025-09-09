# routes.py
from resources.patient_resource import patient_bp
from resources.report_resource import report_bp

def register_routes(app):
    app.register_blueprint(patient_bp)
    app.register_blueprint(report_bp)
