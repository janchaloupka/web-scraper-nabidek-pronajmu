import functools
import operator
import os
from pathlib import Path

import environ
from dotenv import load_dotenv

from disposition import Disposition

load_dotenv(".env")

app_env = os.getenv("APP_ENV")
if app_env:
    load_dotenv(".env." + app_env, override=True)

load_dotenv(".env.local", override=True)

_str_to_disposition_map = {
    "1+kk": Disposition.FLAT_1KK,
    "1+1": Disposition.FLAT_1,
    "2+kk": Disposition.FLAT_2KK,
    "2+1": Disposition.FLAT_2,
    "3+kk": Disposition.FLAT_3KK,
    "3+1": Disposition.FLAT_3,
    "4+kk": Disposition.FLAT_4KK,
    "4+1": Disposition.FLAT_4,
    "5++": Disposition.FLAT_5_UP,
    "others": Disposition.FLAT_OTHERS
}

def dispositions_converter(raw_disps: str):
    return functools.reduce(operator.or_, map(lambda d: _str_to_disposition_map[d], raw_disps.split(",")), Disposition.NONE)

# Výchozí seznam scraperů (realingo je dočasně nefunkční, proto není ve výchozím seznamu)
_default_scrapers = "bravis,eurobydleni,idnesreality,realcity,remax,sreality,ulovdomov,bezrealitky,bazos"

def scrapers_converter(raw_scrapers: str) -> list[str]:
    """Převede seznam scraperů oddělených čárkou na seznam klíčů (bez mezer, malými písmeny, bez duplicit)"""
    result = []
    for name in raw_scrapers.split(","):
        name = name.strip().lower()
        if name and name not in result:
            result.append(name)
    return result


@environ.config(prefix="")
class Config:
    debug: bool = environ.bool_var()
    found_offers_file: Path = environ.var(converter=Path)
    refresh_interval_daytime_minutes: int = environ.var(converter=int)
    refresh_interval_nighttime_minutes: int = environ.var(converter=int)
    dispositions: Disposition = environ.var(converter=dispositions_converter)
    scrapers: list[str] = environ.var(converter=scrapers_converter, default=_default_scrapers)
    embed_batch_size: int = environ.var(converter=int, default=10)

    bazos_group: str = environ.var(default="reality")
    bazos_searchstring: str = environ.var(default="")
    bazos_location: str = environ.var(default="")
    bazos_radius: str = environ.var(default="")
    bazos_price_from: str = environ.var(default="")
    bazos_price_to: str = environ.var(default="")

    @environ.config()
    class Discord:
        token = environ.var()
        offers_channel = environ.var(converter=int)
        dev_channel = environ.var(converter=int)

    discord: Discord = environ.group(Discord)

config: Config = Config.from_environ()
