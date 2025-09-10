#!/usr/bin/env python3

import os
import connexion
from flask_cors import CORS
from connexion.exceptions import BadRequestProblem

from openapi_server import encoder
from openapi_server.impl.error_handler import register_error_handlers, register_custom_error_handlers
from openapi_server.models.error import Error
from flask import jsonify


def main():
    # Set test mode to use mock data instead of AWS
    os.environ['TEST_MODE'] = 'true'
    
    app = connexion.App(__name__, specification_dir='./openapi/')
    app.app.json_encoder = encoder.JSONEncoder
    
    # Enable CORS for frontend integration
    CORS(app.app, origins=['http://localhost:3000'])
    
    app.add_api('openapi.yaml',
                arguments={'title': 'CMZ API'},
                pythonic_params=True,
                strict_validation=True,
                validate_responses=True)

    # Register consistent error handling (PR003946-90)
    register_error_handlers(app.app)
    register_custom_error_handlers(app.app)
    
    # PR003946-84: Register Connexion-specific error handlers for enum validation
    @app.app.errorhandler(BadRequestProblem)
    def handle_connexion_bad_request(error):
        """Handle Connexion BadRequestProblem with consistent Error schema."""
        message = str(error.detail) if hasattr(error, 'detail') else str(error)
        
        # PR003946-84: Detect log level enum validation errors
        if "level" in message and ("not one of" in message.lower() or "'debug', 'info', 'warn', 'error'" in message):
            error_obj = Error(
                code="invalid_log_level",
                message="Invalid log level specified",
                details={
                    "field": "level",
                    "allowed_values": ["debug", "info", "warn", "error"],
                    "error_type": "invalid_log_level"
                }
            )
        else:
            # General validation error
            error_obj = Error(
                code="validation_error",
                message="Request validation failed",
                details={"validation_detail": message}
            )
        
        return jsonify(error_obj.to_dict()), 400

    app.run(port=8080)


if __name__ == '__main__':
    main()
