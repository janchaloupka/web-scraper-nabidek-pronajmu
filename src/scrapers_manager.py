import logging
import traceback

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
from scrapers.scraper_bazos import ScraperBazos


# Mapování hodnot env proměnné SCRAPERS na jednotlivé scrapery
scrapers_map: dict[str, type[ScraperBase]] = {
    "bravis": ScraperBravis,
    "eurobydleni": ScraperEuroBydleni,
    "idnesreality": ScraperIdnesReality,
    "realcity": ScraperRealcity,
    "realingo": ScraperRealingo,
    "remax": ScraperRemax,
    "sreality": ScraperSreality,
    "ulovdomov": ScraperUlovDomov,
    "bezrealitky": ScraperBezrealitky,
    "bazos": ScraperBazos,
}


def create_scrapers(dispositions: Disposition, scraper_names: list[str] = None) -> list[ScraperBase]:
    """Vytvoří instance scraperů podle konfigurace

    Args:
        dispositions (Disposition): Požadované dispozice bytu
        scraper_names (list[str], optional): Seznam klíčů scraperů (viz scrapers_map), které se mají použít.
            Pokud není zadán, použije se hodnota z env proměnné SCRAPERS.

    Raises:
        ValueError: Pokud seznam obsahuje neznámý scraper

    Returns:
        list[ScraperBase]: Seznam aktivních scraperů
    """
    if scraper_names is None:
        scraper_names = config.scrapers

    unknown = [name for name in scraper_names if name not in scrapers_map]
    if unknown:
        raise ValueError("Unknown scraper(s) in SCRAPERS: {}. Available scrapers: {}".format(
            ", ".join(unknown), ", ".join(scrapers_map.keys())))

    return [scrapers_map[name](dispositions) for name in scraper_names]


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

    return offers
