import smtplib

from string import Template

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

MY_ADDRESS = ''
PASSWORD = ''

def get_contacts(filename):
    """
    Return two lists names, emails containing names and email addresses
    read from a file specified by filename.
    """
    
    names = []
    emails = []
    with open(filename, mode='r', encoding='utf-8') as contacts_file:
        for a_contact in contacts_file:
            names.append(a_contact.split()[0])
            emails.append(a_contact.split()[1])
    return names, emails

def read_template(filename):
    """
    Returns a Template object comprising the contents of the 
    file specified by filename.
    """
    
    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)

def main():
	names, emails = get_contacts('email_files/mycontacts.txt') # read contacts
	message_template = read_template('email_files/message.txt')

	#try:
	# set up the SMTP server
	s = smtplib.SMTP(host='smtp.gmail.com', port=587)
	s.starttls()
	s.login(MY_ADDRESS, PASSWORD)

	# For each contact, send the email:
	for name, email in zip(names, emails):
	    msg = MIMEMultipart()       # create a message

	    # add in the actual person name to the message template
	    message = message_template.substitute(PERSON_NAME=name.title())

	    # Prints out the message body for our sake
	    # print(message)

	    # setup the parameters of the message
	    msg['From']=MY_ADDRESS
	    msg['To']=email
	    msg['Subject']="Image Msg Test"
	    
	    # add in the message body
	    # msg.attach(MIMEText(message, 'plain'))

		# send msg with picture
	    msgText = MIMEText('<b>Some <i>HTML</i> text</b> and an image.<br><img src="cid:image1"><br>Nifty!', 'html')

	    msg.attach(msgText)

	    fp = open('email_files/dog.png','rb')
	    msgImage = MIMEImage(fp.read())
	    fp.close()

	    msgImage.add_header('Content-ID','<image1>')
	    msg.attach(msgImage)

	    
	    # send the message via the server set up earlier.
	    s.send_message(msg)
	    del msg
	    
	# Terminate the SMTP session and close the connection
	s.quit()
	#except:
	#	print("Error: Failed to send email message, Check your setting and try again")
    
if __name__ == '__main__':
    main()
