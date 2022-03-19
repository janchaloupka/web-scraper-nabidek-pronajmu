from typing import List
from scrapers.generic_apartment_rental_scraper import ApartmentRentalOffer, GenericApartmentRentalScraper
from xml.etree import ElementTree
import requests
import re


class SrealityScraper(GenericApartmentRentalScraper):

    def get_latest_offers(self) -> List[ApartmentRentalOffer]:
        request = requests.get(self.url)
        request.encoding = 'utf-8'

        tree = ElementTree.fromstring(request.text)
        namespaces = {"rss": "http://purl.org/rss/1.0/"}

        items: List[ApartmentRentalOffer] = []

        for item in tree.findall("rss:channel/rss:item", namespaces):
            loc_and_price = item.find("rss:description", namespaces).text.split(",", maxsplit=1)

            items.append(ApartmentRentalOffer(
                link = item.find("rss:link", namespaces).text,
                description = item.find("rss:title", namespaces).text,
                location = loc_and_price[1].strip(),
                price = int(re.sub(r"[^\d]", "", loc_and_price[0]))
            ))

        return items
