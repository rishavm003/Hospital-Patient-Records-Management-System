"""
Global Error Handler Middleware
"""
from flask import jsonify
from datetime import datetime, timezone


def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({
            'success': False, 'message': 'Bad request', 'statusCode': 400,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({
            'success': False, 'message': 'Unauthorized', 'statusCode': 401,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({
            'success': False, 'message': 'Forbidden', 'statusCode': 403,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({
            'success': False, 'message': 'Resource not found', 'statusCode': 404,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({
            'success': False, 'message': 'Internal server error', 'statusCode': 500,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500
