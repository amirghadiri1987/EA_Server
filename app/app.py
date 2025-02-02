@app.route("/check_and_upload", methods=["POST"])
def check_and_upload():
    """API endpoint to check if a file needs to be uploaded and process it."""
    client_id = request.form.get("clientID")
    rows_mql5 = request.form.get("rows_count")

    # Validate inputs
    if not client_id or rows_mql5 is None:
        return jsonify({"error": "Missing clientID or rows_count"}), 400

    try:
        rows_mql5 = int(rows_mql5)
    except ValueError:
        return jsonify({"error": "Invalid rows_count"}), 400

    # Create client folder if it doesn't exist
    client_folder = os.path.join(config.UPLOAD_DIR, client_id)
    os.makedirs(client_folder, exist_ok=True)

    # Get the current row count in the database
    rows_db = count_database_rows(client_id)

    # If database exists and row count matches, no need to upload
    if database_exists(client_id) and rows_db == rows_mql5:
        return jsonify({"message": "No need to upload. Data is up-to-date.", "rows": rows_db}), 200

    # Check if a file is provided
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    # Validate file type
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    # Save the file temporarily
    csv_path = os.path.join(client_folder, config.CSV_FILENAME)
    file.save(csv_path)

    # Save CSV data to the database and delete the file
    result = save_csv_to_database(client_id, csv_path)
    if isinstance(result, int):
        return jsonify({"message": "File uploaded, saved to database, and deleted", "rows_saved": result}), 201
    else:
        return jsonify({"error": f"Failed to process file: {result}"}), 500

# Helper function to save CSV data to the database
def save_csv_to_database(client_id, csv_path):
    """Save CSV data to the database and return the number of rows saved."""
    db_path = os.path.join(config.UPLOAD_DIR, client_id, config.DATABASE_FILENAME)

    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(csv_path)

        # Connect to the database and save the DataFrame
        conn = sqlite3.connect(db_path)
        df.to_sql("trades", conn, if_exists="replace", index=False)
        conn.close()

        # Get the number of rows saved
        row_count = len(df)

        # Delete the temporary CSV file
        os.remove(csv_path)
        return row_count
    except Exception as e:
        return str(e)
