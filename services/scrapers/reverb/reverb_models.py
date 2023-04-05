"""reverb_models.py"""

from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from pydantic.dataclasses import dataclass
# pylint: disable=missing-class-docstring
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods


@dataclass
class Price:
    amount: str
    amount_cents: int
    currency: str
    symbol: str
    display: str


@dataclass
class BuyerPrice:
    amount: str
    amount_cents: int
    currency: str
    symbol: str
    display: str
    tax_included_hint: str
    tax_included: bool
    tax_included_rate: int


@dataclass
class State:
    slug: str
    description: str


@dataclass
class UsRateItem:
    amount: str
    amount_cents: int
    currency: str
    symbol: str
    display: str


@dataclass
class Shipping:
    local: bool
    us: bool
    us_rate: Optional[UsRateItem]


@dataclass
class LargeCrop:
    href: str


@dataclass
class SmallCrop:
    href: str


@dataclass
class Full:
    href: str


@dataclass
class Thumbnail:
    href: str


@dataclass
class Links:
    large_crop: LargeCrop
    small_crop: SmallCrop
    full: Full
    thumbnail: Thumbnail


class Photo(BaseModel):
    links: Optional[Links] = Field(None, alias="_links")


@dataclass
class Photo1:
    href: str


@dataclass
class Self:
    href: str


@dataclass
class Update:
    method: str
    href: str


@dataclass
class End:
    method: str
    href: str


@dataclass
class Want:
    method: str
    href: str


@dataclass
class Unwant:
    method: str
    href: str


@dataclass
class Edit:
    href: str


@dataclass
class Web:
    href: str


@dataclass
class Cart:
    href: str


@dataclass
class MakeOffer:
    method: str
    href: str


@dataclass
class Links1:
    photo: Photo1
    self: Self
    update: Update
    end: End
    want: Want
    unwant: Unwant
    edit: Edit
    web: Web
    cart: Cart
    make_offer: Optional[MakeOffer] = None


class Listing(BaseModel):
    id: int
    make: str
    model: str
    finish: Optional[str] = None
    year: str
    title: str
    created_at: str
    shop_name: str
    description: str
    condition: str
    condition_uuid: str
    condition_slug: str
    price: Price
    inventory: int
    has_inventory: bool
    offers_enabled: bool
    auction: bool
    category_uuids: List[str]
    listing_currency: str
    published_at: str
    buyer_price: BuyerPrice
    sku: Optional[str] = None
    state: State
    shipping: Shipping
    slug: str
    photos: List[Photo]
    _links: Optional[Links1] = None

    @validator("published_at")
    @classmethod
    def publised_at_valid(cls, value: str) -> str:
        """Validate the published_at field is a
        proper datetime. If it is not, populate
        the field with a default (current utc)
        time."""
        try:
            datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z")
        except ValueError:
            now = datetime.now(timezone.utc)
            return now.strftime("%Y-%m-%dT%H:%M:%S%z")
        return value


@dataclass
class Image:
    href: str


@dataclass
class Self1:
    href: str


@dataclass
class Listings:
    href: str


@dataclass
class Follow:
    href: str


@dataclass
class Next:
    href: str


@dataclass
class Links2:
    image: Image
    self: Self1
    listings: Listings
    follow: Follow
    next: Next


class Results(BaseModel):
    name: str
    description: str
    total: int
    current_page: int
    total_pages: int
    listings: List[Listing]
    _links: Optional[Links2] = None

    @validator("current_page", "total_pages")
    @classmethod
    def pages_valid(cls, value: int) -> int:
        """Validate the the pages values are
        positive integers. If they are not,
        populate the fields with a default (1)
        value. """
        if not isinstance(value, int) or value <= 0:
            return 1
        return value
