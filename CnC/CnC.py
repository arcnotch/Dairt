from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import urllib.request
import os
import json
import sys

hostName = "A" #ip
hostPort = 0 #443
UUID = ''
Commands=[]

scriptDir = os.getcwd()

def ConfigurationServer():
    with open('configuration.json') as f:
        confFileJson = json.load(f)

        global hostName
        global hostPort
        global UUID
        global Commands
        global File

        hostName = confFileJson['Server']
        hostPort = confFileJson['Port']
        UUID = confFileJson['UUID']
        File = confFileJson['File']

        f = open('commands.txt', 'r')
        Commands = f.read().splitlines()
        f.close()
        #Commands = confFileJson['Commands']

class MyServer(BaseHTTPRequestHandler):
    #GET Requests
    def do_GET(self):
        #Checks if the UUID is match (Kind of authentication)
        if (self.headers.get('UUID') == UUID):
            #Client asked for configuration
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

    #POST Requests
    def do_POST(self):
        #Checks if the UUID is match (Kind of authentication)
        '''if (self.headers.get('UUID') == UUID):
            #Client send a new data about command
            if self.path.endswith("/Commands"):
                #print('Got POST Command')
                self.data_string = self.rfile.read(int(self.headers['Content-Length']))
                self.send_response(200)
                self.end_headers()
                data = json.loads(self.data_string)
                print('New Data recieved from '+data['computer'])
                with open(os.path.join(scriptDir+ "\CommandsData\\"+data['computer']+".dat"), "ab+") as outfile:
                    outfile.write((data['computer']+','+data['type']+','+data['data']).encode())
                self.wfile.write(("Done").encode())
                return'''

ConfigurationServer()
myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
