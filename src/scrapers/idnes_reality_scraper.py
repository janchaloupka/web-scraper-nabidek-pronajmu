import re
from typing import List
from scrapers.generic_apartment_rental_scraper import ApartmentRentalOffer, GenericApartmentRentalScraper
import requests
from bs4 import BeautifulSoup


class IdnesRealityScraper(GenericApartmentRentalScraper):

    def get_latest_offers(self) -> List[ApartmentRentalOffer]:
        request = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(request.text, 'html.parser')

        items: List[ApartmentRentalOffer] = []

        offers = soup.find(id="snippet-s-result-articles")
        for item in offers.find_all("div", {"class": "c-products__item"}):

            if "c-products__item-advertisment" in item.get("class"):
                continue

            items.append(ApartmentRentalOffer(
                link = item.find("a", {"class": "c-products__link"}).get('href'),
                description = ' '.join(item.find("h2", {"class": "c-products__title"}).get_text().strip().splitlines()),
                location = item.find("p", {"class": "c-products__info"}).get_text().strip(),
                price = int(re.sub(r"[^\d]", "", item.find("p", {"class": "c-products__price"}).get_text()))
            ))

        return items
