-	Outline
1.	Environment Setup
     Python version support
     Python packages
2.	How to start
3.	Reference 
  

-	Environment Setup
Python version : 3.7.4
Python packages : pip install pyqt5
               Pip install pyqt5-tools
               Pip install requests
               Pip install xmltodict

-	How to start 
1.	Run Open_SOAP_Command_Tool.bat
 

Input the below settings
1.	IP Address
2.	Port
3.	Account
4.	Password
5.	API Group
6.	API Name
7.	Input body (if required)
	Then click Send API Button

Example : 
IP Address : 192.168.1.1
Port : 5043
Account : admin
Password : Password1
API Group : DeviceInfo
API Name : GetInfo
Input body : 

 

How to config Input Body ? 
     example :
API : EnableTrafficMeter  => "<NewTrafficMeterEnable>0</NewTrafficMeterEnable> \n"




