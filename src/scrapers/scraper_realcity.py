import re
from typing import List
from scrapers.scraper_base import ScraperBase
from scrapers.rental_offer import RentalOffer
import requests
from bs4 import BeautifulSoup


class ScraperRealcity(ScraperBase):

    query_url = "https://www.realcity.cz/pronajem-bytu/brno-4892/3-kk?sp=%7B%22prefLoc%22%3A%5B4892%5D%2C%22mloc%22%3A%7B%22name%22%3A%22Brno%22%7D%2C%22withImage%22%3Atrue%2C%22transactionTypes%22%3A%5B%22rent%22%5D%2C%22propertyTypes%22%3A%5B%7B%22propertyType%22%3A%22flat%22%2C%22options%22%3A%7B%22disposition%22%3A%5B%223%2Bkk%22%2C%223%2B1%22%2C%224%2Bkk%22%2C%224%2B1%22%5D%7D%7D%5D%7D"
    name = "REALCITY"
    logo_url = "https://files.janchaloupka.cz/realcity.png"
    color = 0xB60D1C


    def get_latest_offers(self) -> List[RentalOffer]:
        request = requests.get(self.query_url, headers=self.headers)
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
