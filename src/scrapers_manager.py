import logging
import traceback
import re

from config import *
from disposition import Disposition
from scrapers.rental_offer import RentalOffer
from scrapers.scraper_base import ScraperBase
from scrapers.scraper_bravis import ScraperBravis
from scrapers.scraper_euro_bydleni import ScraperEuroBydleni
from scrapers.scraper_idnes_reality import ScraperIdnesReality
from scrapers.scraper_realcity import ScraperRealcity
from scrapers.scraper_realingo import ScraperRealingo
from scrapers.scraper_remax import ScraperRemax
from scrapers.scraper_sreality import ScraperSreality
from scrapers.scraper_ulov_domov import ScraperUlovDomov
from scrapers.scraper_bezrealitky import ScraperBezrealitky


def create_scrapers(dispositions: Disposition) -> list[ScraperBase]:
    return [
        ScraperBravis(dispositions),
        ScraperEuroBydleni(dispositions),
        ScraperIdnesReality(dispositions),
        ScraperRealcity(dispositions),
        #ScraperRealingo(dispositions),
        ScraperRemax(dispositions),
        ScraperSreality(dispositions),
        ScraperUlovDomov(dispositions),
        ScraperBezrealitky(dispositions),
    ]


def extract_price_from_offer(price: int | str) -> int | None:
    if isinstance(price, int):
        return price
    
    if isinstance(price, str):
        price_match = re.search(r'[\d\s,]+', price.replace(' ', ''))
        if price_match:
            price_str = price_match.group().replace(',', '').replace(' ', '')
            try:
                return int(price_str)
            except ValueError:
                pass
    
    return None


def filter_offers_by_price(offers: list[RentalOffer], min_price: int | None = None, max_price: int | None = None) -> list[RentalOffer]:
    if min_price is None and max_price is None:
        return offers
    
    filtered_offers = []
    for offer in offers:
        price = extract_price_from_offer(offer.price)
        
        if price is None:
            logging.warning(f"Could not extract price from offer: {offer.price} for {offer.title}")
            continue
            
        if min_price is not None and price < min_price:
            continue
            
        if max_price is not None and price > max_price:
            continue
            
        filtered_offers.append(offer)
    
    return filtered_offers


def fetch_latest_offers(scrapers: list[ScraperBase]) -> list[RentalOffer]:
    """Získá všechny nejnovější nabídky z dostupných serverů

    Returns:
        list[RentalOffer]: Seznam nabídek
    """

    offers: list[RentalOffer] = []
    for scraper in scrapers:
        try:
            for offer in scraper.get_latest_offers():
                offers.append(offer)
        except Exception:
            logging.error(traceback.format_exc())

    offers = filter_offers_by_price(offers, config.min_price, config.max_price)
        
    return offers
