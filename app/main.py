import os
import shutil
import csv
import sqlite3
import pandas as pd
import config
import logging
from flask import Flask, flash, request, jsonify, Response, redirect, url_for, session, abort
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user 
from werkzeug.utils import secure_filename
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from redis import Redis
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

limiter = Limiter(
    get_remote_address,
    app=app,
    storage_uri="redis://localhost:6379"
)
UPLOAD_FOLDER = config.UPLOAD_DIR
ALLOWED_EXTENSIONS = config.allowed_extensions
CALL_BACK_TOKEN = config.call_back_token
CALL_BACK_TOKEN_ADMIN = config.call_back_token_admin
CALL_BACK_TOKEN_CHECK_SERVER = config.call_back_token_check_server
CALL_BACK_TOKEN_SYNC = config.call_back_token_sync
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# 9

# flask-login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# config
app.config.update(
    SECRET_KEY = config.SECRET_KEY
)
# silly user model
class User(UserMixin):

    def __init__(self, id):
        self.id = id
        
        
    def __repr__(self):
        return "%d" % (self.id)


# create some users with ids 1 to 20       
user = User(0)


# some protected url
@app.route('/')
@login_required
def home():
    return Response("Hello World in the page!")


# somewhere to login
@app.route(f'/{CALL_BACK_TOKEN_ADMIN}/login', methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST': #TODO: stop the brute force
        username = request.form['username']
        password = request.form['password']        
        if password == config.PASSWORD and username == config.USERNAME:
            login_user(user)
            return redirect('/') 
        else:
            return abort(401)
    else:
        return Response('''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=password name=password>
            <p><input type=submit value=Login>
        </form>
        ''')


# somewhere to logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return Response('<p>Logged out</p>')


# handle login failed
@app.errorhandler(401)
def page_not_found(error):
    return Response('<p>Login failed</p>')
    
    
# callback to reload the user object        
@login_manager.user_loader
def load_user(userid):
    return User(userid)













# TODO some health check url
# ✅
@app.route(f'/{CALL_BACK_TOKEN_CHECK_SERVER}/v1/ok')
def health_check():
    response_data = {"status": "success", "message": "Server is running"}
    return jsonify(response_data), 200

# TODO Fix simple welcome page 
@app.route("/chck")
@limiter.limit("5 per minute")
def hello_world():
    print("Configured upload folder:", config.UPLOAD_DIR)
    return "<p>Hello, World!</p>"











# TODO Test function check_row_count in mql5
#  Expose check_row_count as API
# @app.route("/count_database_rows", methods=["GET"])
def count_database_rows(client_id):
    """Count the number of rows in the 'trades' table for a given client."""
    db_path = os.path.join(config.UPLOAD_DIR, client_id, config.DATABASE_FILENAME)
    
    if not os.path.exists(db_path):
        return 0
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM trades")
            row_count = cursor.fetchone()[0]
        return row_count
    except sqlite3.Error:
        # Handle database errors (e.g., table doesn't exist)
        return 0
    

def allowed_file(filename):
    """Check if file has allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in config.allowed_extensions


# Function to check if the database exists
def database_exists(client_id):
    db_path = os.path.join(config.UPLOAD_DIR, client_id, config.DATABASE_FILENAME)
    return os.path.exists(db_path)


# TODO Test function check_and_upload_file in mql5
#  Expose check_and_upload_file as API
@app.route(f'/{CALL_BACK_TOKEN}/check_and_upload', methods=["POST"])
def check_and_upload():
    """API endpoint to check if a file needs to be uploaded and process it."""
    # Ensure the request method is POST
    if request.method != "POST":
        return jsonify({"error": "Method not allowed. Use POST."}), 405

    # Extract clientID and rows_count from the request
    client_id = request.form.get("clientID")
    rows_mql5 = request.form.get("rows_count")

    # Validate inputs
    if not client_id or rows_mql5 is None:
        return jsonify({"error": "Missing clientID or rows_count"}), 400

    try:
        rows_mql5 = int(rows_mql5)
    except ValueError:
        return jsonify({"error": "Invalid rows_count. Must be an integer."}), 400

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
    try:
        file.save(csv_path)
    except Exception as e:
        return jsonify({"error": f"Failed to save file: {str(e)}"}), 500

    # Save CSV data to the database and delete the file
    try:
        result = save_csv_to_database(client_id, csv_path)
        if isinstance(result, int):
            return jsonify({"message": "File uploaded, saved to database, and deleted", "rows_saved": result}), 201
        else:
            return jsonify({"error": f"Failed to process file: {result}"}), 500
    finally:
        # Ensure the temporary file is deleted
        if os.path.exists(csv_path):
            os.remove(csv_path)

    






    # TODO Test function transfer_to_database in mql5


#  Expose transfer_to_database as API
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
    




    # TODO Test function upload_transaction_to_db in mql5
#  Expose upload_transaction_to_db as API
@app.route("/upload_transaction", methods=["POST"])
def upload_transaction_to_db():
    transaction_data = request.json
    if not transaction_data:
        return jsonify({"error": "Missing transaction data"}), 400

    conn = sqlite3.connect(config.database_file_path)
    cur = conn.cursor()

    cur.execute('''INSERT INTO Trade_Transaction 
        (open_time, symbol, magic_number, type, volume, open_price, sl, tp, close_price, close_time, commission, swap, profit, profit_points, duration, open_comment, close_comment)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
        (transaction_data['Open Time'], transaction_data['Symbol'], transaction_data['Magic Number'], 
         transaction_data['Type'], transaction_data['Volume'], transaction_data['Open Price'], 
         transaction_data['S/L'], transaction_data['T/P'], transaction_data['Close Price'], 
         transaction_data['Close Time'], transaction_data['Commission'], transaction_data['Swap'], 
         transaction_data['Profit'], transaction_data['Profit Points'], transaction_data['Duration'], 
         transaction_data['Open Comment'], transaction_data['Close Comment']))

    conn.commit()
    conn.close()
    return jsonify({"message": "Transaction uploaded successfully"}), 200




# Upload a single transaction (when a transaction is completed)
transaction_data = {
    'Open Time': '2025.01.08 08:08:15',
    'Symbol': 'BTCUSD.',
    'Magic Number': 11085,
    'Type': 'buy',
    'Volume': 0.01,
    'Open Price': 96501.4,
    'S/L': None,
    'T/P': None,
    'Close Price': 96491.3,
    'Close Time': '2025.01.08 08:10:04',
    'Commission': -0.78,
    'Swap': 0,
    'Profit': -0.1,
    'Profit Points': -1010,
    'Duration': '0:01:49',
    'Open Comment': 'Break EA 651',
    'Close Comment': ''
}



def create_filtered_database(client_id, magic_number):
    """
    Creates a filtered database based on the Magic_Number.
    """
    # Paths to the original and filtered databases
    original_db_path = os.path.join(config.UPLOAD_DIR, client_id, config.DATABASE_FILENAME)
    filtered_db_path = os.path.join(config.UPLOAD_DIR, client_id, f"filtered_{magic_number}.db")

    # Check if the filtered database already exists
    if os.path.exists(filtered_db_path):
        logger.info(f"Filtered database for Magic_Number {magic_number} already exists.")
        return filtered_db_path

    # Connect to the original database
    try:
        with sqlite3.connect(original_db_path) as conn:
            query = f"SELECT * FROM trades WHERE Magic_Number = {magic_number}"
            df = pd.read_sql_query(query, conn)
    except sqlite3.Error as e:
        logger.error(f"Error reading from the original database: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None

    # Save the filtered data to the new database
    try:
        with sqlite3.connect(filtered_db_path) as conn:
            df.to_sql("filtered_trades", conn, if_exists="replace", index=False)
        logger.info(f"Filtered database created for Magic_Number {magic_number}.")
        return filtered_db_path
    except sqlite3.Error as e:
        logger.error(f"Error creating the filtered database: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None


def calculate_outputs(filtered_db_path):
    """
    Calculates the required outputs from the filtered database.
    """
    try:
        with sqlite3.connect(filtered_db_path) as conn:
            query = "SELECT * FROM filtered_trades"
            df = pd.read_sql_query(query, conn)
    except sqlite3.Error as e:
        logger.error(f"Error reading from the filtered database: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None

    # Calculate outputs
    try:
        winning_trades, win_percentage = calculate_trades_won_percentage(df["Profit"])
        outputs = {
            "Most_Volume": float(df["Volume"].max()),  # Convert to float
            "First_Open_Time": str(df["Open_Time"].min()),  # Convert to string
            "Last_Close_Time": str(df["Close_Time"].max()),  # Convert to string
            "Total_Profit": float(df["Profit"].sum()),  # Convert to float
            "Drawdown": float(calculate_drawdown(df["Profit"])),  # Convert to float
            "Profit_Factor": float(calculate_profit_factor(df["Profit"])),  # Convert to float
            "Trades_Won": int(winning_trades),  # Convert to int
            "Trades_Won_Percentage": float(win_percentage),  # Convert to float
            "Expected_Payoff": float(calculate_expected_payoff(df["Profit"]))  # Convert to float
        }
        return outputs
    except Exception as e:
        logger.error(f"Error calculating outputs: {e}")
        return None


def calculate_drawdown(profit_series):
    """
    Calculate the maximum drawdown from a series of profits.
    """
    import pandas as pd

    # Convert the profit series to a pandas Series if it's not already
    if not isinstance(profit_series, pd.Series):
        profit_series = pd.Series(profit_series)

    # Add a row for the initial state (before the first trade)
    profit_series = pd.concat([pd.Series([0]), profit_series], ignore_index=True)

    # Calculate cumulative profit (starting from 0)
    cumulative_profit = profit_series.cumsum()

    # Calculate maximum cumulative profit
    max_cumulative_profit = cumulative_profit.cummax()

    # Calculate drawdown
    drawdown = max_cumulative_profit - cumulative_profit

    # Calculate maximum drawdown
    max_drawdown = drawdown.max()

    return max_drawdown


def calculate_profit_factor(profit_series):
    """
    Calculates the profit factor (Gross Profit / Gross Loss).
    """
    gross_profit = profit_series[profit_series > 0].sum()
    gross_loss = abs(profit_series[profit_series < 0].sum())
    return gross_profit / gross_loss if gross_loss != 0 else 0


def calculate_trades_won_percentage(profit_series):
    """
    Calculates the percentage of winning trades and the number of winning trades.
    """
    # Count the number of winning trades (Profit > 0)
    winning_trades = profit_series[profit_series > 0].count()
    
    # Total number of trades
    total_trades = profit_series.count()
    
    # Calculate the percentage of winning trades
    if total_trades > 0:
        win_percentage = (winning_trades / total_trades) * 100
    else:
        win_percentage = 0
    
    return winning_trades, win_percentage


def calculate_expected_payoff(profit_series):
    """
    Calculates the expected payoff (Average profit per trade).
    """
    return profit_series.mean()


def get_filtered_outputs(client_id, magic_number):
    """
    Main function to get the filtered outputs.
    """
    # Step 1: Create or check the filtered database
    filtered_db_path = create_filtered_database(client_id, magic_number)
    if not filtered_db_path:
        return {"error": "Failed to create or access the filtered database."}

    # Step 2: Calculate the outputs
    outputs = calculate_outputs(filtered_db_path)
    if not outputs:
        return {"error": "Failed to calculate outputs."}

    return outputs


@app.route(f'/{CALL_BACK_TOKEN_SYNC}/get_filtered_outputs', methods=["GET"])
def api_get_filtered_outputs():
    client_id = request.args.get("client_id")
    magic_number = request.args.get("magic_number")

    if not client_id or not magic_number:
        return jsonify({"error": "Missing client_id or magic_number"}), 400

    try:
        magic_number = int(magic_number)
    except ValueError:
        return jsonify({"error": "Invalid magic_number. Must be an integer."}), 400

    outputs = get_filtered_outputs(client_id, magic_number)
    if "error" in outputs:
        return jsonify(outputs), 500

    return jsonify(outputs), 200




if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
