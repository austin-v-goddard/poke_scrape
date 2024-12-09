
from scraper_utils import continuous_request
from bs4 import BeautifulSoup # Parse HTML


sz_url = 'https://www.pokene.com/copy-of-pre-order-coming-soon-1?page=4'

sz_html = continuous_request(sz_url)

sz_soup = BeautifulSoup(sz_html, 'html.parser')

soup_all_products = sz_soup.find('ul', class_='S4WbK_ uQ5Uah c2Zj9x')
children = soup_all_products.findChildren("li" , recursive=False)
for child in children:
    print(child)

print(len(children))
quit()

num_products = len(soup_all_products)

result_string = 'There are currently ' + str(len(soup_all_products)) + ' products available for pre-order on Safari-Zone:\n'

for i in range(num_products):
    prod_name = soup_all_products[i].find('a').contents[0].strip()
    try:
        card_badge = '(' + soup_all_products[i].find('span').contents[0] + ')'  #
    except Exception as e:
        card_badge = ''
    result_string = result_string + '   ' + prod_name + ' ' + card_badge + '\n'

