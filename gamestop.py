

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from time import sleep
import pandas as pd
#from csv_diff import load_csv, compare
import smtplib, ssl # Send Email
import imaplib # Read Email
import email
from email.mime.text import MIMEText
from datetime import datetime # Get current time

pd.option_context('display.max_rows', None, 'display.max_columns', None)  # more options can be specified also

# Email
bot_email_addr = 'poke.scrape.bot@gmail.com'
app_password = 'zykj tdau xtmi bzfn'
mail_list = ['austin.v.goddard@gmail.com','kyler.j.goddard@gmail.com'] #,'kassidie@gmail.com', 'lindsey.goddard15@gmail.com']
admin_mail = ['austin.v.goddard@gmail.com']
bot_sig = '\n\nI am a bot beep-boop.'



# Set up Chrome options
chrome_options = Options()
#chrome_options.add_argument("--headless")  # Run in headless mode (no browser UI)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
#chrome_options.binary_location = "/usr/bin/google-chrome"
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
#chrome_options.add_argument(
#    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")

# Path to your ChromeDriver
#chromedriver_path = "/home/kgoddard/poke_scrape/chromedriver-linux64/chromedriver"  # Replace with your ChromeDriver path
#service = Service(chromedriver_path)

# gamestop URLs
search_url = "https://www.gamestop.com/search/?q=prismatic+evolutions&lang=default&start=0&sz=20"
### Product urls ###
url1  = "https://www.gamestop.com/toys-games/trading-cards/products/pokemon-trading-card-game-prismatic-evolutions-booster-bundle/418865.html"
url2 = "https://www.gamestop.com/toys-games/trading-cards/products/pokemon-trading-card-game-prismatic-evolutions-elite-trainer-box/417631.html"
url3 = "https://www.gamestop.com/toys-games/trading-cards/products/pokemon-trading-card-game-prismatic-evolutions-surprise-box-styles-may-vary/418757.html"
url4 = "https://www.gamestop.com/toys-games/trading-cards/products/pokemon-trading-card-game-prismatic-evolutions-binder-collection/417633.html"
url5 = "https://www.gamestop.com/toys-games/trading-cards/products/pokemon-trading-card-game-prismatic-evolutions-mini-tin-styles-may-vary/418756.html"
url6 = "https://www.gamestop.com/toys-games/trading-cards/products/pokemon-trading-card-game-scarlet-and-violet-prismatic-evolutions-accessory-pouch/419125.html"
url7 = "https://www.gamestop.com/toys-games/trading-cards/products/pokemon-trading-card-game-prismatic-evolutions-poster-collection/417632.html"
url8 = "https://www.gamestop.com/toys-games/trading-cards/products/pokemon-trading-card-game-prismatic-evolutions-blister---two-pack/418758.html"
url9 = "https://www.gamestop.com/toys-games/trading-cards/products/pokemon-trading-card-game-prismatic-evolutions-tech-sticker-collection/417634.html"

url_list = [url1, url2, url3, url4, url5, url6, url7, url8, url9]
url = 'https://www.gamestop.com/toys-games/trading-cards/products/pokemon-trading-card-game-twilight-masquerade-elite-trainer-box/406121.html'

driver = webdriver.Chrome(options=chrome_options)
driver.get(url)
time.sleep(5) # Lets all elements load. Not best solution

button = driver.find_element(By.XPATH, "//*[@id='add-to-cart-buttons']/div[2]/div/button[1]")

#print(button)
#button.click()

time.sleep(10)


quit()

buttons = driver.find_elements(By.TAG_NAME, "button")
print(len(buttons))

for button in buttons:
    #print(button)
    #print(type(button))
    if 'add to cart' in button.get_attribute('innerHTML').lower():
        print('--------')

        print(button.get_attribute('innerHTML'))
        print('--------')
        button.click()
        time.sleep(1)

time.sleep(2)
driver.quit()

quit()











while True:

    try:
        orig_prod_df = pd.read_csv('new_gamestop_product_status.csv', index_col=False)
        orig_prod_df.to_csv('orig_gamestop_product_status.csv', index=False)
    except Exception as e:
        print('Cannot find original product list, current list will now be original')

    # Open the URL
    tmp_prod_list = []
    for url in url_list:
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)

        ### Get the product information ###
        products = driver.find_elements(By.XPATH, "//h2[@class='product-name h2']")

        ### Iterate through products and extract details
        for product in products:
            ### Check if in stock ###
            try:
                stock_status_element = driver.find_element(By.XPATH, "//input[@id='isMasterInStock']")
                stock_status = stock_status_element.get_attribute("value")
                stock_status = "In Stock" if stock_status == "true" else "Out of Stock"
                print(f"Stock Status: {stock_status}")
            except Exception as e:
                print(f"Error extracting stock status: {e}")
                stock_status = 'Unable to Get'
            tmp_prod_list.append([product.text, stock_status])
            driver.quit()




    ### Create Data Frame of Results ###
    prod_df = pd.DataFrame(tmp_prod_list, columns=['Product', 'Stock_Status'])
    print('\n')
    print(UTCDateTime())
    print('Total Number of Prismatic Products', len(prod_df))
    print('\n\n')
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.max_colwidth', None, 'display.expand_frame_repr', False):
        print(prod_df)

    ### Comparing new and old product lists ###
    prod_df.to_csv('new_gamestop_product_status.csv', index=False)
    diff = compare(
    load_csv(open("new_gamestop_product_status.csv")),
    load_csv(open("orig_gamestop_product_status.csv")))

    ### If there are differences create the result string and email notification to subscribers ###
    if len(diff['added']) != 0:
        print(diff['added'])
        result_string = '\nThere are currently ' + str(len(prod_df)) + ' Prismatic Evolutions products listed on gamestop:\n\n'
        for i in prod_df.iterrows():
            result_string = result_string + '\n ' + str(i[1]['Product']) + ' ' + str(i[1]['Stock_Status']) + '\n'
        print(result_string)
        message = 'Subject: Change to Gamestop PE Listings ' + curr_time() +  '. \n\nGamestop change at: ' + curr_time() + '\n\n' + result_string + '\nLink: ' + search_url + bot_sig
        #message = 'Target test'
        #send_email(message,mail_list)
    else:
        print('No changes found')
    driver.quit()

