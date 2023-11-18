from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
from bs4 import BeautifulSoup
import requests

def extract_clean_string(string:str):
    return string.replace('\u00a0', '').replace('\u00e9', '').strip()

from bs4 import BeautifulSoup

from bs4 import BeautifulSoup

def parse_product(product_html):
    product_info = {}
    soup = BeautifulSoup(product_html, 'html.parser')

    try:
        # Extract product name
        product_info['name'] = soup.select_one('.woo-loop-product__title a').text.strip()
    except AttributeError:
        product_info['name'] = None

    try:
        # Extract product link
        product_info['link'] = soup.select_one('.woo-loop-product__title a')['href']
    except (AttributeError, TypeError):
        product_info['link'] = None

    try:
        # Extract product image URL
        product_info['image_url'] = soup.select_one('.mf-product-thumbnail img')['src']
    except (AttributeError, TypeError):
        product_info['image_url'] = None

    try:
        # Extract product brand (if available)
        product_info['brand'] = soup.select_one('.meta-brand a').text.strip() if soup.select_one('.meta-brand a') else None
    except AttributeError:
        product_info['brand'] = None

    try:
        # Extract product description
        product_info['description'] = soup.select_one('.woocommerce-product-details__short-description').text.strip()
    except AttributeError:
        product_info['description'] = None

    try:
        # Extract product price
        product_info['price'] = soup.select_one('span.woocommerce-Price-amount.amount').text.strip()
    except AttributeError:
        product_info['price'] = None

    try:
        # Extract discounted price (if available)
        discounted_price = soup.select_one('.price del .woocommerce-Price-amount bdi')
        product_info['discounted_price'] = discounted_price.text.strip() if discounted_price else None
    except AttributeError:
        product_info['discounted_price'] = None

    return product_info



def get_product_list_and_parse(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find the product container
    product_container = soup.select_one('.products-content')
    print(product_container)

    # Find all products within the container
    product_list = product_container.find_all('li')

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
        sleep(2)
        driver.save_screenshot('screenshot.png')
        html_content = driver.page_source
        # // write to file
        # write_to_file(html_content, 'nextlevelpc.html')
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
    target_url = 'https://nextlevelpc.ma/produits-les-plus-vendus/'
    # target_url = 'https://nextlevelpc.ma/page/2/?s=intel+i5+&post_type=product'
    # target_url = 'https://nextlevelpc.ma/?s=i5+&post_type=product'
    html_content = get_html_with_selenium(target_url)
    if html_content is not None:
        for product in html_content:
            print(product)
            requests.post(url=API_ENDPOINT, data=product)
        # write_to_file(html_content, 'nextlevelpc.json')

