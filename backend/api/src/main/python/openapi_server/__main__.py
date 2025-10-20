#!/usr/bin/env python3

import connexion
from flask_cors import CORS

from openapi_server import encoder


def main():
    app = connexion.App(__name__, specification_dir='./openapi/')
    app.app.json_encoder = encoder.JSONEncoder

    # Enable CORS for frontend access
    CORS(app.app, resources={
        r"/*": {
            "origins": ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-User-Id"],
            "supports_credentials": True
        }
    })

    app.add_api('openapi.yaml',
                arguments={'title': 'CMZ API'},
                pythonic_params=True)

    app.run(port=8080)


if __name__ == '__main__':
    main()
