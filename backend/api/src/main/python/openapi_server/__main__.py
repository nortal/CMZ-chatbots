#!/usr/bin/env python3

import connexion
from flask_cors import CORS
from flask import jsonify
from werkzeug.exceptions import NotFound, InternalServerError

from openapi_server import encoder


def main():
    app = connexion.App(__name__, specification_dir='./openapi/')
    app.app.json_encoder = encoder.JSONEncoder

    # Enable CORS for all routes
    CORS(app.app, resources={r"/*": {"origins": "*"}})

    # Add custom error handlers for consistent error schema (PR003946-90)
    @app.app.errorhandler(404)
    def handle_404(e):
        from openapi_server.models.error import Error
        error = Error(
            code="not_found",
            message="The requested resource was not found",
            details={"path": str(e) if e else "Unknown path"}
        )
        response = jsonify(error.to_dict())
        response.status_code = 404
        return response

    @app.app.errorhandler(400)
    def handle_400(e):
        from openapi_server.models.error import Error
        # Extract detail from the exception if it's a BadRequest
        message = "Bad request"
        details = {}
        if hasattr(e, 'description'):
            message = e.description
        if hasattr(e, 'detail'):
            details = {"validation_error": e.detail}

        error = Error(
            code="bad_request",
            message=message,
            details=details
        )
        response = jsonify(error.to_dict())
        response.status_code = 400
        return response

    @app.app.errorhandler(500)
    def handle_500(e):
        from openapi_server.models.error import Error
        error = Error(
            code="internal_error",
            message="An internal server error occurred",
            details={"error": str(e) if e else "Unknown error"}
        )
        response = jsonify(error.to_dict())
        response.status_code = 500
        return response

    # Custom validation error handler for Connexion
    from connexion.exceptions import BadRequestProblem
    from jsonschema import ValidationError as JsonSchemaValidationError

    @app.app.errorhandler(BadRequestProblem)
    def handle_bad_request_problem(e):
        from openapi_server.models.error import Error
        error = Error(
            code="validation_error",
            message=str(e.detail) if hasattr(e, 'detail') else "Validation failed",
            details={"validation_errors": e.detail if hasattr(e, 'detail') else {}}
        )
        response = jsonify(error.to_dict())
        response.status_code = 400
        return response

    @app.app.errorhandler(JsonSchemaValidationError)
    def handle_json_schema_validation(e):
        from openapi_server.models.error import Error
        error = Error(
            code="validation_error",
            message=e.message,
            details={"validation_path": list(e.path) if e.path else []}
        )
        response = jsonify(error.to_dict())
        response.status_code = 400
        return response

    app.add_api('openapi.yaml',
                arguments={'title': 'CMZ API'},
                pythonic_params=True)

    app.run(port=8080)


if __name__ == '__main__':
    main()
