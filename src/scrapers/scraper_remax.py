import logging
import re
import requests
from typing import List
from disposition import Disposition
from scrapers.scraper_base import ScraperBase
from scrapers.rental_offer import RentalOffer
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from utils import flatten

class ScraperRemax(ScraperBase):

    name = "Remax"
    logo_url = "https://www.remax-czech.cz/apple-touch-icon.png"
    color = 0x003DA5

    disposition_mapping = {
        Disposition.FLAT_1KK: "&types%5B4%5D%5B2%5D=on",
        Disposition.FLAT_2KK: "&types%5B4%5D%5B3%5D=on",
        Disposition.FLAT_3KK: "&types%5B4%5D%5B4%5D=on",
        Disposition.FLAT_4KK: "&types%5B4%5D%5B5%5D=on",
        Disposition.FLAT_1: "&types%5B4%5D%5B9%5D=on",
        Disposition.FLAT_2: "&types%5B4%5D%5B10%5D=on",
        Disposition.FLAT_3: "&types%5B4%5D%5B11%5D=on",
        Disposition.FLAT_4: "&types%5B4%5D%5B12%5D=on",
        Disposition.FLAT_5_UP: (
            "&types%5B4%5D%5B6%5D=on", # 5kk
            "&types%5B4%5D%5B7%5D=on", # 6kk
            "&types%5B4%5D%5B8%5D=on", # 7kk
            "&types%5B4%5D%5B13%5D=on", # 5+1
            "&types%5B4%5D%5B14%5D=on", # 6+1
            "&types%5B4%5D%5B15%5D=on", # 7+1
        ),
        Disposition.FLAT_OTHERS: (
            "&types%5B4%5D%5B16%5D=on", # atyp
            "&types%5B4%5D%5B17%5D=on", # jiný
        ),
    }


    def build_response(self) -> requests.Response:
        url = "https://www.remax-czech.cz/reality/vyhledavani/?regions%5B116%5D%5B3702%5D=on&sale=2"
        url += "".join(flatten([self.disposition_mapping[d] for d in self.disposition]))
        url += "&order_by_published_date=0"

        logging.info("Remax request: %s", url)

        return requests.get(url, headers=self.headers)

    def get_latest_offers(self) -> List[RentalOffer]:
        response = self.build_response()
        soup = BeautifulSoup(response.text, 'html.parser')

        items: List[RentalOffer] = []

        for item in soup.select("#list .container-fluid .pl-items .pl-items__item"):
            items.append(RentalOffer(
                scraper = self,
                link = urljoin(self.query_url, item.get('data-url')),
                title = item.get("data-title"),
                location = re.sub(r"\s+", " ", item.get("data-display-address")),
                price = int(re.sub(r"[^\d]", "", item.get("data-price")) or "0"),
                image_url = item.get("data-img")
            ))

        return items
