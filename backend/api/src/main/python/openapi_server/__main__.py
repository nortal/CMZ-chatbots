#!/usr/bin/env python3

import os
import connexion
from flask_cors import CORS

from openapi_server import encoder
from openapi_server.impl.error_handler import register_error_handlers, register_custom_error_handlers


def main():
    # Set test mode to use mock data instead of AWS
    os.environ['TEST_MODE'] = 'true'
    
    app = connexion.App(__name__, specification_dir='./openapi/')
    app.app.json_encoder = encoder.JSONEncoder
    
    # Enable CORS for frontend integration
    CORS(app.app, origins=['http://localhost:3000'])
    
    app.add_api('openapi.yaml',
                arguments={'title': 'CMZ API'},
                pythonic_params=True)

    # Register consistent error handling (PR003946-90)
    register_error_handlers(app.app)
    register_custom_error_handlers(app.app)

    app.run(port=8080)


if __name__ == '__main__':
    main()
