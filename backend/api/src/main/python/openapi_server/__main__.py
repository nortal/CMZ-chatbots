#!/usr/bin/env python3

import connexion
from flask_cors import CORS

from openapi_server import encoder
from openapi_server.impl.error_handler import register_error_handlers, register_custom_error_handlers


def main():
    app = connexion.App(__name__, specification_dir='./openapi/')
    app.app.json_encoder = encoder.JSONEncoder
    
    # Enable CORS for frontend integration
    CORS(app.app, origins=['http://localhost:3000'])
    
    # Register consistent error handlers (PR003946-90)
    register_error_handlers(app.app)
    register_custom_error_handlers(app.app)
    
    app.add_api('openapi.yaml',
                arguments={'title': 'CMZ API'},
                pythonic_params=True)
    
    # Register custom problem handler for Connexion validation errors
    from connexion.exceptions import ProblemException
    
    @app.app.errorhandler(ProblemException)
    def handle_connexion_validation_error(error):
        from flask import jsonify
        from openapi_server.models.error import Error
        
        error_obj = Error(
            code="validation_error",
            message="Request validation failed", 
            details={
                "validation_detail": str(error.detail) if hasattr(error, 'detail') else str(error),
                "status": error.status if hasattr(error, 'status') else 400
            }
        )
        return jsonify(error_obj.to_dict()), error.status if hasattr(error, 'status') else 400

    app.run(port=8080)


if __name__ == '__main__':
    main()
