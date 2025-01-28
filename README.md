# EA_Server
Flask File Upload and Row Validation Service
This project provides a Flask-based REST API for handling CSV file uploads, validating row counts, and managing client-specific directories. The API is designed to work with a system that uploads trade transaction files from MQL5 clients.

Features
File Upload and Management:

Files are uploaded to client-specific folders based on the clientID.
The system checks if a file already exists for the client and compares its row count to the given rowSystem.
Row Count Validation:

If the row count of the uploaded file matches the existing file, no changes are made.
If the row counts differ, the new file replaces the existing one.
RESTful Endpoints:

The service provides endpoints for uploading files, checking file status, and validating file data.
Requirements
Server Environment
Python: Version 3.8 or higher
Flask: A Python web framework
Pandas: For reading and validating CSV files
Dependencies
Install the required packages using pip:

bash
Copy
Edit
pip install flask pandas
API Endpoints
1. Root Endpoint
