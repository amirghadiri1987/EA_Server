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
[ ] pip install flask pandas
API Endpoints
1. Root Endpoint
URL: /
Method: GET
Response:
Returns a confirmation message for the server's status.

Example Response:
{
    "message": "Hello, World!"
}

2. Process CSV File
URL: /process_csv
Method: POST

Request Parameters:
Form Data:
clientID: Unique identifier for the client (e.g., 1001).
rowSystem: The expected row count for the file.
file: The CSV file to upload.
Logic:
If the file exists and its row count matches rowSystem:
Responds with a success message.
If the file exists but the row count differs:
Uploads the new file and replaces the old one.
If the file does not exist:
Creates the client folder (if necessary) and uploads the file.
Example Request:

curl -X POST http://<server-ip>:5000/process_csv \
-F "clientID=1001" \
-F "rowSystem=250" \
-F "file=@/path/to/Trade_Transaction.csv"

Example Responses:
File Exists and Matches:

{
    "status": "success",
    "message": "File exists and matches rowSystem",
    "rows": 250,
    "path": "/home/amir/w/ServerUpload/1001/Trade_Transaction.csv"
}

File Exists but Mismatch:

{
    "status": "success",
    "message": "File row count mismatch. New file uploaded.",
    "existing_rows": 200,
    "new_rows": 250,
    "path": "/home/amir/w/ServerUpload/1001/Trade_Transaction.csv"
}
File Did Not Exist:

{
    "status": "success",
    "message": "File did not exist. New file uploaded.",
    "new_rows": 250,
    "path": "/home/amir/w/ServerUpload/1001/Trade_Transaction.csv"
}

Folder Structure
The uploaded files are stored under the UPLOAD_FOLDER directory. Each client has a unique folder named after their clientID.

Example Structure:

/home/amir/w/ServerUpload/
├── 1001/
│   └── Trade_Transaction.csv
├── 1002/
│   └── Trade_Transaction.csv
Configuration
The UPLOAD_FOLDER is defined in the Flask app configuration. Update the UPLOAD_FOLDER path as needed:

python
UPLOAD_FOLDER = '/path/to/upload/directory'
Additionally, ensure that the upload directory has appropriate write permissions.

Running the Application
Start the Server: Run the Flask app:

python app.py
Access the API:

The server listens on http://0.0.0.0:5000.
Use tools like Postman or curl to interact with the API.
Deployment
For production environments, consider using a WSGI server like gunicorn or deploying with tools like Docker or NGINX.

Example: Run with gunicorn:


gunicorn --bind 0.0.0.0:5000 app:app
Troubleshooting
File Not Found Errors: Ensure the UPLOAD_FOLDER directory exists and is writable.
Row Count Mismatches: Confirm the file format is a valid CSV and contains no formatting issues.
Future Improvements
Add authentication to restrict access to the API.
Implement detailed logging for file operations.
Add support for additional file formats.

Let me know if you need changes or additions! 😊
