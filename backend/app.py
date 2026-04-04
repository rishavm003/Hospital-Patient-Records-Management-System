"""
Main Flask Application — Hospital Patient Records Management System
"""
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from datetime import timedelta
from config.database import db_config
from config.constants import JWT_ACCESS_TOKEN_EXPIRES
from middleware.error_handler import register_error_handlers
import os


def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-string')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(seconds=JWT_ACCESS_TOKEN_EXPIRES)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)

    # Extensions
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    JWTManager(app)

    # Database
    if not db_config.connect():
        raise Exception("Failed to connect to MongoDB")

    # Register all blueprints
    from routes.auth_routes import auth_bp
    from routes.patient_routes import patient_bp
    from routes.user_routes import user_bp
    from routes.appointment_routes import appointment_bp
    # from routes.medical_record_routes import medical_record_bp
    # from routes.lab_test_routes import lab_test_bp
    # from routes.department_routes import department_bp

    app.register_blueprint(auth_bp,           url_prefix='/api/auth')
    app.register_blueprint(patient_bp,         url_prefix='/api/patients')
    app.register_blueprint(user_bp,            url_prefix='/api/users')
    app.register_blueprint(appointment_bp,     url_prefix='/api/appointments')
    # app.register_blueprint(medical_record_bp,  url_prefix='/api/medical-records')
    # app.register_blueprint(lab_test_bp,        url_prefix='/api/lab-tests')
    # app.register_blueprint(department_bp,      url_prefix='/api/departments')

    # Global error handlers
    register_error_handlers(app)

    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Hospital PRMS API is running', 'version': '1.0.0'}

    @app.route('/')
    def index():
        return {'message': 'Hospital Patient Records Management System API', 'version': '1.0.0'}

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
