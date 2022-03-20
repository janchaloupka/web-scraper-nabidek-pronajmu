import logging
import traceback
from typing import List
from config import *
from scrapers.rental_offer import RentalOffer
from scrapers.scraper_euro_bydleni import ScraperEuroBydleni
from scrapers.scraper_base import ScraperBase
from scrapers.scraper_idnes_reality import ScraperIdnesReality
from scrapers.scraper_realingo import ScraperRealingo
from scrapers.scraper_sreality import ScraperSreality
from scrapers.scraper_ulov_domov import ScraperUlovDomov


SCRAPERS: List[ScraperBase] = [
    ScraperEuroBydleni("https://www.eurobydleni.cz/search-form"),
    ScraperIdnesReality("https://reality.idnes.cz/s/pronajem/byty/brno-mesto/?s-qc%5BsubtypeFlat%5D%5B0%5D=31&s-qc%5BsubtypeFlat%5D%5B1%5D=4k&s-qc%5BsubtypeFlat%5D%5B2%5D=41&s-qc%5BsubtypeFlat%5D%5B3%5D=5k&s-qc%5BsubtypeFlat%5D%5B4%5D=51&s-qc%5BsubtypeFlat%5D%5B5%5D=6k&s-qc%5BsubtypeFlat%5D%5B6%5D=atypical"),
    ScraperRealingo("https://www.realingo.cz/graphql"),
    ScraperSreality("https://www.sreality.cz/api/cs/v2/estates?category_main_cb=1&category_sub_cb=7|11|10|8|12|9|16&category_type_cb=2&locality_district_id=72&locality_region_id=14&per_page=20"),
    ScraperUlovDomov("https://www.ulovdomov.cz/fe-api/find")
]


def fetch_latest_offers() -> List[RentalOffer]:
    """Získá všechny nejnovější nabídky z dostupných serverů

    Returns:
        List[RentalOffer]: Seznam nabídek
    """

    offers: List[RentalOffer] = []
    for scraper in SCRAPERS:
        try:
            for offer in scraper.get_latest_offers():
                offers.append(offer)
        except Exception:
            logging.error(traceback.format_exc())

    return offers
