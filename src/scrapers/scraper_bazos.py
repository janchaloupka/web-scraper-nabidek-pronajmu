import logging

import requests
from bs4 import BeautifulSoup

from config import config
from scrapers.rental_offer import RentalOffer
from scrapers.scraper_base import ScraperBase
import requests
from bs4 import BeautifulSoup


class ScraperBazos(ScraperBase):

    name = "BAZOS"
    logo_url = "https://play-lh.googleusercontent.com/EPQt7rfipj_vji4uIkVo43g7OJLNc-NH6FpT_HuiJkgHbyi_-Biossm0SnOd1UQfrdw=w240-h480-rw"
    color = 0xFFA500


    def build_response(self) -> requests.Response:
        format_str = "https://www.bazos.cz/search.php?hledat={}&hlokalita={}&humkreis={}&cenaod={}&cenado={}"
        url = format_str.format(
            config.bazos_searchstring,
            config.bazos_location,
            config.bazos_radius,
            config.bazos_price_from,
            config.bazos_price_to
        )
        logging.debug("BAZOS request: %s", url)

        return requests.get(url, headers=self.headers)

    def get_latest_offers(self) -> list[RentalOffer]:
        response = self.build_response()
        soup = BeautifulSoup(response.text, 'html.parser')

        items: list[RentalOffer] = []

        for item in soup.select(".inzeraty"):
            image = item.find("img", "obrazek")
            price = item.find("div", "inzeratycena")
            about = item.find("div", "popis")

            items.append(RentalOffer(
                scraper=self,
                link=item.find("h2", "nadpis").a.get("href"),
                title=item.find("h2", "nadpis").a.get_text() or "Chybí titulek",
                location=about.getText() or "Chybí popis",
                price=price.b.get_text() or "0",
                image_url=image.get("src")
            ))

        return items
