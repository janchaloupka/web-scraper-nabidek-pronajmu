import logging
from typing import Optional
from urllib.parse import urlencode, urljoin

import requests
from bs4 import BeautifulSoup

from config import config
from scrapers.rental_offer import RentalOffer
from scrapers.scraper_base import ScraperBase


class ScraperBazos(ScraperBase):

    name = "BAZOS"
    logo_url = "https://play-lh.googleusercontent.com/EPQt7rfipj_vji4uIkVo43g7OJLNc-NH6FpT_HuiJkgHbyi_-Biossm0SnOd1UQfrdw=w240-h480-rw"
    color = 0xFFA500

    # Bazoš skupina (rubrika) použitá pro vyhledávání, viz BAZOS_GROUP v .env.
    # "www" znamená hledání napříč všemi rubrikami.
    ALL_GROUPS = "www"

    def _get_search_params(self) -> dict[str, str]:
        return {
            "hledat": config.bazos_searchstring,
            "hlokalita": config.bazos_location,
            "humkreis": config.bazos_radius,
            "cenaod": config.bazos_price_from,
            "cenado": config.bazos_price_to,
        }

    def _get_base_url(self) -> str:
        return "https://{}.bazos.cz/".format(config.bazos_group)

    def build_response(self) -> Optional[requests.Response]:
        params = self._get_search_params()

        # Pokud není nastaven žádný bazoš parametr, scraper je neaktivní
        if not any(value.strip() for value in params.values()):
            logging.debug("BAZOS: no search parameters configured, skipping")
            return None

        base_url = self._get_base_url()

        # Dotaz je stavěn přímo na doménu zvolené skupiny (např. https://reality.bazos.cz/),
        # aby se nemusely dodatečně filtrovat výsledky z ostatních rubrik.
        # Pozor: query string se u rubrik liší od celobazošového vyhledávání na www.bazos.cz/search.php
        if config.bazos_group == self.ALL_GROUPS:
            url = urljoin(base_url, "search.php") + "?" + urlencode(params)
        else:
            params = {**params, "rubriky": config.bazos_group, "Submit": "Hledat", "kitx": "ano"}
            url = base_url + "?" + urlencode(params)

        logging.debug("BAZOS request: %s", url)

        return requests.get(url, headers=self.headers)

    def get_latest_offers(self) -> list[RentalOffer]:
        response = self.build_response()
        if response is None:
            return []

        soup = BeautifulSoup(response.text, 'html.parser')
        base_url = self._get_base_url()

        items: list[RentalOffer] = []

        for item in soup.select(".inzeraty"):
            image = item.find("img", "obrazek")
            price = item.find("div", "inzeratycena")
            about = item.find("div", "popis")
            heading = item.find("h2", "nadpis")

            items.append(RentalOffer(
                scraper=self,
                # Na doménách rubrik jsou odkazy relativní, na www.bazos.cz absolutní
                link=urljoin(base_url, heading.a.get("href")),
                title=heading.a.get_text() or "Chybí titulek",
                location=about.getText() or "Chybí popis",
                price=price.b.get_text() or "0",
                image_url=image.get("src")
            ))

        return items
