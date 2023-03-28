import logging
import re

import requests
from bs4 import BeautifulSoup

from disposition import Disposition
from scrapers.rental_offer import RentalOffer
from scrapers.scraper_base import ScraperBase
from scrapers.rental_offer import RentalOffer
import requests
from bs4 import BeautifulSoup


class ScraperIdnesReality(ScraperBase):

    name = "iDNES Reality"
    logo_url = "https://sta-reality2.1gr.cz/ui/image/favicons/favicon-32x32.png"
    color = 0x1D80D7

    disposition_mapping = {
        Disposition.FLAT_1KK: "s-qc%5BsubtypeFlat%5D%5B0%5D=1k",
        Disposition.FLAT_1: "s-qc%5BsubtypeFlat%5D%5B0%5D=11",
        Disposition.FLAT_2KK: "s-qc%5BsubtypeFlat%5D%5B0%5D=2k",
        Disposition.FLAT_2: "s-qc%5BsubtypeFlat%5D%5B0%5D=21",
        Disposition.FLAT_3KK: "s-qc%5BsubtypeFlat%5D%5B0%5D=3k",
        Disposition.FLAT_3: "s-qc%5BsubtypeFlat%5D%5B0%5D=31",
        Disposition.FLAT_4KK: "s-qc%5BsubtypeFlat%5D%5B0%5D=4k",
        Disposition.FLAT_4: "s-qc%5BsubtypeFlat%5D%5B0%5D=41",
        Disposition.FLAT_5_UP: (
            "s-qc%5BsubtypeFlat%5D%5B0%5D=5k",
            "s-qc%5BsubtypeFlat%5D%5B0%5D=51",
            "s-qc%5BsubtypeFlat%5D%5B0%5D=6k", # 6 a víc
        ),
        Disposition.FLAT_OTHERS: "s-qc%5BsubtypeFlat%5D%5B0%5D=atypical", # atyp
    }


    def build_response(self) -> requests.Response:
        url = "https://reality.idnes.cz/s/pronajem/byty/brno-mesto/?"
        url += "&".join(self.get_dispositions_data())

        logging.debug("iDNES reality request: %s", url)

        return requests.get(url, headers=self.headers)

    def get_latest_offers(self) -> list[RentalOffer]:
        response = self.build_response()
        soup = BeautifulSoup(response.text, 'html.parser')

        items: list[RentalOffer] = []

        offers = soup.find(id="snippet-s-result-articles")
        for item in offers.find_all("div", {"class": "c-products__item"}):

            if "c-products__item-advertisment" in item.get("class"):
                continue

            items.append(RentalOffer(
                scraper = self,
                link = item.find("a", {"class": "c-products__link"}).get('href'),
                title = ' '.join(item.find("h2", {"class": "c-products__title"}).get_text().strip().splitlines()),
                location = item.find("p", {"class": "c-products__info"}).get_text().strip(),
                price = int(re.sub(r"[^\d]", "", item.find("p", {"class": "c-products__price"}).get_text()) or "0"),
                image_url = item.find("img").get("data-src")
            ))

        return items
