import sys
from PyQt5.QtWidgets import QApplication , QMainWindow
from SOAP_Command_Tool import *
from datetime import datetime
import requests # pip install requests
import string
import random
import xmltodict # pip install xmltodict
import json
import os

log_file = os.path.dirname(os.path.abspath(__file__)) + "/soap_command_logs.txt"

class MyMainWindow(QMainWindow , Ui_Form):

    log_text = ""
    
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)
        
        if os.path.exists(log_file):
            os.remove(log_file)
        else:
             print("{} does not exist".format(log_file))
             
    def click_events(self):
        self.SendAPI.clicked.connect(self.send_soap_api)
        self.Quit.clicked.connect(self.close)

    def soap_request(self , verify_para , session_id , target_url , soap_apigroup , soap_apiname , soap_inputbody , token=None):

        try:
            soap_req_xml = '<?xml version="1.0" \n encoding="UTF-8" \n standalone="no" \n ?> \n' + \
                        '<SOAP-ENV:Envelope \n' + \
                        'xmlns:SOAPSDK1="http://www.w3.org/2001/XMLSchema" \n' + \
                        'xmlns:SOAPSDK2="http://www.w3.org/2001/XMLSchema-instance" \n' + \
                        'xmlns:SOAPSDK3="http://schemas.xmlsoap.org/soap/encoding/" \n' + \
                        'xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"> \n' + \
                        '<SOAP-ENV:Header> \n' + \
                        '<SessionID>' + session_id + '</SessionID> \n' + \
                        '</SOAP-ENV:Header> \n' + \
                        '<SOAP-ENV:Body> \n' + \
                        '<M1:' + soap_apiname + '\n xmlns:M1="urn:NETGEAR-ROUTER:service:' + soap_apigroup + ':1"> \n' + \
                        soap_inputbody + \
                        '</M1:' + soap_apiname + '> \n' + \
                        '</SOAP-ENV:Body> \n' + \
                        '</SOAP-ENV:Envelope> \n'

            headers = {'User-Agent': 'SOAP Toolkit 3.0', 'Cache-Control': 'no-cache', 'Pragma': 'no-cache',
                    'Content-type': 'text/xml;charset=utf-8',
                    'SOAPAction': 'urn:NETGEAR-ROUTER:service:' + soap_apigroup + ':1#' + soap_apiname}

            if token:
                headers["Cookie"] = token

            a = datetime.now()
            r = requests.post(target_url, data=soap_req_xml, headers=headers, timeout=30, verify=verify_para)
            #print(r.text)

            if soap_apiname == 'SOAPLogin':
                # print("token : {}".format(r.headers['Set-Cookie']))
                # print("#"*20)
                return r.headers['Set-Cookie']

            xpars = xmltodict.parse((r.text).lower())
            json_data = json.dumps(xpars)
            ret = json.loads(json_data)
            b = datetime.now()
            return ret , (b - a)
        except Exception as err:
            return None , None

    def send_soap_api(self):

        host = self.IPAddress.text() # Get QLineEdit()
        soap_port = self.Port.text()
        login_name = self.Account.text()
        login_pwd = self.Password.text()
        soap_apigroup = self.APIGroup.text()
        soap_apiname = self.APIName.text()
        soap_inputbody = self.InputBody.toPlainText() # Get QPlainTextEdit()

        session_id = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))

        if soap_port in ["80" , "5000"] :
            connect_type = "http"
        else:
            connect_type = "https"

        if connect_type == "https":
            verify_para = False
        else:
            verify_para = True

        target_url = '{0}://{1}:{2}/soap/server_sa/'.format(connect_type , host, soap_port)

        ##############
        # SOAP Login #
        ##############
        soap_login_inputbody = '<Password>' + login_pwd + '</Password> \n' + \
              '<Username>' + login_name + '</Username>'

        token = self.soap_request(verify_para=verify_para, session_id=session_id, target_url=target_url\
                             , soap_apigroup='DeviceConfig', soap_apiname='SOAPLogin' , soap_inputbody=soap_login_inputbody)

        ########################
        # ConfigurationStarted #
        ########################
        soap_start_inputbody = '<NewSessionID>{0}</NewSessionID>'.format(session_id)
        self.soap_request(verify_para=verify_para, session_id=session_id, target_url=target_url \
                     , soap_apigroup='DeviceConfig', soap_apiname='ConfigurationStarted', soap_inputbody=soap_start_inputbody , token=token)

        ###############
        # Test Action #
        ###############
        ret , res_time=self.soap_request(verify_para=verify_para, session_id=session_id, target_url=target_url \
                     , soap_apigroup=soap_apigroup, soap_apiname=soap_apiname, soap_inputbody=soap_inputbody , token=token)


        #########################
        # ConfigurationFinished #
        #########################
        soap_end_inputbody = '<NewStatus>ChangesApplied</NewStatus>'
        self.soap_request(verify_para=verify_para, session_id=session_id, target_url=target_url \
                     , soap_apigroup='DeviceConfig', soap_apiname='ConfigurationFinished', soap_inputbody=soap_end_inputbody , token=token)

        ###############
        # SOAP Logout #
        ###############
        self.soap_request(verify_para=verify_para, session_id=session_id, target_url=target_url \
                     , soap_apigroup='DeviceConfig', soap_apiname='SOAPLogout', soap_inputbody=soap_end_inputbody , token=token)


        #res_code = ret['SOAP-ENV:Envelope']['SOAP-ENV:Body']['ResponseCode']
        print("ret : {}".format(ret))
        if not ret:
            print("Device is not ready !!!")
            res_code = "Device is not ready !!!"
            ResBody = ""
            #return
        else:
            res_code = ret['soap-env:envelope']['soap-env:body']['responsecode']
            ResBody = str(ret['soap-env:envelope']['soap-env:body'])

        self.log_text = "\n" + self.log_text + "\n"
        
        # datetime object containing current date and time
        now = datetime.now()

        # dd/mm/YY H:M:S
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
        dt_string = dt_string + "\n" + \
                    "    Host      : " + host + "\n" + \
                    "    Port      : " + soap_port + "\n" + \
                    "    Account   : " + login_name + "\n" + \
                    "    Password  : " + login_pwd + "\n" + \
                    "    APIGroup  : " + soap_apigroup + "\n" + \
                    "    APIName   : " + soap_apiname + "\n" + \
                    "    InputBody : " + soap_inputbody + "\n" + \
                    "    ResCode   : " + res_code + "\n" + \
                    "    ResTime   : " + str(res_time) + "\n" + \
                    "    ResBody   : " + ResBody + "\n" + \
                    "=============================================="
                    
        self.log_text = dt_string + "\n" + self.log_text + "\n"

        #print(self.log_text)
        self.execution_logs.setPlainText(self.log_text)
        
        with open(log_file, "w") as myfile:
            myfile.write(self.log_text)
    
if __name__=="__main__":

    
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    myWin.click_events()
    sys.exit(app.exec_())
