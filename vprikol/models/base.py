from enum import Enum
from typing import List, Union, Optional
from pydantic import BaseModel

class RatingType(str, Enum):
    ADMINS = "admins"
    ADVOCATES = "advocates"
    COMBINE_OPERATORS = "combine_operators"
    BUS_DRIVERS = "bus_drivers"
    TRACTOR_DRIVERS = "tractor_drivers"
    CATCHERS = "catchers"
    COLLECTORS = "collectors"
    CORN_PILOTS = "corn_pilots"
    CRYPTO_ASC = "crypto_asc"
    CRYPTO_BTC = "crypto_btc"
    ELECTRIC_TRAIN_DRIVERS = "electric_train_drivers"
    LVL_FAMILIES = "lvl_families"
    LVL_PLAYERS = "lvl_players"
    MECHANICS = "mechanics"
    RICHEST = "richest"
    OUTBIDS = "outbids"
    PILOTS = "pilots"
    SELLERS = "sellers"
    TAXI_DRIVERS = "taxi_drivers"
    TRAM_DRIVERS = "tram_drivers"
    TRUCKERS = "truckers"
    CLADMENS = "cladmens"


class EstateType(str, Enum):
    HOUSES = "houses"
    BUSINESSES = "businesses"


class EstateHistoryType(str, Enum):
    HOUSE = "house"
    BUSINESS = "business"


class PunishType(str, Enum):
    KICK = "kick"
    WARN = "warn"
    WARNOFF = "warnoff"
    JAIL = "jail"
    JAILOFF = "jailoff"
    MUTE = "mute"
    MUTEOFF = "muteoff"
    RMUTE = "rmute"
    BAN = "ban"
    BANIP = "banip"
    UNJAIL = "unjail"
    UNMUTE = "unmute"
    UNRMUTE = "unrmute"
    APUNISH = "apunish"
    APUNISHOFF = "apunishoff"
    UNAPUNISH = "unapunish"


class SSFont(str, Enum):
    ARIAL_BOLD = 'arialbd.ttf'
    ARIAL_BOLD_ITALIC = 'arialbdi.ttf'
    BITTER_BOLD = 'bitterbd.ttf'
    BITTER_BOLD_ITALIC = 'bitterbdi.ttf'
    MONTSERRAT_BOLD = 'montserratbd.ttf'
    MONTSERRAT_BOLD_ITALIC = 'montserratbdi.ttf'
    NUNITO_BOLD = 'nunitobd.ttf'
    NUNITO_BOLD_ITALIC = 'nunitobdi.ttf'
    OPENSANS_BOLD = 'opensansbd.ttf'
    OPENSANS_BOLD_ITALIC = 'opensansbdi.ttf'
    UBUNTU_BOLD = 'ubuntubd.ttf'
    UBUNTU_BOLD_ITALIC = 'ubuntubdi.ttf'
    ROBOTO_BOLD = 'robotobd.ttf'
    ROBOTO_BOLD_ITALIC = 'robotobdi.ttf'
    SF_PRO_DISPLAY_BOLD = 'SF-Pro-Display-Bold.otf'


class ValidationError(BaseModel):
    loc: List[Union[str, int]]
    msg: str
    type: str


class HTTPValidationError(BaseModel):
    detail: Optional[List[ValidationError]] = None
