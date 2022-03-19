from abc import abstractmethod
from dataclasses import dataclass
from typing import List

@dataclass
class ApartmentRentalOffer:
    """Nabídka pronájmu bytu"""

    link: str
    """URL adresa na nabídku"""

    description: str
    """Popis nabídky (nejčastěji počet pokojů, výměra)"""

    location: str
    """Lokace bytu (městská část, ulice)"""

    price: int
    """Cena pronájmu za měsíc bez poplatků a energií"""


class GenericApartmentRentalScraper():
    """Hlavní třída pro získávání aktuálních nabídek pronájmu bytů z různých služeb
    """

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36"
    headers = {"User-Agent": user_agent}

    def __init__(self, url: str):
        self.url = url

    @abstractmethod
    def get_latest_offers() -> List[ApartmentRentalOffer]:
        """Načte a vrátí seznam nejnovějších nabídek bytů k pronájmu z dané služby

        Raises:
            NotImplementedError: Pokud potomek neimplementuje tuto metodu

        Returns:
            List[ApartmentRentalOffer]: Seznam nabízených bytů k pronájmu
        """
        raise NotImplementedError("Fetching new results is not implemeneted")
