import re
from typing import List
from scrapers.scraper_base import ScraperBase
from scrapers.rental_offer import RentalOffer
import requests
from bs4 import BeautifulSoup


class ScraperIdnesReality(ScraperBase):

    query_url = "https://reality.idnes.cz/s/pronajem/byty/brno-mesto/?s-qc%5BsubtypeFlat%5D%5B0%5D=3k&s-qc%5BsubtypeFlat%5D%5B1%5D=31&s-qc%5BsubtypeFlat%5D%5B3%5D=atypical"
    name = "iDNES Reality"
    logo_url = "https://sta-reality2.1gr.cz/ui/image/favicons/favicon-32x32.png"
    color = 0x1D80D7


    def get_latest_offers(self) -> List[RentalOffer]:
        request = requests.get(self.query_url, headers=self.headers)
        soup = BeautifulSoup(request.text, 'html.parser')

        items: List[RentalOffer] = []

        offers = soup.find(id="snippet-s-result-articles")
        for item in offers.find_all("div", {"class": "c-products__item"}):

            if "c-products__item-advertisment" in item.get("class"):
                continue

            items.append(RentalOffer(
                scraper = self,
                link = item.find("a", {"class": "c-products__link"}).get('href'),
                description = ' '.join(item.find("h2", {"class": "c-products__title"}).get_text().strip().splitlines()),
                location = item.find("p", {"class": "c-products__info"}).get_text().strip(),
                price = int(re.sub(r"[^\d]", "", item.find("p", {"class": "c-products__price"}).get_text()) or "0"),
                image_url = item.find("img").get("data-src")
            ))

        return items
