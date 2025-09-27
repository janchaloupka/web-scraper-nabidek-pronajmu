import functools
import operator
from pathlib import Path

import environ
from dotenv import load_dotenv

from disposition import Disposition

load_dotenv(".env")

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

def optional_int_converter(value: str):
    return int(value) if value and value.strip() else None


@environ.config(prefix="")
class Config:
    debug: bool = environ.bool_var()
    found_offers_file: Path = environ.var(converter=Path)
    refresh_interval_daytime_minutes: int = environ.var(converter=int)
    refresh_interval_nighttime_minutes: int = environ.var(converter=int)
    dispositions: Disposition = environ.var(converter=dispositions_converter)
    embed_batch_size: int = environ.var(converter=int, default=10)
    min_price: int | None = environ.var(converter=optional_int_converter, default=None)
    max_price: int | None = environ.var(converter=optional_int_converter, default=None)

    @environ.config()
    class Discord:
        token = environ.var(default=None)
        offers_channel = environ.var(converter=optional_int_converter, default=None)
        dev_channel = environ.var(converter=optional_int_converter, default=None)

    @environ.config()
    class Telegram:
        token = environ.var(default=None)
        chat_id = environ.var(default=None)

    bot_type: str = environ.var()
    discord: Discord = environ.group(Discord)
    telegram: Telegram = environ.group(Telegram)

config: Config = Config.from_environ()
