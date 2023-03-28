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


@environ.config(prefix="")
class Config:
    info_debug_level: int = environ.var(converter=int, default=15)

    debug: bool = environ.bool_var()
    found_offers_file: Path = environ.var(converter=Path)
    refresh_interval_daytime_minutes: int = environ.var(converter=int)
    refresh_interval_nighttime_minutes: int = environ.var(converter=int)
    dispositions: Disposition = environ.var(converter=dispositions_converter)

    @environ.config()
    class Discord:
        token = environ.var()
        offers_channel = environ.var(converter=int)
        dev_channel = environ.var(converter=int)

    discord: Discord = environ.group(Discord)

config: Config = Config.from_environ()
