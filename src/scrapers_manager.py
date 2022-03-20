import logging
import traceback
from typing import List
from config import *
from scrapers.rental_offer import RentalOffer
from scrapers.scraper_bravis import ScraperBravis
from scrapers.scraper_euro_bydleni import ScraperEuroBydleni
from scrapers.scraper_base import ScraperBase
from scrapers.scraper_idnes_reality import ScraperIdnesReality
from scrapers.scraper_realingo import ScraperRealingo
from scrapers.scraper_remax import ScraperRemax
from scrapers.scraper_sreality import ScraperSreality
from scrapers.scraper_ulov_domov import ScraperUlovDomov
from scrapers.scraper_realcity import ScraperRealcity


scrapers: List[ScraperBase] = [
    ScraperBravis(),
    ScraperEuroBydleni(),
    ScraperIdnesReality(),
    ScraperRealcity(),
    ScraperRealingo(),
    ScraperRemax(),
    ScraperSreality(),
    ScraperUlovDomov()
]


def fetch_latest_offers() -> List[RentalOffer]:
    """Získá všechny nejnovější nabídky z dostupných serverů

    Returns:
        List[RentalOffer]: Seznam nabídek
    """

    offers: List[RentalOffer] = []
    for scraper in scrapers:
        try:
            for offer in scraper.get_latest_offers():
                offers.append(offer)
        except Exception:
            logging.error(traceback.format_exc())

    return offers
