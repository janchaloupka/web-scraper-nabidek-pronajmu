from typing import List
from scrapers.scraper_base import ScraperBase
from scrapers.rental_offer import RentalOffer
import requests


class ScraperUlovDomov(ScraperBase):

    query_url = "https://www.ulovdomov.cz/fe-api/find/seperated-offers-within-bounds"
    name = "UlovDomov"
    logo_url = "https://www.ulovdomov.cz/favicon.png"
    color = 0xFFFFFF

    json_request = {
        "acreage_from": "",
        "acreage_to": "",
        "added_before": "",
        "banner_panel_width_type": 480,
        "bounds": {
            "north_east": {
                "lat": 49.294485,
                "lng": 16.727853
            },
            "south_west": {
                "lat": 49.109655,
                "lng": 16.428068
            }
        },
        "conveniences": [],
        "dispositions": [6, 7, 16],
        "furnishing": [],
        "is_price_commision_free": None,
        "limit": 20,
        "offer_type_id": None,
        "page": 1,
        "price_from": "",
        "price_to": "",
        "query": "",
        "sort_by": "date:desc",
        "sticker": None
    }


    def disposition_id_to_string(self, id) -> str:
        return {
            1: "garsonky",
            2: "1+kk",
            3: "1+1",
            4: "2+kk",
            5: "2+1",
            6: "3+kk",
            7: "3+1",
            8: "4+kk",
            9: "4+1",
            10: "5+kk",
            11: "5+1",
            12: "6+kk",
            13: "6+1",
            14: "7+kk",
            15: "7+1",
            16: "atypický",
            29: "domu",
            24: "spolubydlení (1 lůžkový)",
            25: "spolubydlení (2 lůžkový)",
            26: "spolubydlení (3 lůžkový)",
            27: "spolubydlení (4+ lůžkový)",
            28: "spolubydlení (samostatný pokoj)",
            "shared_room": "spolubydlení",
            "5_and_more": "5 a více"
        }.get(id, "")

    def get_latest_offers(self) -> List[RentalOffer]:
        request = requests.post(self.query_url, headers=self.headers, json=self.json_request)
        response = request.json()

        items: List[RentalOffer] = []
        for offer in response["offers"]:
            items.append(RentalOffer(
                scraper = self,
                link = offer["absolute_url"],
                # TODO "Pronájem" podle ID?
                description = "Pronájem " + self.disposition_id_to_string(offer["disposition_id"]) + " " + str(offer["acreage"]) + " m²",
                location = offer["street"]["label"] + ", " + offer["village"]["label"] + " - " + offer["village_part"]["label"],
                price = offer["price_rental"],
                image_url = offer["photos"][0]["path"]
            ))

        return items
