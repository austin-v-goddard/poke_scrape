
import requests # scrape HTML
from bs4 import BeautifulSoup # Parse HTML
from datetime import datetime # Get current time
import time # Wait function
import smtplib, ssl # Send Email
import imaplib # Read Email
import email
from pathlib import Path # Does file exist
import threading

## TODO
#   Keep html on change
#   Add output (prints every hour)

## Global Vars
# HTML
sz_url = 'https://safari-zone.com/collections/frontpage'
# File
prod_file_name = 'current_safari_prods.txt'
# Email
bot_email_addr = 'poke.scrape.bot@gmail.com'
app_password = 'zykj tdau xtmi bzfn'
mail_list = ['austin.v.goddard@gmail.com','kyler.j.goddard@gmail.com','kassidie@gmail.com']
admin_mail = ['austin.v.goddard@gmail.com']
bot_sig = '\n\nI am a bot beep-boop.'


## Functions

def curr_time():
    return str(datetime.now()).split('.')[0]


def continuous_request(url):
    while True:
        try:
            response = requests.get(url).text
            return response
        except Exception as e:
            print('Unable to get response from ' + url + ' at ' + curr_time() + '.')
            continue


def poll_safari_zone():
    sz_html = continuous_request(sz_url)

    sz_soup = BeautifulSoup(sz_html, 'html.parser')

    soup_all_products = sz_soup.find_all('li', class_='grid__item scroll-trigger animate--slide-in')

    num_products = len(soup_all_products)

    result_string = 'There are currently ' + str(len(soup_all_products)) + ' products available for pre-order on Safari-Zone:\n'

    for i in range(num_products):
        prod_name = soup_all_products[i].find('a').contents[0].strip()
        try:
            card_badge = '(' + soup_all_products[i].find('span').contents[0] + ')' #
        except Exception as e:
            card_badge = ''
        result_string = result_string + '   ' + prod_name + ' ' + card_badge + '\n'

    return result_string



def did_prod_list_change(new_prod_list):
    if new_prod_list != open(prod_file_name, 'r').read():
        return True
    return False


def write_prod_list(result_string):
    f = open(prod_file_name, "w")
    f.write(result_string)
    f.close()


def send_email(message, recipients):
    for recipient in recipients:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(bot_email_addr, app_password)
        s.sendmail(bot_email_addr, recipient, message)
        s.quit()


def get_incoming_emails():
    imap_server = imaplib.IMAP4_SSL(host='imap.gmail.com')
    imap_server.login(bot_email_addr, app_password)
    imap_server.select()

    email_subjects = []
    email_senders = []
    email_infos = []
    _, message_numbers_raw = imap_server.search(None, 'ALL')
    for message_number in message_numbers_raw[0].split():
        _, msg_data = imap_server.fetch(message_number, '(RFC822)')
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_string(response_part[1].decode())
                email_senders.append(msg['from'])
                email_subjects.append(msg['subject'])

    return [email_subjects,email_senders]

def poll_incoming_emails():
    pass


## Main
[email_subjects,email_senders] = get_incoming_emails()

if len(email_senders) is 0:
    print("No new emails...")
    # Continue

for subject,sender in zip(email_subjects,email_senders):
    print(subject)
    print(sender)

quit()

t1 = threading.Thread(target=print_square)


# Check to see if product file exists. If not, create it.
if not Path(prod_file_name).is_file():
    print('Product file does not exist. Creating now...')
    result_string = poll_safari_zone()
    write_prod_list(result_string)
    

while True: # Main Loop
    try:
        result_string = poll_safari_zone()

        if did_prod_list_change(result_string):
            print("Preorders have changed...")
            write_prod_list(result_string)
            message = 'Subject: Change to Safari Zone Preorders ' + curr_time() +  '. \n\nSafariZone preorder change at: ' + curr_time() + '\n\n' + result_string + '\nLink: ' + sz_url + bot_sig
            send_email(message,mail_list)
        #quit()
        time.sleep(30)

    # If an error occurs, notify admin
    except Exception as e:
        print(e)
        print("Encountered Error...")
        message = 'Subject: Poke Scraper Encountered Error ' + curr_time() +  '. \n\nDeal with it.\n\n' + 'Reason: ' + str(e) + '\n\nAttempting to continue.\n\n' + bot_sig
        send_email(message, admin_mail) # send admin email
        continue

