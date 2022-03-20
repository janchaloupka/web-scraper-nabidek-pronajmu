from dataclasses import dataclass

@dataclass
class RentalOffer:
    """Nabídka pronájmu bytu"""

    link: str
    """URL adresa na nabídku"""

    description: str
    """Popis nabídky (nejčastěji počet pokojů, výměra)"""

    location: str
    """Lokace bytu (městská část, ulice)"""

    price: int
    """Cena pronájmu za měsíc bez poplatků a energií"""

    image_url: str
    """Náhledový obrázek nabídky"""

    scraper: 'ScraperBase'
    """Odkaz na instanci srapera, ze kterého tato nabídka pochází"""
