import smtplib
import shutil
import os
import json

from pathlib import Path
from string import Template

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# path for storing email credientials
AUTH_PATH = 'auth'
AUTH_FILE = 'email_crediential.json'

class EmailSender:

	def __init__(self):

		self.isSetup = False
		self.fname_auth = os.path.join(AUTH_PATH,AUTH_FILE)
		path_to_fname_auth = Path(self.fname_auth)

		if path_to_fname_auth.exists():

			with open(self.fname_auth) as cred_file:

				try:	# try to open json file and parse details
					collective_params = json.load(cred_file)

					self.email_address = collective_params['email_address']
					self.email_password = collective_params['email_password']
					self.smtp_server = collective_params['smtp_server']
					self.port_number = int(collective_params['port_number'])
				except:
					print("Email error 0: Failed to get login details, perhaps invalid or corrupted auth/email_crediential.json file?")
					self.isSetup = False

				try:	# if successfully loaded login details, try to login server
					self.sendingServer = smtplib.SMTP(host=self.smtp_server, port=self.port_number)
					self.sendingServer.starttls()
					self.sendingServer.login(self.email_address, self.email_password)
					self.isSetup = True
				except:
					print("Email error 1: Failed to setup SMTP server properly, perhaps invalid login details?")
					self.isSetup = False

				cred_file.close()


	def getSetupFlag(self):
		return self.isSetup

	def getLoginDetails(self):
		return self.email_address, self.email_password, self.smtp_server, self.port_number
		
	def login_setup(self, user, password, smtp, port):

		try:
			self.sendingServer = smtplib.SMTP(host=smtp, port=port)
			self.sendingServer.starttls()
			self.sendingServer.login(user,password)
		except:
			print("Email error 2: Failed to setup SMTP server, check your login details")
			self.isSetup = False

		try:
			self.email_address = user
			self.email_password = password
			self.smtp_server = smtp
			self.port_number = port			

			# write creditential files to json
			cred_data = {'email_address': self.email_address,
						 'email_password': self.email_password,
						 'smtp_server': self.smtp_server,
						 'port_number': str(self.port_number)
						}

			with open(self.fname_auth, 'w+') as myCred:
				json.dump(cred_data, myCred)
				myCred.close()

			self.isSetup = True
		except:
			print("Email error 3: Failed to store credientials, check if the folder (auth/) is present!")
			self.isSetup = False

	def send_testmsg(self):

		sendSuccess = False
		if self.isSetup:
			try:
			    msg = MIMEMultipart()       # create a message

			    # add in the actual person name to the message template
			    message = "Great! This is a test message from TrigCam!"

			    # Prints out the message body for our sake
			    print(message)

			    # setup the parameters of the message
			    msg['From']=' TrigCam noreply'
			    msg['To']= self.email_address
			    msg['Subject']= "TrigCam Test Message"
			    
			    # add in the message body
			    msg.attach(MIMEText(message, 'plain'))
			    
			    # send the message via the server set up earlier.
			    self.sendingServer.send_message(msg)
			    
			    del msg
			    sendSuccess = True
			except:
				print("Email error 4: Failed to send out email msg, runtime error!")
				sendSuccess = False

		return sendSuccess		


	def close_connection(self):
		if self.isSetup:
			self.sendingServer.quit()
			self.isSetup = False