from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import re
import requests

def extract_price_mad(price_string):
    # Remove non-digit characters from the string
    numeric_part = re.sub(r'[^\d,]', '', price_string)

    # Replace comma with dot to form a valid float number
    numeric_part = numeric_part.replace(',', '.')

    try:
        return numeric_part + ' MAD'
        # return float(numeric_part)
    except ValueError:
        return None

def parse_product(product_html):
    product_info = {}
    soup = BeautifulSoup(product_html, 'html.parser')

    # Extract product name
    product_info['name'] = soup.select_one('.product-title a').text.strip().replace('...', '')
    product_info['availability'] = soup.select_one('.product-availability').text.strip()
    product_info['description'] = soup.select_one('.product-description-short').text.strip()
    product_info['link'] = soup.select_one('.product-title a')['href']

    # Extract product image URL
    product_info['image_url'] = soup.select_one('.product-thumbnail img')['src']

    # Extract product brand
    product_info['brand'] = product_info['name'].replace('PC Gamer UltraPC ', '').split(' ')[0]  # Brand information is not available in the provided HTML

    # Extract product price
    product_info['price'] = extract_price_mad(soup.select_one('.price').text.strip())

    return product_info

def get_product_list_and_parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find the product container
    product_container = soup.select_one('.products')

    # print(product_container)

    # Find all products within the container
    product_list = product_container.find_all('article')

    # Apply parse_product to each product in the list
    parsed_products = [parse_product(str(product)) for product in product_list]

    return parsed_products

def get_html_with_selenium(url):
    driver = None
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')  # Last I checked this was necessary.
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        html_content = driver.page_source
        return get_product_list_and_parse(html_content)
    except Exception as e:
        print(f"Error: {e}")
        return None
    finally:
        if driver:
            driver.quit()


def write_to_file(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=2)  # indent=2 for pretty formatting

API_ENDPOINT='http://localhost:3000/products'

if __name__ == "__main__":
    # while from page 1 to 10
    for i in range(1, 11):
        target_url = f'https://www.ultrapc.ma/meilleures-ventes?page={i}/'
        html_content = get_html_with_selenium(target_url)
        if html_content is not None:
            # loop through the list of products and print them
            for product in html_content:
                print(product)
                requests.post(url=API_ENDPOINT, data=product)
            # write_to_file(html_content, 'ultra-pc.json')

    # target_url = 'https://www.ultrapc.ma/'
    # target_url = 'https://www.ultrapc.ma/'
    # target_url = 'https://www.ultrapc.ma/recherche?controller=search&s=intel+core+i-5'
        # print(html_content)