import os
from typing import List, Set
from xmlrpc.client import boolean
from scrapers.generic_apartment_rental_scraper import ApartmentRentalOffer


class OffersStorage:
    """Úložiště dříve nalezených nabídek"""

    def __init__(self, path: str):
        self.path = path
        """Cesta k uloženým odkazům"""

        self.first_time = False
        """Neproběhl pokus o uložení nabídek (soubor neexistuje)"""

        self._links: Set[str] = set()
        """Seznam URL odkazů na všechny nalezené nabídky"""

        try:
            with open(self.path) as file:
                for line in file:
                    self._links.add(line.strip())
        except FileNotFoundError:
            self.first_time = True


    def contains(self, offer: ApartmentRentalOffer) -> bool:
        """Objevila se nabídka již dříve?

        Args:
            offer (ApartmentRentalOffer): Nabídka

        Returns:
            bool: Jde o starou nabídku
        """
        return offer.link in self._links


    def save_offers(self, offers: List[ApartmentRentalOffer]):
        """Uložit nabídky jako nalezené

        Args:
            offers (List[ApartmentRentalOffer]): Nalezené nabídky
        """
        with open(self.path, 'a+') as file_object:
            for offer in offers:
                self._links.add(offer.link)
                file_object.write(offer.link + os.linesep)

            self.first_time = True
