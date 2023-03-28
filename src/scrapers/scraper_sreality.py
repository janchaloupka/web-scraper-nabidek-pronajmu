from typing import List
from scrapers.scraper_base import ScraperBase
from scrapers.rental_offer import RentalOffer
from time import time
import requests
from urllib.parse import urljoin


class ScraperSreality(ScraperBase):

    query_url = "https://www.sreality.cz/api/cs/v2/estates?category_main_cb=1&category_sub_cb=6|7|16&category_type_cb=2&locality_district_id=72&locality_region_id=14&per_page=20"
    name = "Sreality"
    logo_url = "https://www.sreality.cz/img/icons/android-chrome-192x192.png"
    color = 0xCC0000

    _category_type_to_url = {
        0: "vse",
        1: "prodej",
        2: "pronajem",
        3: "drazby"
    }

    _category_main_to_url = {
        0: "vse",
        1: "byt",
        2: "dum",
        3: "pozemek",
        4: "komercni",
        5: "ostatni"
    }

    _category_sub_to_url = {
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
            12: "6-a-vice",
            16: "atypicky",
            47: "pokoj",
            37: "rodinny",
            39: "vila",
            43: "chalupa",
            33: "chata",
            35: "pamatka",
            40: "na-klic",
            44: "zemedelska-usedlost",
            19: "bydleni",
            18: "komercni",
            20: "pole",
            22: "louka",
            21: "les",
            46: "rybnik",
            48: "sady-vinice",
            23: "zahrada",
            24: "ostatni-pozemky",
            25: "kancelare",
            26: "sklad",
            27: "vyrobni-prostor",
            28: "obchodni-prostor",
            29: "ubytovani",
            30: "restaurace",
            31: "zemedelsky",
            38: "cinzovni-dum",
            49: "virtualni-kancelar",
            32: "ostatni-komercni-prostory",
            34: "garaz",
            52: "garazove-stani",
            50: "vinny-sklep",
            51: "pudni-prostor",
            53: "mobilni-domek",
            36: "jine-nemovitosti"
        }


    def _create_link_to_offer(self, offer) -> str:
        return urljoin(self.query_url, "/detail" +
            "/" + self._category_type_to_url[offer["seo"]["category_type_cb"]] +
            "/" + self._category_main_to_url[offer["seo"]["category_main_cb"]] +
            "/" + self._category_sub_to_url[offer["seo"]["category_sub_cb"]] +
            "/" + offer["seo"]["locality"] +
            "/" + str(offer["hash_id"]))


    def get_latest_offers(self) -> List[RentalOffer]:
        request = requests.get(self.query_url + "&tms=" + str(int(time())), headers=self.headers)
        response = request.json()

        items: List[RentalOffer] = []

        for item in response["_embedded"]["estates"]:
            # Ignorovat "tip" nabídky, které úplně neodpovídají filtrům a mění se s každým vyhledáváním
            if item["region_tip"] > 0:
                continue

            items.append(RentalOffer(
                scraper = self,
                link = self._create_link_to_offer(item),
                title = item["name"],
                location = item["locality"],
                price = item["price_czk"]["value_raw"],
                image_url = item["_links"]["image_middle2"][0]["href"]
            ))

        return items
