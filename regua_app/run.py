"""Convenience script to run the CRM communication ruler application.

This script imports the application factory from the `regua_app` package
and runs it with debug mode enabled.  Use `python run.py` to start the
development server.  When deploying to production, configure a proper
WSGI server and disable debug.
"""

from regua_app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)