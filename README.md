## Overview
This Command and Control (C2) framework is designed to remotely execute commands on victim machines, allowing centralized management through a Python Flask server. The framework consists of several key components that work together to facilitate seamless communication, command execution, and data retrieval.
The framework is designed to bypass Antivirus (AV) and Endpoint Detection and Response (EDR) systems.

![DarkControl Architecture Image](https://github.com/HackWidMaddy/DarkControl/blob/main/images/architecture.JPG)

Disclaimer: Purely made for testing and educational purposes. DO NOT run the payloads generated by this tool against hosts that you do not have explicit permission and authorization to test. You are responsible for any trouble you may cause by using this tool.

![Virus Total AV ByPass Image](https://github.com/HackWidMaddy/DarkControl/blob/main/images/virustotal.JPG)

### Components
1. **Python Flask Server**: 
   - **server.py**: Acts as the main control center for the C2 framework. It handles API requests from victim machines, manages sessions, and dispatches commands.
   - **commands.py**: Generates payloads for execution on victim machines and interacts with the Redis queue to manage command execution and results.

2. **PowerShell Script**: 
   - Runs in the background on victim machines.
   - Polls the Flask server at regular intervals (defined by the `$PollingInterval` variable).
   - Executes commands received from the server locally on the victim machine.
   - Sends the execution results back to the Flask server.

3. **Redis**:
   - Used for maintaining a queue for each session.
   - Ensures efficient management and execution of commands.
   - Stores commands temporarily until they are picked up by the victim machines.

4. **SQLite3**:
   - Local database on the Flask server.
   - Stores session data persistently to keep track of active sessions and their states.

### Functionality
- **Initialization**: When the PowerShell script first runs on a victim machine, it sends an initialization request to the Flask server. This registers the session in the SQLite3 database and sets up necessary parameters for subsequent communication.
- **Polling and Command Execution**: The PowerShell script continually polls the Flask server to check if there are any commands to be executed. If commands are found in the Redis queue, they are executed locally on the victim machine, and the results are sent back to the server.
- **Result Handling**: The server processes the results received from the victim machines and updates the session data accordingly.

### Security
- **HTTPS Communication**: All communication between the victim machines and the Flask server is secured using HTTPS with self-signed certificates. This ensures that data transmitted over the network is encrypted, protecting against eavesdropping and man-in-the-middle attacks.

### Modules
The framework includes several built-in modules to perform specific tasks on the victim machines. These modules can be extended or modified to add new functionalities:
- **Browser Module**: Retrieves browser history from the victim machine.
- **Fun Module**: Includes commands to play sounds or open a browser for a Rickroll.
- **Network Module**: Retrieves WLAN profiles along with their passwords and SSIDs from the victim machine.
- **Spy Module**: Captures clipboard data and takes screenshots of the victim machine.

### File Operations
The framework supports file upload and download functionalities, allowing files to be transferred between the server and the victim machines seamlessly.

### Persistence
- **Session Management**: The use of SQLite3 ensures that session data is stored persistently on the server. This allows for the tracking of active sessions and their statuses over time.
- **Command Queue**: Redis provides a robust queuing mechanism for managing and executing commands efficiently, even in scenarios involving multiple victim machines.

![commands.py interface](https://github.com/HackWidMaddy/DarkControl/blob/main/images/interface.JPG)

## Installation

### Prerequisites
- Python 3.x
- Docker

### Steps

1. **Clone the repository**:
    ```bash
    git clone https://github.com/HackWidMaddy/DarkControl.git
    cd DarkControl
    ```

2. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3. **Generate SSL Certificates**:
    Create self-signed SSL certificates for HTTPS communication.
    ```bash
    openssl req -newkey rsa:2048 -nodes -keyout key.pem -x509 -days 365 -out cert.pem
    ```
    Follow the prompts to fill in the certificate details.

4. **Pull and Run Redis with Docker**:
    ```bash
    docker pull redis
    docker run -d -p 6379:6379 redis
    ```

5. **Configure the Application**:
    Edit `config.json` to set your configuration parameters (e.g., server IP, ports, etc.).

6. **Start the Flask Server**:
    ```bash
    python3 c2_server/server.py
    ```
    If there is any port conflict error in server.py, you can change the port number directly in the script.

7. **Start Command Management**:
    ```bash
    python3 c2_server/commands.py
    ```

You should now have the C2 framework up and running. The Flask server will handle incoming requests from victim machines, while the `commands.py` script allows you to manage and dispatch commands.Type help for additional INFO.NOTE: Run server.py and commands.py from outside of c2_server folder

### Contribute

Contributions are welcome! Feel free to fork the repository, make your changes, and submit a pull request.


This comprehensive C2 framework offers a powerful tool for remote administration and monitoring, providing a secure and efficient means to control multiple machines from a centralized server.
