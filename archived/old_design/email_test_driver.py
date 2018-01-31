from settings import EmailSender


MY_ADDRESS = ''
PASSWORD = ''

def main():
    
    newSender = EmailSender()

    newSender.login_setup(MY_ADDRESS,PASSWORD,'smtp.gmail.com',587)

    if newSender.getSetupFlag():
    	newSender.send_testmsg()
    	newSender.close_connection()

main()