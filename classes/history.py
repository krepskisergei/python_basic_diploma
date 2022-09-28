from datetime import datetime, date
from app.logger import get_logger


# initiate logger
logger = get_logger(__name__)


class History:
    """Data class for user query history."""
    attrs = {
        'id': int,
        'queryTime': datetime,
        'command': str,
        'locationId': int,
        'checkIn': date,
        'checkOut': date,
        'priceMin': float,
        'priceMax': float,
        'distanceMin': float,
        'distanceMax': float,
        'resultsNum': int,
        'photosNum': int
    }

    def __init__(self, chat_id: int) -> None:
        """Initiate class instance by chat_id."""
        self.chatId = chat_id
        self._func_list = [
            x for x in dir(self)
            if callable(getattr(self, x))
            and x.startswith('_check_')
        ]

    @property
    def to_list(self) -> list:
        """Return instance attributes (except id, complete) in list."""
        attr_tuplte = (
            'chatId', 'queryTime', 'command', 'locationId',
            'checkIn', 'checkOut', 'priceMin', 'priceMax',
            'distanceMin', 'distanceMax', 'resultsNum', 'photosNum'
        )
        attr_list = []
        for attr in attr_tuplte:
            try:
                attr_list.append(self.__getattribute__(attr))
            except AttributeError:
                attr_list.append(None)
        return attr

    @property
    def current_step(self) -> str:
        """Get current step."""
        attr_list = list(self.attrs.keys())
        attr_list.reverse()
        for attr in attr_list:
            try:
                self.__getattribute__(attr)
                return attr_list[attr_list.index(attr) - 1]
            except AttributeError:
                pass
        else:
            return None

    # setters
    @logger.debug_func
    def set_attributes(self, attr_dict: dict) -> dict:
        """Return dict with success updating attributes."""
        result = {}
        for attr, value in attr_dict.items():
            if self._set_attribute(attr, value):
                result[attr] = value
        return result

    @logger.debug_func
    def _set_attribute(self, attr_name: str, value) -> bool:
        """Return status of setting attribute."""
        try:
            self.__getattribute__(attr_name)
            return
        except AttributeError:
            try:
                attr_type = self.attrs.get(attr_name, None)
                if attr_type is not None:
                    if value is not None and isinstance(value, attr_type):
                        self.__setattr__(attr_name, value)
                        if f'_check_{attr_name}' in self._func_list:
                            try:
                                check = getattr(self, f'_check_{attr_name}')
                                check()
                                return True
                            except HistoryCheckError:
                                self.__delattr__(attr_name)
                                return False
                        return True
                    else:
                        if value is not None:
                            raise HistoryValueError(
                                f'Attribute [{attr_name}] value '
                                f'[{value}] error.'
                            )
                else:
                    raise HistoryValueError(
                        f'Attribute name error [{attr_name}].')
            except HistoryBaseError:
                return False

    # checkers
    def _check_command(self) -> None:
        """Check attribute command value."""
        attr = 'command'
        commands_tuple = (
            '/lowprice',
            '/highprice',
            '/bestdeal'
        )
        try:
            value = self.__getattribute__(attr)
            if value in commands_tuple:
                return
            raise HistoryCheckError(
                f'Error checking attribute [{attr}] = [{value}].')
        except AttributeError:
            raise HistoryCheckError(f'No attribute for [{attr}].')

    def _check_checkOut(self) -> None:
        """Check attribute checkOut value."""
        attr = 'checkOut'
        try:
            value = self.__getattribute__(attr)
            if value > self.checkIn:
                return
            raise HistoryCheckError(
                f'Error checking attribute [{attr}] = [{value}].')
        except AttributeError:
            raise HistoryCheckError(f'No attribute for [{attr}].')

    def _check_priceMax(self) -> None:
        """Check attribute priceMax value."""
        attr = 'priceMax'
        try:
            value = self.__getattribute__(attr)
            if value > self.priceMin:
                return
            raise HistoryCheckError(
                f'Error checking attribute [{attr}] = [{value}].')
        except AttributeError:
            raise HistoryCheckError(f'No attribute for [{attr}].')

    def _check_distanceMax(self) -> None:
        """Check attribute distanceMax value."""
        attr = 'distanceMax'
        try:
            value = self.__getattribute__(attr)
            if value > self.distanceMin:
                return
            raise HistoryCheckError(
                f'Error checking attribute [{attr}] = [{value}].')
        except AttributeError:
            raise HistoryCheckError(f'No attribute for [{attr}].')

    def _check_resultsNum(self) -> None:
        """Check attribute resultsNum value."""
        from app.config import MAX_RESULTS

        attr = 'resultsNum'
        try:
            value = self.__getattribute__(attr)
            if 0 < value <= MAX_RESULTS:
                return
            raise HistoryCheckError(
                f'Error checking attribute [{attr}] = [{value}].')
        except AttributeError:
            raise HistoryCheckError(f'No attribute for [{attr}].')

    def _check_photosNum(self) -> None:
        """Check attribute resultsNum value."""
        from app.config import MAX_PHOTOS

        attr = 'photosNum'
        try:
            value = self.__getattribute__(attr)
            if value <= MAX_PHOTOS:
                return
            raise HistoryCheckError(
                f'Error checking attribute [{attr}] = [{value}].')
        except AttributeError:
            raise HistoryCheckError(f'No attribute for [{attr}].')


class HistoryBaseError(Exception):
    """Basic class of History exception with logging."""
    _log_level: int = 0

    def __init__(self, *args) -> None:
        """Initiate History exception."""
        if self._log_level > 0:
            msg = ''
            if args:
                msg = ' '.join(map(str, args))
            logger.log_message(msg, self._log_level)
        super().__init__(*args)


class HistoryValueError(HistoryBaseError):
    """Exception for setting attribute value error."""
    _log_level: int = logger.WARNING


class HistoryCheckError(HistoryBaseError):
    """Exception for checking attributes error."""
    _log_level: int = logger.WARNING
