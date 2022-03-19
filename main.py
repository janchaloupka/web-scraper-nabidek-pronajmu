#!/usr/bin/evn python3

import traceback
from typing import List, Set
from scrapers.euro_bydleni_scraper import EuroBydleniScraper
from scrapers.generic_apartment_rental_scraper import ApartmentRentalOffer, GenericApartmentRentalScraper
from scrapers.idnes_reality_scraper import IdnesRealityScraper
from scrapers.realingo_scraper import RealingoScraper
from scrapers.sreality_scraper import SrealityScraper
from scrapers.ulov_domov_scraper import UlovDomovScraper

if __name__ != "__main__":
    exit(0)

FOUND_OFFERS_FILE_PATH = "found_offers.txt"

found_offers: Set[str] = set()
with open(FOUND_OFFERS_FILE_PATH) as file:
    for line in file:
        found_offers.add(line.strip())


def add_to_found_offers(offer: ApartmentRentalOffer):
    found_offers.add(offer.link)
    with open(FOUND_OFFERS_FILE_PATH, 'a') as file_object:
        file_object.write(offer.link)

def new_offer(offer: ApartmentRentalOffer):
    add_to_found_offers(offer)
    # TODO pošli na discord

scrapers: List[GenericApartmentRentalScraper] = [
    SrealityScraper("https://www.sreality.cz/api/cs/v2/estates/rss?category_main_cb=1&category_sub_cb=7|11|10|8|12|9|16&category_type_cb=2&locality_district_id=72&locality_region_id=14&sort=0"),
    IdnesRealityScraper("https://reality.idnes.cz/s/pronajem/byty/brno-mesto/?s-qc%5BsubtypeFlat%5D%5B0%5D=31&s-qc%5BsubtypeFlat%5D%5B1%5D=4k&s-qc%5BsubtypeFlat%5D%5B2%5D=41&s-qc%5BsubtypeFlat%5D%5B3%5D=5k&s-qc%5BsubtypeFlat%5D%5B4%5D=51&s-qc%5BsubtypeFlat%5D%5B5%5D=6k&s-qc%5BsubtypeFlat%5D%5B6%5D=atypical"),
    UlovDomovScraper("https://www.ulovdomov.cz/fe-api/find"),
    EuroBydleniScraper("https://www.eurobydleni.cz/search-form"),
    RealingoScraper("https://www.realingo.cz/graphql")
]

for scraper in scrapers:
    try:
        for offer in scraper.get_latest_offers():
            if offer.link not in found_offers:
                new_offer(offer)
    except Exception:
        error_message = traceback.format_exc()
        # TODO odešli eksepšn na Discord
        traceback.print_exc()
