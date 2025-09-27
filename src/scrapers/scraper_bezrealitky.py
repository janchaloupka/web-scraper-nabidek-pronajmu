""" Scraper for BezRealitky.cz
author: Mark Barzali
"""

import json
import logging
from abc import ABC as abstract
from typing import ClassVar

from disposition import Disposition
from scrapers.scraper_base import ScraperBase
from scrapers.rental_offer import RentalOffer
import requests


class ScraperBezrealitky(ScraperBase):

    name = "BezRealitky"
    logo_url = "https://www.bezrealitky.cz/manifest-icon-192.maskable.png"
    color = 0x00CC00
    base_url = "https://www.bezrealitky.cz"
    file: ClassVar[str] = "./graphql/bezrealitky.json"

    API: ClassVar[str] = "https://api.bezrealitky.cz/"
    OFFER_TYPE: ClassVar[str] = "PRONAJEM"
    ESTATE_TYPE: ClassVar[str] = "BYT"
    BRNO: ClassVar[str] = "R438171"

    class Routes(abstract):
        GRAPHQL: ClassVar[str] = "graphql/"
        OFFERS: ClassVar[str] = "nemovitosti-byty-domy/"

    disposition_mapping = {
        Disposition.FLAT_1KK: "DISP_1_KK",
        Disposition.FLAT_1: "DISP_1_1",
        Disposition.FLAT_2KK: "DISP_2_KK",
        Disposition.FLAT_2: "DISP_2_1",
        Disposition.FLAT_3KK: "DISP_3_KK",
        Disposition.FLAT_3: "DISP_3_1",
        Disposition.FLAT_4KK: "DISP_4_KK",
        Disposition.FLAT_4: "DISP_4_1",
        Disposition.FLAT_5_UP: None,
        Disposition.FLAT_OTHERS: None,
    }

    disposition_reverse_mapping = {
        "DISP_1_KK": "1kk",
        "DISP_1_1": "1+1",
        "DISP_2_KK": "2kk",
        "DISP_2_1": "2+1",
        "DISP_3_KK": "3kk",
        "DISP_3_1": "3+1",
        "DISP_4_KK": "4kk",
        "DISP_4_1": "4+1",
    }

    def __init__(self, dispositions: Disposition):
        super().__init__(dispositions)
        self._read_config()
        self._patch_config()

    def _read_config(self) -> None:
        with open(ScraperBezrealitky.file, "r") as file:
            self._config = json.load(file)

    def _patch_config(self):
        match = {
            "estateType": self.ESTATE_TYPE,
            "offerType": self.OFFER_TYPE,
            "disposition": self.get_dispositions_data(),
            "regionOsmIds": [self.BRNO],
            "locale": "CS",
        }
        self._config["variables"].update(match)

    @staticmethod
    def _create_link_to_offer(item: dict) -> str:
        return f"{ScraperBezrealitky.base_url}/{ScraperBezrealitky.Routes.OFFERS}{item}"

    def build_response(self) -> requests.Response:        
        return requests.post(
            url=f"{ScraperBezrealitky.API}{ScraperBezrealitky.Routes.GRAPHQL}",
            json=self._config,
            headers=self.headers
        )

    def get_latest_offers(self) -> list[RentalOffer]:
        response = self.build_response().json()
        adverts = response.get("data", {}).get("listAdverts", {}).get("list", [])

        offers: list[RentalOffer] = []
        for item in adverts:
            location = item.get("address", "")
            disposition_key = item.get("disposition", "")
            disposition = self.disposition_reverse_mapping.get(disposition_key, disposition_key)
            surface = item.get("surface", "")
            title_parts = [disposition, f"{surface} m²" if surface else ""]
            title = " ".join(filter(None, title_parts)) or "BezRealitky"
            price = item.get("price", 0)
            image_url = item.get("mainImage", {}).get("url", "")

            offers.append(
                RentalOffer(
                    scraper=self,
                    link=self._create_link_to_offer(item.get("uri", "")),
                    title=title,
                    location=location,
                    price=price,
                    image_url=image_url,
                )
            )
        return offers
