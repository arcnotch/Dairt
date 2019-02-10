# Dairt

Triad Malicious Remote Code PoC

The goal of the team is to form a Social Engineering vector attack in order to gain network control over tested companies networks by take over the victim's station (Phishing attack).

## Struction

The project is consists of 3 layers (MVC application): Client, Server and C&C server.

##### Client
composed of a docm document which includes a VBA macro that downloads the malicious files and payloads to execute on the victim's station.

##### Server
The logic control unit of the application business flow. The server roles are:
* Transfer and validate the client input  to the C&C server.
* Stores the client output commands in the DB.
* Validate the user origin (by IP)

##### C&C Server
The C&C server roles are:
* Listening for remote code execution connection
* Contains the payloads and malicious files

##### Encryption 
The client side decrypt the CnC's files with symmetric key. This script was created in order to encrypt the files with the symmetric key.

##### File Listener 
A single URL listenner that returns the malicious doc that contains the malicious macro

### Prerequisites


[Python 3](https://www.python.org/downloads/)


[MySQL Localhost Server](https://www.mysql.com/downloads/)



### Installing - Client

The VBA (client.vbs) and the VB (main.vbs) Scripts contain the configuration to communicate to the server.

The following lines should be edit due to the application configuration:

```
SERVERADDRESS = "http://IP_or_DNS/"
CONFIGURATIONPATH = "/Configuration"
HEADERS = "Your_First-UUID_As_Clear_Text" '<- Server authentication
```
* CONFIGURATIONPATH - Should be match to the server configuration path in the configuration.json
* HEADERS - Should be match to the server UUID in the configuration.json

### Installing - Server & DB

The server runs on Python 3 and uses MySQL server.
In order to configurate the server there is a configuration file named [configuration.json]. A JSON file includes the server configuration requirements:

```
{
	"Server": "http://Server_IP_or_DNS/",
	"Port": 80,
	"PrivateKey": "",
	"Certificate": "",
	"UUID": "Your_First-UUID_As_Clear_Text",
	"CnCUrl": "http://CNC_IP_or_DNS/",
	"CnCPort": 8080,
	"MaliciousPath":"/MaliciousPath",
	"DocmFile":"malicious.doc",
	"FromAbroad": true\false
}
```
* In addition, edit the Server.py following code to be match to the C&C server headers:
```
HEADERS = {'UUID':'CNC_Your_Secend-UUID_As_Clear_Text'}
```
In order to configurate the DB there is a configuration file named [SQLconfiguration.json]. A JSON file includes the SQL configuration requirements:

```
{
	"Server": "127.0.0.1",
	"Username": "DB_username",
	"Password": "DB_password"
}

```
Create a database named: ```payload```
and create a table by the following command:
```
CREATE TABLE commandresults (
computername VARCHAR(50) NOT NULL,
event VARCHAR(50) NOT NULL,
data VARCHAR(max)
)
```
### Installing - C&C

The server runs on Python 3.
In order to configurate the C&C there is a configuration file named [configuration.json]. A JSON file includes the C&C configuration requirements:

```
{
	"Server": "http://CNC_IP_or_DNS/",
	"Port": 8080,
	"PrivateKey": "",
	"Certificate": "",
	"UUID": "CNC_Your_Secend-UUID_As_Clear_Text",
	"File": "main.vbs",
	"ServerAddress": "http://Server_IP_or_DNS/",
    "FromAbroad": false\true
}

```

The "File" attribute is the first file the client is going to download and execute automaticly when the VBA Script (client.vbs) is executed. If you want to edit or change the first file to be executed change the name of the file in the configuration file and move your file to the C&C folder.


## Usage

* Default command - A command which the client will execute and send an output to the server
* Command - A command that required a connection (For example, reverse command shell)

The attack is executed as followed:
1. The client requests for the main script and execute it automaticlly.
2. The malicious file configurates itself by the server and gets the list of files and commands to execute.
3. ```Default commands``` execution.
4. Downloads list of files by the list provided by the server in the configuration phase and decrypts each file.
5. ```Commands``` execution.


In order to run a ```Default commands```, edit the ```defaultcommands.txt``` file in the C&C server folder (one line one command).

In order to run a ```Commands```, edit the ```commands.txt``` file in the C&C server folder (one line one command).
### Encryption
**The client side decrypted the CnC's files with a symmetric key. The key is the same as the UUID header which means the files have to be encrypted with the UUID header as the symmetric key.**
In order to download encrypted files:
1. Encryp each file with the VBScript encryption script:
```myEncryption.vbs file.txt file.enc "Your_First-UUID_As_Clear_Text"```
2. Copy the encrypted file to the MaliciousFiles folder in the C&C.
3. Rename the encrypted filename to the origin name.

### Installing - File Listener

The server runs on Python 3.
In order to configurate the File Listener there is a configuration file named [configuration.json]. A JSON file includes the File Listener configuration requirements:

```
{
	"Server": "http://IP_or_DNS/",
	"Port": 8085,
	"PrivateKey": "",
	"Certificate": "",
	"DocmFile": "main.vbs",
    "FromAbroad": false\true
}

```

### Doc VBA Obfuscation

We used [Doctor Lai's VBScript Obfuscator](https://github.com/DoctorLai/VBScript_Obfuscator) in order to obfuscate the VBA script: ```client.vbs``` inside the Doc file (macro). 

### AV Tests

We focus on spesific AV which did not recognize the attack


## Built With

* Native Python3 (servers)
* Native VBScript and VBA
* Vulnerable platform - Microsoft Word macro documents



## Authors

* **Yarden Yerushalmi** - *Team leader & Programmer* - [Linkedin](https://www.linkedin.com/in/yarden-yerushalmi/)
* **Avi Ozizak** - *Infrastruction & Payloads* - [Linkedin](https://github.com/)
* **Guy Ratzon** - *Infrastruction* - [Linkedin](https://github.com/)
* **Matan Frank** - *Programmer* - [Linkedin](https://github.com/)

All above are friends and co-workers in  [***Triad Security***](https://www.triadsec.com/)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

The following codes were included in the script:
* [Json parser/encoder](http://demon.tw/my-work/vbs-json.html)
* [Json decoder](https://gist.github.com/atifaziz/5465514)
* [VB Script encryption and decryption](http://www.robvanderwoude.com/vbstech_files_encode_xor.php)
