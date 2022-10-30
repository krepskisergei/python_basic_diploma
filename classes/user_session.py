from datetime import datetime, date
from app.app_logger import get_logger


# initiate logger
logger = get_logger(__name__)


class UserSession:
    """Class for keep user data in sessions."""
    attrs = {
        'command': str,
        'id': int,
        'query_time': datetime,
        'location_id': int,
        'check_in': date,
        'check_out': date,
        'price_min': float,
        'price_max': float,
        'distance_min': float,
        'distance_max': float,
        'results_num': int,
        'photos_num': int
    }
    id: int
    query_time: datetime
    command: str
    location_id: int
    check_in: date
    check_out: date
    price_min: float
    price_max: float
    distance_min: float
    distance_max: float
    results_num: int
    photos_num: int

    def __init__(self, chat_id: int, **kwargs) -> None:
        self.chat_id = chat_id
        if kwargs:
            self.set_attrs(kwargs)

    @property
    def data(self) -> list:
        """Return instance data in list."""
        return [self.chat_id]

    @property
    def current_step(self) -> str:
        """
        Return instance current step. 'complete' on fullfill.
        """
        attrs = list(self.attrs.keys())
        attrs.reverse()

        for _attr in attrs:
            try:
                self.__getattribute__(_attr)
                if _attr == attrs[0]:
                    return 'complete'
                return attrs[attrs.index(_attr) - 1]
            except AttributeError:
                pass
        else:
            return attrs[-1]

    # validator
    def _validator(self, attr_name: str, attr_value: object) -> object:
        """
        Return attr_value in attr_name type.
        Raise UserSessionValue error on failed.
        """
        attr_type = self.attrs.get(attr_name, None)
        # invalid attribute name
        if attr_type is None:
            raise UserSessionAttributeError(
                f'Invalid attribute name [{attr_name}].')
        # attribute value have correct type
        if isinstance(attr_value, attr_type):
            return attr_value
        # convert attr_value
        try:
            if attr_type == str:
                return str(attr_value)
            if attr_type == int:
                attr_value = attr_value.replace('.', '').replace(
                    ',', '').replace(' ', '')
                return int(attr_value)
            if attr_type == bool:
                if isinstance(attr_value, str):
                    attr_value = attr_value.replace('.', '').replace(
                        ',', '').replace(' ', '')
                    return bool(int(attr_value))
                return bool(attr_value)
            if attr_type == float:
                attr_value = attr_value.replace(',', '.').replace(' ', '')
                return float(attr_value)
            if attr_type == date:
                return datetime.strptime(attr_value, '%Y-%m-%d').date()
            if attr_type == datetime:
                return datetime.strptime(attr_value, '%Y-%m-%d %H:%M:%S')
        except ValueError as e:
            raise UserSessionValueError(
                    f'Invalid {attr_name} attribute value type [{attr_value}]',
                    type(attr_value), attr_type, *e.args
                )

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
            # validate types
            try:
                attr_value = self._validator(attr_name, attr_value)
            except (UserSessionAttributeError, UserSessionValueError):
                return False
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

    def _check_check_in(self) -> None:
        """
        Check attribute 'check_in'.
        Raise UserSessionAttributeError, UserSessionValueError on errors.
        """
        attr = 'check_in'
        try:
            value = self.__getattribute__(attr)
            if value >= date.today():
                return None
            raise UserSessionValueError(
                f'Invalid attribute [{attr}] value: {value}.')
        except AttributeError:
            raise UserSessionAttributeError(f'Attribute [{attr}] not set.')

    def _check_check_out(self) -> None:
        """
        Check attribute 'check_out'.
        Raise UserSessionAttributeError, UserSessionValueError on errors.
        """
        attr = 'check_out'
        try:
            value = self.__getattribute__(attr)
            if value > self.check_in:
                return None
            raise UserSessionValueError(
                f'Invalid attribute [{attr}] value: {value}.')
        except AttributeError:
            raise UserSessionAttributeError(f'Attribute [{attr}] not set.')

    def _check_price_min(self) -> None:
        """
        Check attribute 'price_min'.
        Raise UserSessionAttributeError, UserSessionValueError on errors.
        """
        attr = 'price_min'
        try:
            value = self.__getattribute__(attr)
            if value >= 0:
                return None
            raise UserSessionValueError(
                f'Invalid attribute [{attr}] value: {value}.')
        except AttributeError:
            raise UserSessionAttributeError(f'Attribute [{attr}] not set.')

    def _check_price_max(self) -> None:
        """
        Check attribute 'price_max'.
        Raise UserSessionAttributeError, UserSessionValueError on errors.
        """
        attr = 'price_max'
        try:
            value = self.__getattribute__(attr)
            if value >= self.price_min:
                return None
            raise UserSessionValueError(
                f'Invalid attribute [{attr}] value: {value}.')
        except AttributeError:
            raise UserSessionAttributeError(f'Attribute [{attr}] not set.')

    def _check_distance_min(self) -> None:
        """
        Check attribute 'distance_min'.
        Raise UserSessionAttributeError, UserSessionValueError on errors.
        """
        attr = 'distance_min'
        try:
            value = self.__getattribute__(attr)
            if value >= 0:
                return None
            raise UserSessionValueError(
                f'Invalid attribute [{attr}] value: {value}.')
        except AttributeError:
            raise UserSessionAttributeError(f'Attribute [{attr}] not set.')

    def _check_distance_max(self) -> None:
        """
        Check attribute 'distance_max'.
        Raise UserSessionAttributeError, UserSessionValueError on errors.
        """
        attr = 'distance_max'
        try:
            value = self.__getattribute__(attr)
            if value >= self.distance_min:
                return None
            raise UserSessionValueError(
                f'Invalid attribute [{attr}] value: {value}.')
        except AttributeError:
            raise UserSessionAttributeError(f'Attribute [{attr}] not set.')

    def _check_results_num(self) -> None:
        """
        Check attribute 'results_num'.
        Raise UserSessionAttributeError, UserSessionValueError on errors.
        """
        attr = 'results_num'
        from app.config import MAX_RESULTS

        try:
            value = self.__getattribute__(attr)
            if 0 < value <= MAX_RESULTS:
                return None
            raise UserSessionValueError(
                f'Invalid attribute [{attr}] value: {value}.')
        except AttributeError:
            raise UserSessionAttributeError(f'Attribute [{attr}] not set.')

    def _check_photos_num(self) -> None:
        """
        Check attribute 'photos_num'.
        Raise UserSessionAttributeError, UserSessionValueError on errors.
        """
        attr = 'photos_num'
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
