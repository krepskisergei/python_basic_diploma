from dataclasses import dataclass


@dataclass(frozen=False)
class Location:
    """Dataclass for Location from API and database."""
    destinationId: int
    geoId: int
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
            self.destinationId,
            self.geoId,
            self.caption,
            self.name,
            self.name_lower
        ]


@dataclass(frozen=True)
class Address:
    """Dataclass for Hotel address from API."""
    streetAddress: str
    extendedAddress: str
    locality: str
    postalCode: str
    region: str
    countryName: str
    countryCode: str
    # TODO: add all attributes from API responce

    def data(self, order: set = None) -> str:
        """
        Return instance data in string separated by commas.
        Data order according set order.
        """
        order_attrs = (
            'streetAddress',
            'extendedAddress',
            'locality',
            'region',
            'countryName'
        )
        if order is not None:
            order_attrs = order
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
    url: str
    starRating: int
    distance: str

    @property
    def data(self) -> list:
        """Return instance data in list."""
        return [
            self.id,
            self.name,
            self.fullAddress,
            self.url,
            self.starRating,
            self.distance
        ]


@dataclass(frozen=False)
class HotelPhoto:
    """
    Dataclass for hotel photos from API and database.
    Use format_url() before use data from instance.
    """
    imageId: int
    baseUrl: str

    @property
    def data(self) -> list:
        """Return instance data in list."""
        return [
            self.imageId,
            self.baseUrl
        ]

    # TODO: change format_url to method output(suffix: str)
    # make dataclass frozen=True

    def format_url(self, suffix: str) -> None:
        """Replace {size} to suffix in baseUrl."""
        self.baseUrl = self.baseUrl.replace('{size}', suffix)


@dataclass(frozen=True)
class SearchResult:
    sessionId: int
    hotelId: int
    price: float

    @property
    def data(self) -> list:
        """Return instance data in list."""
        return [
            self.sessionId,
            self.hotelId,
            self.price
        ]
