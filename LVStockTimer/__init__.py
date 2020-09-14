import datetime
import logging
from . import lvcontrol
from ..shared_code import mail_helper
import os

import azure.functions as func


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    print( "="*60)

    # browser = raw_input("Browser? (Y/N) ")

    # region = raw_input("Region? Options: US,UK,JP,EU,AU,KR,CA")
    browser = False
    region = "CA"

    lv = lvcontrol.LouisVuittonAPI(region, browser)

    choice = "STOCK"
    sku = 'M40712'
    choice = choice.strip().upper()
    if choice == "ATC":
        lv.add_to_cart(sku)
    elif choice == "STOCK":
        status = lv.get_stock_status(sku, logging)
        logging.info( sku + " in Stock: " + str(status))
        if status:
            mail_helper.send_smtp()
            logging.info("Sent mail")
    else:
        lv.get_product_info(sku)


    logging.info('Python timer trigger function ran at %s', utc_timestamp)


# if __name__ == '__main__':
#     print( "="*60)

#     # browser = raw_input("Browser? (Y/N) ")

#     # region = raw_input("Region? Options: US,UK,JP,EU,AU,KR,CA")
#     browser = "N"
#     region = "CA"
#     if browser.strip().upper() == "Y":
#         browser = True
#     else:
#         browser = False

#     lv = LouisVuittonAPI(region, browser)
#     choice = "STOCK"
#     sku = 'M40712'
#     choice = choice.strip().upper()
#     if choice == "ATC":
#         lv.add_to_cart(sku)
#     elif choice == "STOCK":
#         print( "In Stock: " + str(lv.get_stock_status(sku)))
#     else:
#         lv.get_product_info(sku)
