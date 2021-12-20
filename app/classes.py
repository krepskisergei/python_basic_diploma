# python_basic_diploma/app/classes.py
"""
Basic classes for bot.
"""
from os import path, getcwd, environ

from telebot.types import User

from app.dialogs import DISPLAY_PHOTOS_TRUE, DISPLAY_PHOTOS_FALSE
from app.logger import get_logger


logger = get_logger(__name__)

class UserQuery:
    def __init__(self, command: str) -> None:
        """
        Create UserQuery entity.
        Attributes:
            command     - bot handler command from User.
        """
        self._command = command
        logger.info(f'UserQuery entity created by command {command}.')
    
    def _set_town_id(self, town_id: str) -> bool:
        """Setter for town_id."""
        try:
            self._town_id: int = int(town_id)
            logger.info(f'UserQuery set_town_id [{town_id}].')
        except ValueError as e:
            logger.error(f'UserQuery set_town_id error: {e}.')
            return False
    
    def _set_min_price(self, min_price: str) -> bool:
        """Setter for min_price."""
        try:
            self._min_price = int(min_price)
            logger.info(f'UserQuery set_min_price [{min_price}].')
            return True
        except ValueError as e:
            logger.error(f'UserQuery set_min_price error: {e}.')
            return False
    
    def _set_max_price(self, max_price: str) -> bool:
        try:
            self._max_price = int(max_price)
            if self._max_price > self._min_price:
                logger.info(f'UserQuery set_max_price [{max_price}].')
            else:
                logger.info(f'UserQuery set_max_price error: [{self._min_price}] >= [{self._max_price}]')
                max_value = max(self._min_price, self._max_price)
                min_value = min(self._min_price, self._max_price)
                self._max_price = max_value
                self._min_price = min_value
                logger.info('UserQuery set_max_price change min and max values.')
            return True
        except ValueError as e:
            logger.error(f'UserQuery set_max_price error: {e}.')
            return False
    
    def _set_min_dist(self, min_dist: str) -> bool:
        try:
            self._min_dist = int(min_dist)
            logger.info(f'UserQuery set_min_dist [{min_dist}].')
            return True
        except ValueError as e:
            logger.error(f'UserQuery set_min_dist error: {e}.')
            return False
    
    def _set_max_dist(self, max_dist: str) -> bool:
        try:
            self._max_dist = int(max_dist)
            if self._max_dist > self._min_dist:
                logger.info(f'UserQuery set_max_dist [{max_dist}].')
            else:
                logger.info(f'UserQuery set_max_dist error: [{self._min_dist}] >= [{self._max_dist}]')
                max_value = max(self._min_dist, self._max_dist)
                min_value = min(self._min_dist, self._max_dist)
                self._max_dist = max_value
                self._min_dist = min_value
                logger.info('UserQuery set_max_dist change min and max values.')
            return True
        except ValueError as e:
            logger.error(f'UserQuery set_max_dist error: {e}.')
            return False
    
    def _set_results_num(self, results_num: str) -> bool:
        try:
            self._results_num = int(results_num)
            if self._results_num > int(environ.get('MAX_RESULTS')):
                self._results_num = int(environ.get('MAX_RESULTS'))
            logger.info(f'UserQuery set_results_num [{results_num}].')
            return True
        except ValueError as e:
            logger.error(f'UserQuery set_results_num error: {e}.')
            return False
    
    def _set_display_photos(self, display_photos: str) -> bool:
        variants = {
            DISPLAY_PHOTOS_TRUE.lower(): True,
            DISPLAY_PHOTOS_FALSE.lower(): False,
        }
        try:
            self._display_photos = variants[display_photos.lower()]
            logger.info(
                f'UserQuery set_display_photos [{self._display_photos}].'
            )
            return True
        except KeyError as e:
            self._display_photos = False
            logger.error(f'UserQuery set_display_photos error: {e}')
            return False

    def update(self,
        town_id: str='',
        min_price: str='',
        max_price: str='',
        min_dist: str='',
        max_dist: str='',
        results_num: str='',
        display_photos: str=''
    ):
        result = True
        try:
            if len(town_id) > 0:
                if self._set_town_id(town_id) == False:
                    result = False
            if len(min_price) > 0:
                if self._set_min_price(min_price) == False:
                    result = False
            if len(max_price) > 0:
                if self._set_max_price(max_price) == False:
                    result = False
            if len(min_dist) > 0:
                if self._set_min_dist(min_dist) == False:
                    result = False
            if len(max_dist) > 0:
                if self._set_max_dist(max_dist) == False:
                    result = False
            if len(results_num) > 0:
                if self._set_results_num(results_num) == False:
                    result = False
            if len(display_photos) > 0:
                if self._set_display_photos(display_photos) == False:
                    result = False
            return result
        except Exception as e:
            logger.error(f'UserQuery update error: {e}')
            return False
    
    @property
    def command(self) -> str:
        return self._command
    
    @property
    def dictionary(self) -> dict:
        attr_dict = {
            '/lowprice': {
                'command': 'command',
                'town_id': '_town_id', 
                'results_num': '_results_num', 
                'display_photos': '_display_photos',
            },
            '/highprice': {
                'command': 'command',
                'town_id': '_town_id', 
                'results_num': '_results_num', 
                'display_photos': '_display_photos',
            },
            '/bestdeal': {
                'command': 'command',
                'town_id': '_town_id', 
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
                
        return dict() if is_error else result

    def __str__(self):
        userquery_dict = self.dictionary
        result = 'UserQuery entity:\n'
        if len(userquery_dict) == 0:
            result += 'None'
        else:
            for key, value in userquery_dict.items():
                result += f'{key}:\t{value}\n'
        return result


class Session:
    def __init__(self):
        self._session_dist = dict()
        logger.info('Session entity created.')
    
    def create(self, chat_id: str, command: str) -> bool:
        try:
            self._session_dist[chat_id] = UserQuery(command)
            logger.info(
                f'Session create new session chat_id [{chat_id}] by [{command}].'
            )
            logger.info(f'Session size: {len(self._session_dist)}')
            return True
        except Exception as e:
            logger.error(f'Session create error: {e}.')
            return False
    
    def clear(self, chat_id: str) -> bool:
        try:
            del self._session_dist[chat_id]
            logger.info(f'Session clear session [{chat_id}].')
            return True
        except KeyError as e:
            logger.error(f'Session clear error: {e}.')
            return False
    
    def update(self, chat_id: str, attr: str, value: str) -> bool:
        """
        Update data in session by chat_id.
        chat_id: str
        attr: str = town_id | min_price | max_price | min_distance | max_distance | results_num | display_photos
        value: str
        """
        attr_set = (
            'town_id',
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
        
        return result
    
    def get_session_dict(self, chat_id: str) -> dict:
        user_data: UserQuery = self._session_dist[chat_id]
        result = user_data.dictionary
        result['chat_id'] = chat_id
        return result
    
    def __str__(self):
        return f'Session entity:\n {self._session_dist.keys()}\nTotal: {len(self._session_dist)}'


class Hotel:
    def _get_id(self) -> bool:
        try:
            self._id = self._data_dict['id']
            return True
        except KeyError as e:
            logger.error(f'Hotel _get_id error: {e}.')
            return False
    
    def _get_name(self) -> bool:
        try:
            self._name = self._data_dict['name']
            return True
        except KeyError as e:
            logger.error(f'Hotel _get_name error: {e}.')
            return False
    
    def _get_address(self) -> bool:
        address_list = list()
        try:
            address_dict = self._data_dict['address']
            for _i in address_dict.values():
                if _i:
                    address_list.append(_i)
            self._address = ', '.join(address_list)
            return True
        except KeyError as e:
            logger.error(f'Hotel _get_address error: {e}.')
            return False

    def _get_distance(self) -> bool:
        try:
            landmarks = self._data_dict['landmarks']
            for _landmark in landmarks:
                if _landmark['label'].lower() == 'центр города':
                    distance = _landmark['distance']
                    break
            if distance:
                self._distance = distance
                return True
            else:
                return False
        except KeyError as e:
            logger.error(f'Hotel _get_distance error: {e}.')
            return False
    
    def _get_price(self) -> bool:
        try:
            rate_plan = self._data_dict['ratePlan']
            price_dict = rate_plan['price']
            self._price = price_dict['current']
            return True
        except KeyError as e:
            logger.error(f'Hotel _get_price error: {e}.')
            return False


    def __init__(self, data_dict: dict):
        self._data_dict = data_dict
        
    def parse(self) -> bool:
        return (
            self._get_id() and 
            self._get_name() and 
            self._get_address() and 
            self._get_distance() and 
            self._get_price()
        )
    
    @property
    def dictionary(self):
        return {
            'id': self._id,
            'name': self._name,
            'address': self._address,
            'distance': self._distance
        }
    
    @property
    def price(self):
        return self._price

    
