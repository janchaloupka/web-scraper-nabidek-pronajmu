#!/usr/bin/evn python3

import logging
import os
import traceback
import time
from typing import List, Set
from scrapers.euro_bydleni_scraper import EuroBydleniScraper
from scrapers.generic_apartment_rental_scraper import ApartmentRentalOffer, GenericApartmentRentalScraper
from scrapers.idnes_reality_scraper import IdnesRealityScraper
from scrapers.realingo_scraper import RealingoScraper
from scrapers.sreality_scraper import SrealityScraper
from scrapers.ulov_domov_scraper import UlovDomovScraper


SCRAPERS: List[GenericApartmentRentalScraper] = [
    SrealityScraper("https://www.sreality.cz/api/cs/v2/estates/rss?category_main_cb=1&category_sub_cb=7|11|10|8|12|9|16&category_type_cb=2&locality_district_id=72&locality_region_id=14&sort=0"),
    IdnesRealityScraper("https://reality.idnes.cz/s/pronajem/byty/brno-mesto/?s-qc%5BsubtypeFlat%5D%5B0%5D=31&s-qc%5BsubtypeFlat%5D%5B1%5D=4k&s-qc%5BsubtypeFlat%5D%5B2%5D=41&s-qc%5BsubtypeFlat%5D%5B3%5D=5k&s-qc%5BsubtypeFlat%5D%5B4%5D=51&s-qc%5BsubtypeFlat%5D%5B5%5D=6k&s-qc%5BsubtypeFlat%5D%5B6%5D=atypical"),
    UlovDomovScraper("https://www.ulovdomov.cz/fe-api/find"),
    EuroBydleniScraper("https://www.eurobydleni.cz/search-form"),
    RealingoScraper("https://www.realingo.cz/graphql")
]

REMEMBERED_OFFERS_FILE = os.getenv("REMEMBERED_OFFERS_FILE") or "remembered_offers.txt"

REFRESH_INTERVAL_MINUTES = int(os.getenv("REFRESH_INTERVAL_MINUTES") or "30")

silent_run = False
"""Pokud je true, nevypisujeme nalezené nabídky (typicky první spuštění)"""

remembered_offers: Set[str] = set()
"""Seznam URL odkazů na všechny nalezené nabídky"""


def load_remembered_offers():
    with open(REMEMBERED_OFFERS_FILE) as file:
        for line in file:
            remembered_offers.add(line.strip())


def remember_new_offers(offers: List[ApartmentRentalOffer]):
    with open(REMEMBERED_OFFERS_FILE, 'a+') as file_object:
        for offer in offers:
            remembered_offers.add(offer.link)
            file_object.write(offer.link + os.linesep)


def process_latest_offers():
    global silent_run

    new_offers: List[ApartmentRentalOffer] = []
    for scraper in SCRAPERS:
        try:
            for offer in scraper.get_latest_offers():
                if offer.link not in remembered_offers:
                    new_offers.append(offer)
        except Exception:
            error_message = traceback.format_exc()
            # TODO odešli výjimku na Discord
            traceback.print_exc()

    remember_new_offers(new_offers)

    logging.info("Offers fetched (new: " + str(len(new_offers)) + ")")

    if silent_run:
        logging.info("No previous offers remembered, first fetch is running silently")
        silent_run = False
        return set()

    # TODO pošli všechny nabídky z `new_offers` na Discord


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    try:
        load_remembered_offers()
    except FileNotFoundError:
        silent_run = True

    # Spuštění funkce každých x sekund
    # https://stackoverflow.com/a/25251804
    start_time = time.time()
    while True:
        process_latest_offers()
        time.sleep(60.0 * REFRESH_INTERVAL_MINUTES - ((time.time() - start_time) % (60.0 * REFRESH_INTERVAL_MINUTES)))

