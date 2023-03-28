import logging
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from disposition import Disposition
from scrapers.rental_offer import RentalOffer
from scrapers.scraper_base import ScraperBase


class ScraperBravis(ScraperBase):

    name = "BRAVIS"
    logo_url = "https://www.bravis.cz/content/img/logo-small.png"
    color = 0xCE0020
    base_url = "https://www.bravis.cz/pronajem-bytu"


    def build_response(self) -> requests.Response:
        url = self.base_url + "?"

        if Disposition.FLAT_1KK in self.disposition or Disposition.FLAT_1 in self.disposition:
            url += "typ-nemovitosti-byt+1=&"
        if Disposition.FLAT_2KK in self.disposition or Disposition.FLAT_2 in self.disposition:
            url += "typ-nemovitosti-byt+2=&"
        if Disposition.FLAT_3KK in self.disposition or Disposition.FLAT_3 in self.disposition:
            url += "typ-nemovitosti-byt+3=&"
        if Disposition.FLAT_4KK in self.disposition or Disposition.FLAT_4 in self.disposition:
            url += "typ-nemovitosti-byt+4=&"
        if Disposition.FLAT_5_UP in self.disposition:
            url += "typ-nemovitosti-byt+5=&"

        url += "typ-nabidky=pronajem-bytu&lokalita=cele-brno&vybavenost=nezalezi&q=&action=search&s=1-20-order-0"

        logging.debug("BRAVIS request: %s", url)

        return requests.get(url, headers=self.headers)

    def get_latest_offers(self) -> list[RentalOffer]:
        response = self.build_response()
        soup = BeautifulSoup(response.text, 'html.parser')

        items: list[RentalOffer] = []

        for item in soup.select("#search > .in > .itemslist > li"):
            if item.get("class"):
                continue

            params = item.select(".params > li")

            items.append(RentalOffer(
                scraper = self,
                link = urljoin(self.base_url, item.select_one("a.main").get("href")),
                title = "Pronájem " + params[1].find("strong").get_text().strip() + ", " + params[2].find("strong").get_text().strip(),
                location = item.select_one(".location").get_text().strip(),
                price = int(re.sub(r"[^\d]", "", [text for text in item.select_one(".price").stripped_strings][0])),
                image_url = urljoin(self.base_url, item.select_one(".img > img").get("src"))
            ))

        return items
