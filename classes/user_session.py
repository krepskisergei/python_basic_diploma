from datetime import datetime, date
from app.app_logger import get_logger


# initiate logger
logger = get_logger(__name__)


class UserSession:
    """Class for keep user data in sessions."""
    attrs = {
        'command': str,
        'id': int,
        'queryTime': datetime,
        'locationId': int,
        'checkIn': date,
        'checkOut': date,
        'priceMin': float | int,
        'priceMax': float | int,
        'distanceMin': float | int,
        'distanceMax': float | int,
        'resultsNum': int,
        'photosNum': int
    }
    id: int
    queryTime: datetime
    command: str
    locationId: int
    checkIn: date
    checkOut: date
    priceMin: float
    priceMax: float
    distanceMin: float
    distanceMax: float
    resultsNum: int
    photosNum: int

    def __init__(self, chatId: int, **kwargs) -> None:
        self.chatId = chatId
        if kwargs:
            self.set_attrs(kwargs)

    @property
    def data(self) -> list:
        """Return instance data in list."""
        return [self.chatId]

    @property
    def current_step(self) -> str:
        """Get instance current step."""
        attrs = list(self.attrs.keys())
        attrs.reverse()
        for _attr in attrs:
            try:
                self.__getattribute__(_attr)
                return attrs[attrs.index(_attr) - 1]
            except AttributeError:
                pass
        else:
            return attrs[-1]

    # setters
    def set_attrs(self, attr_dict: dict) -> dict:
        """
        Return dict with setted attributes.
        """
        success_attrs = {}
        for attr, value in attr_dict.items():
            try:
                if self._set_attr(attr, value):
                    success_attrs[attr] = value
            except _UserSessionBaseError:
                pass
        return success_attrs

    def _set_attr(self, attr_name: str, attr_value: object) -> bool:
        """
        Return attribute setter status.
        Return None if attribute value exists.
        Can be raising UserSessionAttributeError, UserSessionValueError.
        """
        if attr_value is None:
            raise UserSessionValueError(
                f'Invalid value [{attr_value}] for attribute [{attr_name}].')
        try:
            self.__getattribute__(attr_name)
            return None
        except AttributeError:
            # check order
            if self.current_step != attr_name:
                raise UserSessionAttributeError(
                    f'Attribute [{attr_name}] setting order error.')
            # check types
            attr_type = self.attrs.get(attr_name, None)
            if attr_type is None:
                # invalid attribute name
                raise UserSessionAttributeError(
                    f'Invalid attribute name [{attr_name}].')
            if not isinstance(attr_value, attr_type):
                raise UserSessionValueError(
                    f'Invalid {attr_name} attribute value type [{attr_value}]',
                    type(attr_value), attr_type
                )
            # Set attribute value to instance
            self.__setattr__(attr_name, attr_value)
            # checker
            try:
                # Class have checker
                checker = self.__getattribute__(f'_check_{attr_name}')
                try:
                    if callable(checker):
                        checker()
                    return True
                except (UserSessionValueError, UserSessionAttributeError):
                    self.__delattr__(attr_name)
                    return False
            except AttributeError:
                # No checker
                return True

    # checkers
    def _check_command(self) -> None:
        """
        Check attribute 'command'.
        Raise UserSessionAttributeError, UserSessionValueError on errors.
        """
        attr = 'command'
        try:
            value = self.__getattribute__(attr)
            if value in ('/lowprice', '/highprice', '/bestdeal'):
                return None
            raise UserSessionValueError(
                f'Invalid attribute [{attr}] value: {value}.')
        except AttributeError:
            raise UserSessionAttributeError(f'Attribute [{attr}] not set.')

    def _check_checkIn(self) -> None:
        """
        Check attribute 'checkIn'.
        Raise UserSessionAttributeError, UserSessionValueError on errors.
        """
        attr = 'checkIn'
        try:
            value = self.__getattribute__(attr)
            if value >= date.today():
                return None
            raise UserSessionValueError(
                f'Invalid attribute [{attr}] value: {value}.')
        except AttributeError:
            raise UserSessionAttributeError(f'Attribute [{attr}] not set.')

    def _check_checkOut(self) -> None:
        """
        Check attribute 'checkOut'.
        Raise UserSessionAttributeError, UserSessionValueError on errors.
        """
        attr = 'checkOut'
        try:
            value = self.__getattribute__(attr)
            if value > self.checkIn:
                return None
            raise UserSessionValueError(
                f'Invalid attribute [{attr}] value: {value}.')
        except AttributeError:
            raise UserSessionAttributeError(f'Attribute [{attr}] not set.')

    def _check_priceMin(self) -> None:
        """
        Check attribute 'priceMin'.
        Raise UserSessionAttributeError, UserSessionValueError on errors.
        """
        attr = 'priceMin'
        try:
            value = self.__getattribute__(attr)
            if value >= 0:
                return None
            raise UserSessionValueError(
                f'Invalid attribute [{attr}] value: {value}.')
        except AttributeError:
            raise UserSessionAttributeError(f'Attribute [{attr}] not set.')

    def _check_priceMax(self) -> None:
        """
        Check attribute 'priceMax'.
        Raise UserSessionAttributeError, UserSessionValueError on errors.
        """
        attr = 'priceMax'
        try:
            value = self.__getattribute__(attr)
            if value >= self.priceMin:
                return None
            raise UserSessionValueError(
                f'Invalid attribute [{attr}] value: {value}.')
        except AttributeError:
            raise UserSessionAttributeError(f'Attribute [{attr}] not set.')

    def _check_distanceMin(self) -> None:
        """
        Check attribute 'distanceMax'.
        Raise UserSessionAttributeError, UserSessionValueError on errors.
        """
        attr = 'distanceMin'
        try:
            value = self.__getattribute__(attr)
            if value >= 0:
                return None
            raise UserSessionValueError(
                f'Invalid attribute [{attr}] value: {value}.')
        except AttributeError:
            raise UserSessionAttributeError(f'Attribute [{attr}] not set.')

    def _check_distanceMax(self) -> None:
        """
        Check attribute 'distanceMax'.
        Raise UserSessionAttributeError, UserSessionValueError on errors.
        """
        attr = 'distanceMax'
        try:
            value = self.__getattribute__(attr)
            if value >= self.distanceMin:
                return None
            raise UserSessionValueError(
                f'Invalid attribute [{attr}] value: {value}.')
        except AttributeError:
            raise UserSessionAttributeError(f'Attribute [{attr}] not set.')

    def _check_resultsNum(self) -> None:
        """
        Check attribute 'resultsNum'.
        Raise UserSessionAttributeError, UserSessionValueError on errors.
        """
        attr = 'resultsNum'
        from app.config import MAX_RESULTS

        try:
            value = self.__getattribute__(attr)
            if 0 < value <= MAX_RESULTS:
                return None
            raise UserSessionValueError(
                f'Invalid attribute [{attr}] value: {value}.')
        except AttributeError:
            raise UserSessionAttributeError(f'Attribute [{attr}] not set.')

    def _check_photosNum(self) -> None:
        """
        Check attribute 'resultsNum'.
        Raise UserSessionAttributeError, UserSessionValueError on errors.
        """
        attr = 'photosNum'
        from app.config import MAX_PHOTOS

        try:
            value = self.__getattribute__(attr)
            if value <= MAX_PHOTOS:
                return None
            raise UserSessionValueError(
                f'Invalid attribute [{attr}] value: {value}.')
        except AttributeError:
            raise UserSessionAttributeError(f'Attribute [{attr}] not set.')


class _UserSessionBaseError(Exception):
    """Basic exception for UserSession class with logging."""
    _log_level: int = 0

    def __init__(self, *args: object) -> None:
        if self._log_level > 0:
            msg = ''
            if args:
                msg = ' '.join(map(str, args))
            logger.log_msg(self._log_level, msg)
        super().__init__(*args)


class UserSessionAttributeError(_UserSessionBaseError):
    """Exception with logging for instance attributes error."""
    _log_level: int = logger.ERROR


class UserSessionValueError(_UserSessionBaseError):
    """Exception with logging for instance values error."""
    _log_level: int = logger.WARNING
