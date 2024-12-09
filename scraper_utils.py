from datetime import datetime # Get current time
import requests # scrape HTML
import smtplib, ssl # Send Email
import imaplib # Read Email
import email
import time # Wait function
import logging
import logging.handlers

bot_email_addr = 'poke.scrape.bot@gmail.com'
app_password = 'zykj tdau xtmi bzfn'

bot_sig = '\n\nI am a bot beep-boop.'

def curr_time():
    return str(datetime.now()).split('.')[0]


def continuous_request(url):
    while True:
        try:
            response = requests.get(url).text
            return response
        except Exception as e:
            print('Unable to get response from ' + url + ' at ' + curr_time() + '.')
            time.sleep(5)
            continue


def send_email(subject,message, recipients):
    while True:
        try:
            for recipient in recipients:
                s = smtplib.SMTP('smtp.gmail.com', 587)
                s.starttls()
                s.login(bot_email_addr, app_password)
                s.sendmail(bot_email_addr, recipient, subject+message+bot_sig)
                s.quit()
            break
        except Exception as e:
            print('Unable to send to email at ' + curr_time() + '. Trying again...')
            time.sleep(1)
            continue

def get_incoming_emails():

    # Continually try and get
    imap_server = imaplib.IMAP4_SSL(host='imap.gmail.com')
    imap_server.login(bot_email_addr, app_password)
    imap_server.select()
    _, message_numbers_raw = imap_server.search(None, 'ALL')


    email_subjects = []
    email_senders = []
    email_infos = []
    for message_number in message_numbers_raw[0].split():
        imap_server.store(message_number, '+FLAGS', '\\Deleted')
        _, msg_data = imap_server.fetch(message_number, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_string(response_part[1].decode())
                email_senders.append(msg['from'])
                email_subjects.append(msg['subject'])

    return [email_subjects,email_senders]


def get_incoming_emails_continuous():
    while True:
        try:
            [email_subjects,email_senders] = get_incoming_emails()
            break
        except Exception as e:
            print('Unable to connect to email server at ' + curr_time() + '.')
            time.sleep(5)
            continue
            
    return [email_subjects,email_senders]


def setup_logger(logger_name):

    LOG_FILENAME = 'logs/' + logger_name + '.log'
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # Setup a rotating log file with a max file size of 10MB. 
    # Once the file is full it creates a new file. After 5 
    # files have been fully written, it begins overwriting 
    # the first file, then the second, and so on. 
    handler = logging.handlers.RotatingFileHandler(
        LOG_FILENAME,
        maxBytes=1000000,
        backupCount=5
    )

    formatter = logging.Formatter('%(asctime)s : %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
