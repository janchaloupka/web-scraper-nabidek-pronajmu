import re
import requests
from typing import List
from scrapers.scraper_base import ScraperBase
from scrapers.rental_offer import RentalOffer
from urllib.parse import urljoin
from bs4 import BeautifulSoup


class ScraperEuroBydleni(ScraperBase):

    name = "Eurobydlení"
    logo_url = "https://files.janchaloupka.cz/eurobydleni.png"
    color = 0xFA0F54

    cookies = {"listing-sort": "sort-added"}
    request_data = {
        "sql[advert_type_eu][]": 7,
        "sql[advert_subtype_eu][]": [19, 21, 22, 202, 256],
        "sql[advert_function_eu][]": 3,
        "sql[advert_price_min]": "",
        "sql[advert_price_max]": "",
        "sql[usable_area_min]": "",
        "sql[usable_area_max]": "",
        "sql[estate_area_min]": "",
        "sql[estate_area_max]": "",
        "sql[locality][locality][input]": "",
        "sql[locality][locality][city]": "",
        "sql[locality][locality][zip_code]": "",
        "sql[locality][locality][types]": "",
        "sql[locality][location][lat]": "",
        "sql[locality][location][lng]": "",
        "sql[locality][viewport][south]": "",
        "sql[locality][viewport][west]": "",
        "sql[locality][viewport][north]": "",
        "sql[locality][viewport][east]": "",
        "sql[locality_kraj_kod][]": 116,
        "sql[locality_okres_kod][116][3702]": 3702,
        "sql[poptavka][jmeno]": "",
        "sql[poptavka][prijmeni]": "",
        "sql[poptavka][email]": "",
        "sql[poptavka][telefon]": ""
    }


    def get_latest_offers(self) -> List[RentalOffer]:
        request = requests.post(self.url, headers=self.headers, cookies=self.cookies, data=self.request_data)
        request.encoding = "utf-8"
        soup = BeautifulSoup(request.text, 'html.parser')

        items: List[RentalOffer] = []

        offers = soup.find(id="properties-box")
        for item in offers.find_all("li", {"class": "list-items__item"}):

            image_container = item.find("ul", {"class": "list-items__item__image__wrap"})
            content = item.find("div", {"class": "list-items__content__1"})
            title = content.find("h2", {"class": "list-items__item__title"})
            details = content.find_all("li")

            items.append(RentalOffer(
                scraper = self,
                link = urljoin(self.url, title.find("a").get('href')),
                description = title.get_text().strip(),
                location = details[1].get_text().strip(),
                price = int(re.sub(r"[^\d]", "", details[0].get_text())),
                image_url = "https:" + image_container.find("img").get("src")
            ))

        return items
