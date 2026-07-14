import os
import re
from io import BytesIO

import imagehash
import requests
from PIL import Image

from scrapers.rental_offer import RentalOffer


class TextDedupFilter:
    """Filtr duplikátů na základě dispozice, výměry a ceny (pouze v paměti)"""

    def __init__(self):
        self._fingerprints: dict[str, RentalOffer] = {}

    @staticmethod
    def _fingerprint(offer: RentalOffer) -> str:
        title = offer.title.lower()
        disposition = re.search(r'\d\+(?:kk|\d)', title)
        size = re.search(r'(\d+)\s*m', title)
        price = re.sub(r'[^\d]', '', str(offer.price))
        return f"{disposition.group() if disposition else ''}|{size.group(1) if size else ''}|{price}"

    def is_duplicate(self, offer: RentalOffer) -> bool:
        fp = self._fingerprint(offer)
        if fp.startswith('||') or fp.startswith('|'):
            return False
        return fp in self._fingerprints

    def register(self, offer: RentalOffer):
        fp = self._fingerprint(offer)
        if fp not in self._fingerprints:
            self._fingerprints[fp] = offer


class ImageDedupFilter:
    """Filtr duplikátů na základě perceptuálního hashe obrázku (pouze v paměti)"""

    _headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"}

    def __init__(self, threshold: int = 8):
        self.threshold = threshold
        self._hashes: list[tuple[imagehash.ImageHash, RentalOffer]] = []
        self._cache: dict[str, imagehash.ImageHash | None] = {}

    def _fetch_hash(self, image_url: str) -> imagehash.ImageHash | None:
        try:
            response = requests.get(image_url, headers=self._headers, timeout=10)
            img = Image.open(BytesIO(response.content))
            return imagehash.phash(img)
        except Exception:
            return None

    def _get_hash(self, image_url: str) -> imagehash.ImageHash | None:
        if image_url not in self._cache:
            self._cache[image_url] = self._fetch_hash(image_url)
        return self._cache[image_url]

    def is_duplicate(self, offer: RentalOffer) -> bool:
        if not offer.image_url:
            return False
        h = self._get_hash(offer.image_url)
        if h is None:
            return False
        for existing_hash, _ in self._hashes:
            if abs(h - existing_hash) <= self.threshold:
                return True
        return False

    def register(self, offer: RentalOffer):
        if not offer.image_url:
            return
        h = self._get_hash(offer.image_url)
        if h is not None:
            self._hashes.append((h, offer))


class OffersStorage:
    """Úložiště dříve nalezených nabídek"""

    def __init__(self, path: str):
        self.path = path
        """Cesta k uloženým odkazům"""

        self.first_time = False
        """Neproběhl pokus o uložení nabídek (soubor neexistuje)"""

        self._links: set[str] = set()
        """Seznam URL odkazů na všechny nalezené nabídky"""

        self._text_filter = TextDedupFilter()
        self._image_filter = ImageDedupFilter()

        try:
            with open(self.path) as file:
                for line in file:
                    self._links.add(line.strip())
        except FileNotFoundError:
            self.first_time = True

    def contains(self, offer: RentalOffer) -> bool:
        """Objevila se nabídka již dříve?

        Args:
            offer (RentalOffer): Nabídka

        Returns:
            bool: Jde o starou nabídku
        """
        if offer.link in self._links:
            return True

        # Nejprve rychlý textový filtr (dispozice+výměra+cena),
        # poté nákladnější porovnání obrázků pouze pro neshody
        if self._text_filter.is_duplicate(offer):
            return True
        if self._image_filter.is_duplicate(offer):
            return True

        self._text_filter.register(offer)
        self._image_filter.register(offer)
        return False

    def save_offers(self, offers: list[RentalOffer]):
        """Uložit nabídky jako nalezené

        Args:
            offers (list[RentalOffer]): Nalezené nabídky
        """
        with open(self.path, 'a+') as file_object:
            for offer in offers:
                self._links.add(offer.link)
                self._text_filter.register(offer)
                self._image_filter.register(offer)
                file_object.write(offer.link + os.linesep)

            self.first_time = False
