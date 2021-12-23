# python_basic_diploma/app/classes.py
"""
Basic classes for app.
"""
from os import environ
from datetime import datetime

from app.dialogs import DISPLAY_PHOTOS_TRUE, DISPLAY_PHOTOS_FALSE
from app.logger import get_logger


# initialize logger
logger = get_logger(__name__)

class UserQuery:
    """
    Basic class to save user query.
    """
    def __init__(self, command: str) -> None:
        """
        Create UserQuery entity.
        Attributes:
            command     - bot handler command from User.
        """
        logger.debug(
            f'UserQuery instance initialization by command [{command}].')
        self._command = command
        logger.info(f'UserQuery entity created by command {command}.')
    
    def _set_town_id(self, town_id: str) -> bool:
        """Setter for _town_id. Return True if ok, else return False."""
        logger.debug(f'UserQuery _set_town_id({town_id}) start.')
        try:
            self._town_id: int = int(town_id)
            logger.info(f'UserQuery _set_town_id [{town_id}].')
        except ValueError as e:
            logger.error(f'UserQuery _set_town_id error: {e}.')
            return False
    
    def _set_check_in(self, check_in: str) -> bool:
        """Setter for _check_in. Return True if ok, else return False."""
        logger.debug(f'UserQuery _set_check_in({check_in}) start.')
        try:
            datetime.strptime(check_in, '%Y-%m-%d')
            self._check_in = check_in
            return True
        except ValueError as e:
            logger.error(f'UserQuery _set_check_in error: {e}.')
            return False
    

    def _set_check_out(self, check_out: str) -> bool:
        """Setter for _check_out. Return True if ok, else return False."""
        logger.debug(f'UserQuery _set_check_out({check_out}) start.')
        try:
            datetime.strptime(check_out, '%Y-%m-%d')
            self._check_out = check_out
            return True
        except ValueError as e:
            logger.error(f'UserQuery _set_check_out error: {e}.')
            return False

    
    def _set_min_price(self, min_price: str) -> bool:
        """Setter for _min_price. Return True if ok, else return False."""
        logger.debug(f'UserQuery _set_min_price({min_price}) start.')
        try:
            self._min_price = int(min_price)
            logger.info(f'UserQuery _set_min_price [{min_price}].')
            return True
        except ValueError as e:
            logger.error(f'UserQuery _set_min_price error: {e}.')
            return False
    
    def _set_max_price(self, max_price: str) -> bool:
        """
        Setter for _max_price. 
        Change _min_price and _max_price if _max_price < _min_price.
        Return True if ok, else return False.
        """
        logger.debug(f'UserQuery _set_max_price({max_price}) start.')
        try:
            self._max_price = int(max_price)
            if self._max_price < self._min_price:
                logger.debug((
                    f'UserQuery _set_max_price error: min[{self._min_price}] '
                    f'>= max[{self._max_price}]'))
                max_value = max(self._min_price, self._max_price)
                min_value = min(self._min_price, self._max_price)
                self._max_price = max_value
                self._min_price = min_value
                logger.debug((
                    'UserQuery _set_max_price change _min_price to '
                    f'{self._min_price}.'))
            logger.info(f'UserQuery _set_max_price [{max_price}].')
            return True
        except ValueError as e:
            logger.error(f'UserQuery _set_max_price error: {e}.')
            return False
    
    def _set_min_dist(self, min_dist: str) -> bool:
        """
        Setter for _min_distance.
        Return True if ok, else return False.
        """
        logger.debug(f'UserQuery _set_min_dist({min_dist}) start.')
        try:
            self._min_dist = int(min_dist)
            logger.info(f'UserQuery _set_min_dist [{min_dist}].')
            return True
        except ValueError as e:
            logger.error(f'UserQuery _set_min_dist error: {e}.')
            return False
    
    def _set_max_dist(self, max_dist: str) -> bool:
        """
        Setter for _max_distance.
        Replace _min_distance and _max_distance if _max_distance < _min_distance.
        Return True if ok, else return False.
        """
        try:
            self._max_dist = int(max_dist)
            if self._max_dist < self._min_dist:
                logger.info(f'UserQuery set_max_dist [{max_dist}].')
            else:
                logger.debug((
                    f'UserQuery set_max_dist error: [{self._min_dist}] '
                    f'>= [{self._max_dist}]'))
                max_value = max(self._min_dist, self._max_dist)
                min_value = min(self._min_dist, self._max_dist)
                self._max_dist = max_value
                self._min_dist = min_value
                logger.debug((
                    'UserQuery _set_max_dist change _min_dist'
                    f'to {self._min_dist}.'))
            logger.info(f'UserQuery _set_max_dist [{max_dist}].')
            return True
        except ValueError as e:
            logger.error(f'UserQuery set_max_dist error: {e}.')
            return False
    
    def _set_results_num(self, results_num: str) -> bool:
        """
        Setter for _results_num.
        If results_num > MAX_RESULTS set MAX_RESULTS.
        Return True if ok, else return False.
        """
        logger.debug(f'UserQuery _set_results_num({results_num}) start.')
        try:
            self._results_num = int(results_num)
            if self._results_num > int(environ.get('MAX_RESULTS')):
                self._results_num = int(environ.get('MAX_RESULTS'))
            logger.info(f'UserQuery _set_results_num [{results_num}].')
            return True
        except ValueError as e:
            logger.error(f'UserQuery _set_results_num error: {e}.')
            return False
    
    def _set_display_photos(self, display_photos: str) -> bool:
        """
        Setter for _display_photos.
        By default set _display_photos to False.
        Return True if ok, else return False.
        """
        logger.debug(f'UserQuery _set_display_photos({display_photos}) start.')
        variants = {
            DISPLAY_PHOTOS_TRUE.lower(): True,
            DISPLAY_PHOTOS_FALSE.lower(): False,
        }
        try:
            self._display_photos = variants[display_photos.lower()]
            logger.info(
                f'UserQuery _set_display_photos [{self._display_photos}].'
            )
            return True
        except KeyError as e:
            self._display_photos = False
            logger.error(f'UserQuery _set_display_photos error: {e}')
            return False

    def update(self,
        town_id: str='',
        check_in: str='',
        check_out: str='',
        min_price: str='',
        max_price: str='',
        min_dist: str='',
        max_dist: str='',
        results_num: str='',
        display_photos: str=''
    ):
        """
        Update user data in class instance.
        Return True if ok, else return False.
        """
        result = True
        try:
            if len(town_id) > 0:
                logger.debug(f'UserQuery update _town_id({town_id}) start.')
                if self._set_town_id(town_id) == False:
                    result = False
            if len(check_in) > 0:
                logger.debug(f'UserQuery update _check_in({check_in}) start.')
                if self._set_check_in(check_in) == False:
                    result = False
            if len(check_out) > 0:
                logger.debug(f'UserQuery update _check_out({check_out}) start.')
                if self._set_check_out(check_out) == False:
                    result = False
            if len(min_price) > 0:
                logger.debug(f'UserQuery update _min_price({min_price}) start.')
                if self._set_min_price(min_price) == False:
                    result = False
            if len(max_price) > 0:
                logger.debug(f'UserQuery update _max_price({max_price}) start.')
                if self._set_max_price(max_price) == False:
                    result = False
            if len(min_dist) > 0:
                logger.debug(f'UserQuery update _min_dist({min_dist}) start.')
                if self._set_min_dist(min_dist) == False:
                    result = False
            if len(max_dist) > 0:
                logger.debug(f'UserQuery update _max_dist({max_dist}) start.')
                if self._set_max_dist(max_dist) == False:
                    result = False
            if len(results_num) > 0:
                logger.debug(
                    f'UserQuery update _results_num({results_num}) start.')
                if self._set_results_num(results_num) == False:
                    result = False
            if len(display_photos) > 0:
                logger.debug((
                    f'UserQuery update _display_photos({display_photos}) '
                    'start.'))
                if self._set_display_photos(display_photos) == False:
                    result = False
            return result
        except Exception as e:
            logger.error(f'UserQuery update error: {e}')
            return False
    
    @property
    def command(self) -> str:
        """
        Return user command from class instance.
        """
        logger.debug('UserQuery command property start.')
        return self._command
    
    @property
    def dictionary(self) -> dict:
        """
        Return dict with user data if all data is filled.
        If error return empty dict.
        """
        logger.debug('UserQuery dictionary property start.')
        attr_dict = {
            '/lowprice': {
                'command': 'command',
                'town_id': '_town_id', 
                'check_in': '_check_in',
                'check_out': '_check_out', 
                'results_num': '_results_num', 
                'display_photos': '_display_photos',
            },
            '/highprice': {
                'command': 'command',
                'town_id': '_town_id', 
                'check_in': '_check_in',
                'check_out': '_check_out', 
                'results_num': '_results_num', 
                'display_photos': '_display_photos',
            },
            '/bestdeal': {
                'command': 'command',
                'town_id': '_town_id', 
                'check_in': '_check_in',
                'check_out': '_check_out', 
                'min_price': '_min_price', 
                'max_price': '_max_price', 
                'min_distance': '_min_dist', 
                'max_distance': '_max_dist', 
                'results_num': '_results_num', 
                'display_photos': '_display_photos'
            },
        }
        result = dict()
        is_error = False
        for key, value in attr_dict[self.command].items():
            try:
                result[key] = self.__getattribute__(value)
            except AttributeError as e:
                logger.error(f'UserQuery dictionary error: {e}.')
                is_error = True
                break
        
        logger.debug(
            f'UserQuery dictionary property result: is_error[{is_error}].')
        return dict() if is_error else result

    def __str__(self) -> str:
        """
        Retrun all user data by converting dict in str.
        """
        logger.debug('UserQuery __str__ start.')
        userquery_dict = self.dictionary
        result = 'UserQuery entity:\n'
        if len(userquery_dict) == 0:
            result += 'None'
        else:
            for key, value in userquery_dict.items():
                result += f'{key}:\t{value}\n'
        logger.debug(f'UserQuery __str__ return [{result}].')
        return result


class Session:
    """
    Basic class to create sessions for chat_id.
    Create dict with key = chat_id, value = UserQuery entity.
    """
    def __init__(self):
        """Create dict to save UserQuery instances."""
        self._session_dist = dict()
        logger.info('Session entity created.')
    
    def create(self, chat_id: str, command: str) -> bool:
        """
        Create UserQuery entity in dict.
        Attributes:
            chat_id - telebot message.chat.id
            command - telebot user command
        Return True if ok, else return False.
        """
        logger.debug(
            f'Session create(chat_id={chat_id}, command={command}) start.')
        try:
            self._session_dist[chat_id] = UserQuery(command)
            logger.debug(f'Session size: {len(self._session_dist)}')
            return True
        except Exception as e:
            logger.error(f'Session create error: {e}.')
            return False
    
    def clear(self, chat_id: str) -> bool:
        """
        Delete dict key and value by chat_id.
        Attributes:
            chat_id - telebot message.chat.id.
        Return True if ok, else return False.
        """
        logger.debug(f'Session clear(chat_id={chat_id}) start.')
        try:
            del self._session_dist[chat_id]
            logger.info(f'Session for [{chat_id}] cleared.')
            return True
        except KeyError as e:
            logger.error(f'Session [{chat_id}] clear error: {e}.')
            return False
    
    def update(self, chat_id: str, attr: str, value: str) -> bool:
        """
        Update data in session by chat_id.
        Attributes:
            chat_id - telebot message.chat.id
            attr - keyname to update (town_id | min_price | max_price | min_distance | max_distance | results_num | display_photos)
            value - key value
        Return True if ok, else return False.
        """
        logger.debug((
            f'Session update(chat_id={chat_id}, attr={attr}, '
            f'value={value}) started.'))
        attr_set = (
            'town_id',
            'check_in',
            'check_out',
            'min_price',
            'max_price',
            'min_distance',
            'max_distance',
            'results_num',
            'display_photos',
        )
        if chat_id not in self._session_dist.keys():
            logger.error(f'Session update error: no session for [{chat_id}].')
            return False
        
        if attr not in attr_set:
            logger.error(f'Session update error: attr [{attr}] invalid.')
            return False
        
        result = False
        match attr:
            case 'town_id':
                result = self._session_dist[chat_id].update(town_id=value)
            case 'check_in':
                result = self._session_dist[chat_id].update(check_in=value)
            case 'check_out':
                result = self._session_dist[chat_id].update(check_out=value)
            case 'min_price':
                result = self._session_dist[chat_id].update(min_price=value)
            case 'max_price':
                result = self._session_dist[chat_id].update(max_price=value)
            case 'min_distance':
                result = self._session_dist[chat_id].update(min_dist=value)
            case 'max_distance':
                result = self._session_dist[chat_id].update(max_dist=value)
            case 'results_num':
                result = self._session_dist[chat_id].update(results_num=value)
            case 'display_photos':
                result = self._session_dist[chat_id].update(
                    display_photos=value
                )
        logger.debug(f'Session update return {result}.')
        return result
    
    def get_session_dict(self, chat_id: str) -> dict:
        """
        Return UserQuery dictionary by chat_id.
        Add chat_id key and value to dict.
        """
        logger.debug(f'Session get_session_dict(chat_id={chat_id}) start.')
        user_data: UserQuery = self._session_dist[chat_id]
        result = user_data.dictionary
        result['chat_id'] = chat_id
        logger.debug(f'Session get_session_dict return [{result}].')
        return result
    
    def __str__(self):
        """Return Session keys in str."""
        logger.debug('Session __str__ start.')
        return f'Session entity:\n {self._session_dist.keys()}\nTotal: {len(self._session_dist)}'


class Hotel:
    """Basic class for hotel data."""
    def _set_id(self) -> bool:
        """Setter for _id. Return True if ok, else return False."""
        logger.debug('Hotel _set_id start.')
        try:
            self._id = self._data_dict['id']
            logger.debug(f'Hotel _set_id set _id = {self._id}.')
            return True
        except KeyError as e:
            logger.error(f'Hotel _set_id error: {e}.')
            return False
    
    def _set_name(self) -> bool:
        """Setter for _name. Return True if ok, else return False."""
        logger.debug('Hotel _set_name start.')
        try:
            self._name = self._data_dict['name']
            logger.debug(f'Hotel _set_name set _name = {self._name}.')
            return True
        except KeyError as e:
            logger.error(f'Hotel _set_name error: {e}.')
            return False
    
    def _set_address(self) -> bool:
        """Setter for _address. Return True if ok, else return False."""
        logger.debug('Hotel _set_address start.')
        address_list = list()
        try:
            address_dict = self._data_dict['address']
            for _i in address_dict.values():
                if _i:
                    address_list.append(_i)
            self._address = ', '.join(address_list)
            logger.debug(f'Hotel _set_address set _address = {self._address}.')
            return True
        except KeyError as e:
            logger.error(f'Hotel _set_address error: {e}.')
            return False

    def _set_distance(self) -> bool:
        """Setter for _distance. Return True if ok, else return False."""
        logger.debug('Hotel _set_distance start.')
        try:
            landmarks = self._data_dict['landmarks']
            for _landmark in landmarks:
                if _landmark['label'].lower() == 'центр города':
                    distance = _landmark['distance']
                    break
            if distance:
                self._distance = distance
                logger.debug(
                    f'Hotel _set_distance set _distance = {self._distance}.')
                return True
            else:
                logger.error(
                    'Hotel _set_distance error: no distance key in _data_dict.')
                return False
        except KeyError as e:
            logger.error(f'Hotel _set_distance error: {e}.')
            return False
    
    def _set_price(self) -> bool:
        """Setter for _price. Return True if ok, else return False."""
        logger.debug('Hotel _set_price start.')
        try:
            rate_plan = self._data_dict['ratePlan']
            price_dict = rate_plan['price']
            self._price = price_dict['current']
            logger.debug(f'Hotel _set_price set _price = {self._price}.')
            return True
        except KeyError as e:
            logger.error(f'Hotel _set_price error: {e}.')
            return False


    def __init__(self, data_dict: dict):
        """
        Create Hotel instance. Run parse command after creating instance.
        Attributes:
            data_dict - dict parced from RapidApi search results JSON.
        """
        self._data_dict = data_dict
        
    def parse(self) -> bool:
        """
        Parse data_dict and set all Hotel parameters.
        Return True if ok, else return False.
        """
        logger.debug('Hotel parse start.')
        return (
            self._set_id() and 
            self._set_name() and 
            self._set_address() and 
            self._set_distance() and 
            self._set_price()
        )
    
    @property
    def dictionary(self) -> dict:
        """Return Hotel instance data (except _price) in dict. 
        Using for writing data in database."""
        logger.debug('Hotel dictionary start.')
        return {
            'id': self._id,
            'name': self._name,
            'address': self._address,
            'distance': self._distance
        }
    
    @property
    def price(self):
        """Return Hotel instance _price."""
        logger.debug('Hotel price start.')
        return self._price

    
