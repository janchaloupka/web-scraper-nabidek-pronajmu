import traceback
from typing import List
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


def fetch_latest_offers() -> List[ApartmentRentalOffer]:
    """Získá všechny nejnovější nabídky z dostupných serverů

    Returns:
        List[ApartmentRentalOffer]: Seznam nabídek
    """

    offers: List[ApartmentRentalOffer] = []
    for scraper in SCRAPERS:
        try:
            for offer in scraper.get_latest_offers():
                offers.append(offer)
        except Exception:
            traceback.print_exc()
            error_message = traceback.format_exc()
            # TODO odešli výjimku na Discord

    return offers
