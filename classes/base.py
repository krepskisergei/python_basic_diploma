from dataclasses import dataclass


@dataclass(frozen=False)
class Location:
    """Dataclass for Location from API or DB."""
    destinationId: int
    geoId: int
    caption: str
    name: str
    name_lower: str = ''

    def format_data(self) -> None:
        """Remove html tags from caption."""
        self.caption = self.caption.replace(
            "<span class='highlighted'>", ""
        ).replace("</span>", "")
        self.name_lower = self.name.lower().replace(' ', '').replace('-', '')

    def to_list(self) -> list:
        """Return entity data in list."""
        self.format_data()
        return [
            self.destinationId,
            self.geoId,
            self.caption,
            self.name,
            self.name_lower
        ]


@dataclass(frozen=True)
class Address:
    """Dataclass for Hotel Address from API."""
    streetAddress: str
    extendedAddress: str
    locality: str
    postalCode: str
    region: str
    countryName: str
    countryCode: str
    # TODO: Add all data from api responce

    @property
    def full_address(self, addr_attrs: set = None) -> str:
        """Return full address with order in addr_attrs."""
        if addr_attrs is None:
            addr_attrs = (
                'streetAddress',
                'extendedAddress',
                'locality',
                'region',
                'countryName',
                'postalCode'
            )
        addr_list = []
        for _attr in addr_attrs:
            try:
                value = self.__getattribute__(_attr)
                if len(value) > 0:
                    addr_list.append(value)
            except AttributeError:
                pass
        return ', '.join(addr_list)


@dataclass(frozen=True)
class Hotel:
    """Dataclass for Hotel from API and DB."""
    id: int
    name: str
    fullAddress: str
    url: str
    starRating: int
    distance: str

    @property
    def to_list(self) -> list:
        """Return entity data in list."""
        return [
            self.id,
            self.name,
            self.fullAddress,
            self.url,
            self.starRating,
            self.distance
        ]


@dataclass(frozen=True)
class Photo:
    """Dataclass for Hotel Photo from API."""
    imageId: int
    hotelId: int
    baseUrl: str

    def format_url(self, suffix: str) -> None:
        """Replace {size} to suffix in baseUrl."""
        self.baseUrl = self.baseUrl.replace('{size}', suffix)

    @property
    def to_list(self) -> list:
        """Return entity data in list."""
        return [
            self.imageId,
            self.hotelId,
            self.baseUrl
        ]
