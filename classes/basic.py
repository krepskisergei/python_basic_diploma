from dataclasses import dataclass


@dataclass(frozen=False)
class Location:
    """Dataclass for Location from API and database."""
    destination_id: int
    geo_id: int
    caption: str
    name: str
    name_lower: str = ''

    def _format_content(self) -> None:
        """Remove HTML tags from caption and generate name_lower."""
        self.caption = self.caption.replace(
            "<span class='highlighted'>", ""
        ).replace("</span>", "")
        self.name_lower = self.name.lower().replace(' ', '').replace('-', '')

    @property
    def data(self) -> list:
        """Return instance data in list."""
        self._format_content()
        return [
            self.destination_id,
            self.geo_id,
            self.caption,
            self.name,
            self.name_lower
        ]


@dataclass(frozen=True)
class Address:
    """Dataclass for Hotel address from API."""
    street_address: str
    extended_address: str
    locality: str
    region: str
    country_name: str

    @property
    def data(self) -> str:
        """
        Return instance data in string separated by commas.
        Data order according set order.
        """
        order_attrs = (
            'street_address',
            'extended_address',
            'locality',
            'region',
            'country_name'
        )
        data_list = []
        for _attr in order_attrs:
            try:
                value = self.__getattribute__(_attr)
                if len(value) > 0:
                    data_list.append(str(value))
            except AttributeError:
                pass
        return ', '.join(data_list)


@dataclass(frozen=True)
class Hotel:
    """Dataclass for Hotel from API and database."""
    id: int
    name: str
    address: str
    star_rating: int
    distance: float | None

    @property
    def data(self) -> list:
        """Return instance data in list."""
        return [
            self.id,
            self.name,
            self.address,
            self.star_rating,
            self.distance
        ]


@dataclass(frozen=True)
class HotelPhoto:
    """
    Dataclass for hotel photos from API and database.
    Use format_url() before use data from instance.
    """
    id: int
    url: str

    @property
    def data(self) -> list:
        """Return instance data in list."""
        return [
            self.id,
            self.url
        ]

    def formated_url(self, suffix: str) -> str:
        """Replace {size} to suffix in baseUrl."""
        return self.url.replace('{size}', suffix)


@dataclass(frozen=True)
class SearchResult:
    session_id: int
    hotel_id: int
    url: str
    price: float

    @property
    def data(self) -> list:
        """Return instance data in list."""
        return [
            self.session_id,
            self.hotel_id,
            self.url,
            self.price
        ]
