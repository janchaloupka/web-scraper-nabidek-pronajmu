#!/usr/bin/evn python3
import logging
import time
from typing import List
from config import *
from offers_storage import OffersStorage
from scraper import fetch_latest_offers
from scrapers.generic_apartment_rental_scraper import ApartmentRentalOffer


def process_latest_offers(storage: OffersStorage):
    new_offers: List[ApartmentRentalOffer] = []
    for offer in fetch_latest_offers():
        if not storage.contains(offer):
            new_offers.append(offer)

    first_time = storage.first_time
    storage.save_offers(new_offers)

    logging.info("Offers fetched (new: " + str(len(new_offers)) + ")")

    if first_time:
        logging.info("No previous offers, first fetch is running silently")
        return set()

    # TODO pošli všechny nabídky z `new_offers` na Discord


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    offers_storage = OffersStorage(FOUND_OFFERS_FILE)

    logging.info("Fetching latest offers every " + str(REFRESH_INTERVAL_MINUTES) + " minutes")

    # Spuštění funkce každých x sekund
    # https://stackoverflow.com/a/25251804
    start_time = time.time()
    while True:
        process_latest_offers(offers_storage)
        time.sleep(60.0 * REFRESH_INTERVAL_MINUTES - ((time.time() - start_time) % (60.0 * REFRESH_INTERVAL_MINUTES)))
