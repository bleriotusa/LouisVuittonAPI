from selenium import webdriver
from bs4 import BeautifulSoup
import mail_helper
import requests
import json
import os
import logging
import time

# Written by Luke Davis (@R8T3D)
# Under the MIT license

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

class LouisVuittonAPI(object):
    def __init__(self, region, browser):
        cls()
        print("Louis Vuitton API by Luke Davis (@R8T3D)")
        print( "="*60)
        self.s = requests.Session()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0',
            'Connection': 'keep-alive'
        }
        self.s.headers.update(headers)
        self.browser = browser

        # I can't be asked to add more regions, do that yourself.
        self.region_to_url = {
        'UK': 'uk.louisvuitton.com',
        'US': 'us.louisvuitton.com',
        'CA': 'ca.louisvuitton.com',
        'AU': 'au.louisvuitton.com',
        'HK': 'hk.louisvuitton.com',
        'EU': 'eu.louisvuitton.com',
        'KR': 'kr.louisvuitton.com',
        'JP': 'jp.louisvuitton.com'
        }

        self.region_to_lang = {
        'UK': 'eng-gb',
        'AU': 'eng-au',
        'US': 'eng-us',
        'HK': 'eng-hk',
        'EU': 'eng-e1',
        'KR': 'kor-kr',
        'JP': 'jpn-jp',
        'CA': 'eng-ca'
        }

        try:
            self.lv_base_url = self.region_to_url[region.strip().upper()]
            self.lv_lang = self.region_to_lang[region.strip().upper()]
        except:
            print("Invalid region, correct your spelling or add it.")
            raise ValueError('Invalid region')

        if browser:
            self.driver = webdriver.Firefox()
            self.driver.get("https://" + self.lv_base_url)
            cookies = self.driver.get_cookies()
            # print cookies
            for cookie in cookies:
                self.s.cookies.set(cookie['name'], cookie['value'])
        else:
            self.s.get("https://" + self.lv_base_url + "/eng-ca/homepage")
            # response = requests.get("https://" + self.lv_base_url + "/eng-ca/homepage")

        print( "Region: " + region.upper())
        print( "="*60)

    def get_product_info(self, sku):
        """
        Prints product information.

        Args:
            sku: Louis Vuitton product SKU.
        """

        sku = sku.upper()
        print( "Getting product info for " + sku + "...")
        print( " ")

        info_url = "http://" + self.lv_base_url + "/ajax/product.jsp?storeLang=" + self.lv_lang + "&pageType=product&id=" + sku

        info_soup = BeautifulSoup(self.s.get(info_url).text, "lxml")

        try:
            product_name = info_soup.find("h1", {"itemprop": "name"}).text
            product_description = info_soup.find("div", {"id": "productDescriptionSeeMore"}).text.strip()
            product_price = info_soup.find("td", {"class": "priceValue price-sheet"}).text.strip()
            product_image = info_soup.find("div", {"id": "informations"})['data-src-weibo'].replace(" ", "%20")
            product_pid = info_soup.find("input", {"id": "addToWishListFormProductId"})['value']
            display = True
        except:
            display = False
            print( "Product couldn't be found.")

        stock = self.get_stock_status(sku)
        
        if display:
            print( "Product Info:")
            print( "-"*40)
            print( "SKU: " + sku)
            print( "PID: " + product_pid)
            print( "Name: " + product_name)
            print( "Price: " + product_price)
            print( "Description: " + product_description)
            print( "Image URL: " + product_image)
            print( "Available: " + str(stock))
            print( "-"*40)

        if stock:
            choice = input("Product appears to be in stock. \nAttempt to add product to cart? (Y/N) ")
            if choice.upper() == "Y":
                self.add_to_cart(sku)

    def get_pid(self, sku):
        """
        Same function as get_product_info but
        only gets the PID. (for speed reasons)

        Args:
            sku: Louis Vuitton product SKU.
        """

        sku = sku.upper()
        print( "Getting PID for " + sku + "...")

        info_url = "http://" + self.lv_base_url + "/ajax/product.jsp?storeLang=" + self.lv_lang + "&pageType=product&id=" + sku

        info_soup = BeautifulSoup(self.s.get(info_url).text, "lxml")

        pid = info_soup.find("input", {"id": "addToWishListFormProductId"})['value']

        return pid

    def get_stock_status(self, sku, logging):
        """
        Checks a product's inventory status.

        Args:
            sku: Louis Vuitton product SKU.

        Returns:
            True or False based on if product
            is in stock.
        """

        sku = sku.strip().upper()
        print( "Getting stock status for " + sku + "...")

        stock_url = "https://secure.louisvuitton.com/ajaxsecure/getStockLevel.jsp?storeLang=" + self.lv_lang + "&pageType=product&skuIdList=" + sku
        if self.browser:
            self.driver.delete_all_cookies()
            self.driver.get(stock_url)
            element = self.driver.find_element_by_tag_name('body')
            stock_json_raw = element.text
        else:
            response =  self.s.get(stock_url)
            logging.info(response.content)
            stock_json_raw = response.text.strip()

            
        stock_json = json.loads(stock_json_raw)

        if stock_json[sku]['inStock']:
            return True
        else:
            return False

    def add_to_cart(self, sku):
        """
        Adds a product to cart.

        Args:
            sku: Louis Vuitton product SKU.
        """
        sku = sku.upper()
        pid = self.get_pid(sku)

        if self.get_stock_status(sku):
            print( sku + " is available.")
            cart = True
        else:
            print( sku + " is NOT available.")
            cart = False

        print( "Attempting to ATC...")

        headers = {
            'Origin': 'http://' + self.lv_base_url,
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.8,de;q=0.6',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': '*/*',
            'Referer': 'http://uk.louisvuitton.com/eng-gb/products/slender-id-wallet-damier-graphite-nvprod470028v',
            'Connection': 'keep-alive',
        }

        params = (
            ('storeLang', self.lv_lang),
        )

        data = [
          ('_dyncharset', 'UTF-8'),
          ('/atg/commerce/order/purchase/CartModifierFormHandler.catalogRefIds', sku),
          ('_D:/atg/commerce/order/purchase/CartModifierFormHandler.catalogRefIds', ' '),
          ('/atg/commerce/order/purchase/CartModifierFormHandler.productId', pid),
          ('_D:/atg/commerce/order/purchase/CartModifierFormHandler.productId', ' '),
          ('/atg/commerce/order/purchase/CartModifierFormHandler.HSOptionsAsString', '{}'),
          ('_D:/atg/commerce/order/purchase/CartModifierFormHandler.HSOptionsAsString', ' '),
          ('/atg/commerce/order/purchase/CartModifierFormHandler.quantity', '1'),
          ('_D:/atg/commerce/order/purchase/CartModifierFormHandler.quantity', ' '),
          ('/atg/commerce/order/purchase/CartModifierFormHandler.useForwards', 'true'),
          ('_D:/atg/commerce/order/purchase/CartModifierFormHandler.useForwards', ' '),
          ('/atg/commerce/order/purchase/CartModifierFormHandler.addItemToOrder', '--'),
          ('_D:/atg/commerce/order/purchase/CartModifierFormHandler.addItemToOrder', ' '),
          ('/atg/commerce/order/purchase/CartModifierFormHandler.addItemToOrderSuccessURL', '/collections/productSheet/forms/addToCartForm.jsp?storeLang=' + self.lv_lang + '&productId=' + pid + '&skuId=' + sku + '&isMoM=false&priceButtonMom=&addToCartSuccess=true'),
          ('_D:/atg/commerce/order/purchase/CartModifierFormHandler.addItemToOrderSuccessURL', ' '),
          ('/atg/commerce/order/purchase/CartModifierFormHandler.addItemToOrderErrorURL', '/collections/productSheet/forms/addToCartForm.jsp?storeLang=' + self.lv_lang + '&productId=' + pid + '&skuId=' + sku + '&isMoM=false&priceButtonMom='),
          ('_D:/atg/commerce/order/purchase/CartModifierFormHandler.addItemToOrderErrorURL', ' '),
          ('_DARGS', '/mobile/collections/productSheet/forms/addToCartForm.jsp'),
        ]

        if cart:
            ATC = self.s.post('https://secure.louisvuitton.com/ajaxsecure/addToCartForm', headers=headers, params=params, data=data)

            if self.browser:
                self.driver.get("http://uk.louisvuitton.com/" + self.lv_lang + "/cart")
                input()
            else:
                print( "Status Code: " +  str(ATC.status_code))
                print( "ATC success.")

if __name__ == '__main__':
    cls()
    print( "Louis Vuitton API by Luke Davis (@R8T3D)")
    print( "="*60)
    logging.basicConfig(level=logging.INFO)
    # browser = raw_input("Browser? (Y/N) ")

    # region = raw_input("Region? Options: US,UK,JP,EU,AU,KR,CA")
    browser = False
    region = "CA"

    lv = LouisVuittonAPI(region, browser)

    choice = "STOCK"
    sku = 'M40712'
    choice = choice.strip().upper()
    print( os.environ['userPassword'] )
    if choice == "ATC":
        lv.add_to_cart(sku)
    elif choice == "STOCK":
        while True:
            status = lv.get_stock_status(sku, logging)
            logging.info( sku + " in Stock: " + str(status))
            if status:
                mail_helper.send_smtp()
                logging.info("Sent mail")
                logging.info("Sleeping for 5 minutes")
                time.sleep(300) # 5 minutes
            time.sleep(1)
            
    else:
        lv.get_product_info(sku)