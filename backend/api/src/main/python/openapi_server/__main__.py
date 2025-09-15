#!/usr/bin/env python3

import connexion
from connexion.exceptions import ProblemException
from flask import jsonify
from flask_cors import CORS

from openapi_server import encoder
from .impl.error_handler import register_error_handlers, register_custom_error_handlers
from .models.error import Error


def main():
    app = connexion.App(__name__, specification_dir='./openapi/')
    app.app.json_encoder = encoder.JSONEncoder

    # CMZ Template: Auto-enable CORS for local development
    CORS(app.app, origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002"  # Allow common development ports
    ])

    # CMZ API Custom error handler for validation errors
    def handle_connexion_validation_error(exception):
        """Handle Connexion validation errors with our Error schema"""
        if isinstance(exception, ProblemException):
            error_obj = Error(
                code="validation_error",
                message=exception.detail if hasattr(exception, 'detail') else str(exception),
                details={"validation_detail": exception.detail if hasattr(exception, 'detail') else str(exception)}
            )
            return jsonify(error_obj.to_dict()), exception.status
        return exception

    app.add_api('openapi.yaml',
                arguments={'title': 'CMZ API'},
                pythonic_params=True,
                validate_responses=True)

    # Register consistent error schema handlers
    try:
        register_error_handlers(app.app)
        register_custom_error_handlers(app.app)
    except ImportError:
        # Error handlers not yet implemented - this is expected in development
        pass

    # Register Connexion-specific error handler
    app.add_error_handler(ProblemException, handle_connexion_validation_error)

    app.run(port=8080)


if __name__ == '__main__':
    main()