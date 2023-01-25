import re
import requests
from typing import List
from scrapers.scraper_base import ScraperBase
from scrapers.rental_offer import RentalOffer
from urllib.parse import urljoin
from bs4 import BeautifulSoup


class ScraperRemax(ScraperBase):

    query_url = "https://www.remax-czech.cz/reality/vyhledavani/?regions%5B116%5D%5B3702%5D=on&sale=2&types%5B4%5D%5B4%5D=on&types%5B4%5D%5B11%5D=on&types%5B4%5D%5B16%5D=on&types%5B4%5D%5B17%5D=on&order_by_published_date=0"
    name = "Remax"
    logo_url = "https://www.remax-czech.cz/apple-touch-icon.png"
    color = 0x003DA5


    def get_latest_offers(self) -> List[RentalOffer]:
        request = requests.get(self.query_url, headers=self.headers)
        soup = BeautifulSoup(request.text, 'html.parser')

        items: List[RentalOffer] = []

        for item in soup.select("#list .container-fluid .pl-items .pl-items__item"):
            items.append(RentalOffer(
                scraper = self,
                link = urljoin(self.query_url, item.get('data-url')),
                description = item.get("data-title"),
                location = re.sub(r"\s+", " ", item.get("data-display-address")),
                price = int(re.sub(r"[^\d]", "", item.get("data-price")) or "0"),
                image_url = item.get("data-img")
            ))

        return items
