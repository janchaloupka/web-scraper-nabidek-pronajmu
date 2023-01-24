import re
import requests
from typing import List
from scrapers.scraper_base import ScraperBase
from scrapers.rental_offer import RentalOffer
from urllib.parse import urljoin
from bs4 import BeautifulSoup


class ScraperBravis(ScraperBase):

    query_url = "https://www.bravis.cz/pronajem-bytu?typ-nemovitosti-byt+3=&typ-nemovitosti-byt+4=&typ-nabidky=pronajem-bytu&lokalita=cele-brno&vybavenost=nezalezi&q=&action=search&s=1-20-order-0"
    name = "BRAVIS"
    logo_url = "https://www.bravis.cz/content/img/logo-small.png"
    color = 0xCE0020


    def get_latest_offers(self) -> List[RentalOffer]:
        request = requests.get(self.query_url, headers=self.headers)
        soup = BeautifulSoup(request.text, 'html.parser')

        items: List[RentalOffer] = []

        for item in soup.select("#search > .in > .itemslist > li"):
            if item.get("class"):
                continue

            params = item.select(".params > li")

            items.append(RentalOffer(
                scraper = self,
                link = urljoin(self.query_url, item.select_one("a.main").get("href")),
                description = "Pronájem " + params[1].find("strong").get_text().strip() + ", " + params[2].find("strong").get_text().strip(),
                location = item.select_one(".location").get_text().strip(),
                price = int(re.sub(r"[^\d]", "", [text for text in item.select_one(".price").stripped_strings][0])),
                image_url = urljoin(self.query_url, item.select_one(".img > img").get("src"))
            ))

        return items
