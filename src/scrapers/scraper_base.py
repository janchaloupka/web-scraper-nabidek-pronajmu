from abc import abstractmethod
from typing import List
from scrapers.rental_offer import RentalOffer

class ScraperBase():
    """Hlavní třída pro získávání aktuálních nabídek pronájmu bytů z různých služeb
    """

    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36"
    headers = {"User-Agent": user_agent}

    @property
    @abstractmethod
    def query_url(self) -> str:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def logo_url(self) -> str:
        pass

    @property
    @abstractmethod
    def color(self) -> int:
        pass


    @abstractmethod
    def get_latest_offers() -> List[RentalOffer]:
        """Načte a vrátí seznam nejnovějších nabídek bytů k pronájmu z dané služby

        Raises:
            NotImplementedError: Pokud potomek neimplementuje tuto metodu

        Returns:
            List[RentalOffer]: Seznam nabízených bytů k pronájmu
        """
        raise NotImplementedError("Fetching new results is not implemeneted")
