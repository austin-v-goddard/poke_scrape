from bs4 import BeautifulSoup # Parse HTML
import time # Wait function
from pathlib import Path  # Does file exist


from scraper_utils import curr_time
from scraper_utils import send_email
from scraper_utils import continuous_request
from scraper_utils import setup_logger


safari_logger = setup_logger('safari')
sz_url = 'https://safari-zone.com/collections/frontpage'
prod_file_name = 'current_safari_prods.txt'


def get_sz_preorders():

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


def poll_safari(poll_interval=5, do_once=False, do_send=True):
    safari_logger.info('Starting Safari Poll')

    mail_list = open('mail_list.txt', 'r').readlines()
    admin_mail = open('admin_mail.txt', 'r').readlines()

    # Check to see if product file exists. If not, create it.
    if not Path(prod_file_name).is_file():
        print('Product file does not exist. Creating now...')
        result_string = poll_safari_zone()
        write_prod_list(result_string)
    
    while True:  # Main Loop
        safari_logger.info('Starting iteration')
        try:    
            # Check safari zone
            result_string = get_sz_preorders()
            if did_prod_list_change(result_string):
                safari_logger.info('Product List Change')
                write_prod_list(result_string)
                subject = 'Subject: Change to Safari Zone Preorders ' + curr_time() + '\n' 
                message = '\nSafariZone preorder change at: ' + curr_time() + '\n\n' + result_string + '\nLink: ' + sz_url
                if do_send: send_email(subject,message,mail_list)
            
            if do_once: break

            time.sleep(poll_interval)

        # If an error occurs, notify admin
        except Exception as e:
            safari_logger.error('Main loop exception ' + str(e))
            subject = 'Subject: Poke Scraper Encountered Error: ' + curr_time() + '\n' 
            message = '\nDeal with it.\n\n' + 'Reason: ' + str(e) + '\n\nAttempting to continue.\n\n'
            if do_send: send_email(subject, message, admin_mail) # send admin email
            continue

