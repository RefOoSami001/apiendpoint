from flask import Flask, request, jsonify
import sqlite3

# Initialize Flask app
app = Flask(__name__)

# Database setup
DATABASE = 'sms.db'

def init_db():
    """Create the database and the SMS table if it doesn't exist."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_number TEXT NOT NULL,
                to_number TEXT NOT NULL,
                message TEXT NOT NULL,
                sms_id TEXT UNIQUE NOT NULL
            )
        ''')
        conn.commit()

def get_db_connection():
    """Create and return a new database connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Allows us to access columns by name
    return conn

@app.before_first_request
def setup():
    """Initialize the database before the first request."""
    init_db()

# Route to handle incoming SMS
@app.route('/receive_sms', methods=['POST'])
def receive_sms():
    # Get data from the POST request
    from_number = request.form.get('from')
    to_number = request.form.get('to')
    message = request.form.get('message')
    sms_id = request.form.get('sms_id')

    # Check if all required fields are present
    if from_number and to_number and message and sms_id:
        # Insert the new SMS into the database
        try:
            with sqlite3.connect(DATABASE) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO sms (from_number, to_number, message, sms_id)
                    VALUES (?, ?, ?, ?)
                ''', (from_number, to_number, message, sms_id))
                conn.commit()
            return jsonify({"message": "Message received and stored in database."}), 200
        except sqlite3.IntegrityError:
            return jsonify({"error": "Error: sms_id must be unique."}), 400
    else:
        return jsonify({"error": "Error: Missing parameters."}), 400

# New endpoint to get SMS records
@app.route('/get_sms', methods=['GET'])
def get_sms():
    """Retrieve all SMS records from the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sms')
        sms_records = cursor.fetchall()

        # Convert records to a list of dictionaries
        sms_list = []
        for record in sms_records:
            sms_list.append({
                "id": record["id"],
                "from_number": record["from_number"],
                "to_number": record["to_number"],
                "message": record["message"],
                "sms_id": record["sms_id"]
            })

    return jsonify(sms_list), 200

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
