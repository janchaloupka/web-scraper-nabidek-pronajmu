import re
from typing import List
from scrapers.scraper_base import ScraperBase
from scrapers.rental_offer import RentalOffer
import requests
from bs4 import BeautifulSoup


class ScraperRealcity(ScraperBase):

    name = "REALCITY"
    logo_url = "https://files.janchaloupka.cz/realcity.png"
    color = 0x1D80D7 # TODO


    def get_latest_offers(self) -> List[RentalOffer]:
        request = requests.get(self.url, headers=self.headers)
        soup = BeautifulSoup(request.text, 'html.parser')

        items: List[RentalOffer] = []

        offers = soup.find(id="rc-advertise-result")

        for item in offers.find_all("div", {"class": "media advertise item"}):

            items.append(RentalOffer(
                scraper = self,
                link = "https://www.realcity.cz" + item.find("div", {"class": "title"}).a.get("href"),
                description = ' '.join(item.find("div", {"class": "title"}).a.get_text().strip().splitlines()),
                location = item.find("div", {"class": "address"}).get_text().strip(),
                price = int(re.sub(r"[^\d]", "", item.find("div", {"class": "price"}).span.get_text())),
                image_url = "https:" + item.find("div", {"class": "pull-left image"}).a.img.get('src')
            ))

        return items
