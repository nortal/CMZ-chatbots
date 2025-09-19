#!/usr/bin/env python3

import connexion
from flask_cors import CORS

from openapi_server import encoder


def main():
    app = connexion.App(__name__, specification_dir='./openapi/')
    app.app.json_encoder = encoder.JSONEncoder

    # Enable CORS for frontend development with full configuration
    CORS(app.app,
         origins=["http://localhost:3000", "http://localhost:3001"],
         allow_headers=["Content-Type", "Authorization", "X-User-Id"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
         expose_headers=["Content-Type", "X-User-Id"])

    app.add_api('openapi.yaml',
                arguments={'title': 'CMZ API'},
                pythonic_params=True)

    app.run(port=8080)


if __name__ == '__main__':
    main()
