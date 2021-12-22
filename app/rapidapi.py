# python_basic_diploma/app/database.py
from requests import request
import json
from os import environ
from sys import exit
from datetime import datetime, timedelta
from app.classes import Hotel

from app.logger import get_logger


# initialize logger
logger = get_logger(__name__)

# load environment values
rapidapi_host = environ.get('RAPIDAPI_HOST')
rapidapi_key = environ.get('RAPIDAPI_KEY')
rapidapi_locale = environ.get('RAPIDAPI_LOCALE')
rapiapi_currency = environ.get('RAPIDAPI_CURRENCY')

if not rapidapi_host or not rapidapi_key:
    logger.critical('No RapidApi data.')
    exit()

# set default values if not exists
if not rapidapi_locale:
    rapidapi_locale = 'ru_RU'
if not rapiapi_currency:
    rapiapi_currency = 'RUB'
headers = {
    'x-rapidapi-host': rapidapi_host,
    'x-rapidapi-key': rapidapi_key
}


def get_town_list(town_name: str) -> list:
    """
    Return list of dicts(keys: name, destinationId, caption) with data.
    If error - return empty list.
    """
    logger.debug(f'get_town_list(town_name={town_name}) start.')
    result = list()

    url = f'https://{rapidapi_host}/locations/v2/search'
    querystring = {
        'query': town_name,
        'locale': rapidapi_locale,
        'currency': rapiapi_currency
    }
    try:
        responce = request(
            method='GET',
            url=url,
            headers=headers,
            params=querystring
        )
    except Exception as e:
        logger.error(
            f'get_town_list: error by getting town from RapidApi: {e}.')
        # return empty list
        return result
    
    data = json.loads(responce.text)
    for suggestion in data['suggestions']:
        if suggestion['group'].upper() == 'CITY_GROUP':
            entities = suggestion['entities']
            break
    else:
        # no CITY_GROUP in responce
        logger.debug(f'get_town_list: no CITY_GROUP in RapidApi responce.')
        return result
    
    for entity in entities:
        if entity['type'].upper() == 'CITY':
            caption = entity['caption'].replace(
                "<span class='highlighted'>", ""
            ).replace("</span>", "")
            result.append({
                'name': entity['name'],
                'destinationId': entity['destinationId'],
                'caption': caption
            })
    
    logger.debug(f'get_town_id return [{len(result)}] results.')
    return result


def get_hotels_list(user_query_dict: dict) -> list:
    """
    Return list of data with hotels.
    Attributes:
        user_query_dict - UserQuery.dictionary or Session.dictionary result
    Result is source for Hotel class instance.
    If error return empty list.
    """
    logger.debug(f'get_hotels_list(user_query_dict={user_query_dict}) start.')
    result = list()
    url = 'https://hotels4.p.rapidapi.com/properties/list'

    # get current date
    td = datetime.now()
    tm = td + timedelta(days=1)
    td = td.strftime('%Y-%m-%d')
    tm = tm.strftime('%Y-%m-%d')

    # get page numbers
    results_num = user_query_dict['results_num']
    max_page_results = 25
    pages_num = results_num // max_page_results
    if results_num % max_page_results > 0:
        pages_num += 1

    if pages_num == 1:
        page_size = min(max_page_results, results_num)
    else:
        page_size = max_page_results
    logger.debug(f'get_totels_list: pageSize={page_size}, pages={pages_num}.')
    
    # set common querystring
    querystring = {
        'destinationId': str(user_query_dict['town_id']),
        'pageSize': page_size,
        'checkIn': td,
        'checkOut': tm,
        'adults1': '1',
        'locale': rapidapi_locale,
        'currency': rapiapi_currency
    }

    # change querystring by command
    match user_query_dict['command']:
        case '/lowprice':
            querystring['sortOrder'] = 'PRICE'
        case '/highprice':
            querystring['sortOrder'] = 'PRICE_HIGHEST_FIRST'
        case '/bestdeal':
            querystring['sortOrder'] = 'PRICE'
            querystring['priceMin'] = user_query_dict['min_price']
            querystring['priceMax'] = user_query_dict['max_price']
    
    for _page in range(1, pages_num + 1):
        querystring['pageNumber'] = _page
        logger.debug(f'get_hotels_list query: {querystring}.')

        try:
            responce = request(
                method='GET', url=url, headers=headers, params=querystring
            )
            data = json.loads(responce.text)

            try:
                data_list = data['data']['body']['searchResults']['results']
                for _hotel_data in data_list:
                    hotel = Hotel(_hotel_data)
                    if hotel.parse():
                        result.append(hotel)
                    else:
                        logger.error(
                            'get_hotels_list error adding result to list.')
            
            except Exception as e:
                logger.error(f'get_hotels_list error: {e}.')
        except Exception as e:
            logger.error(f'get_hotels_list error: {e}.')
    logger.debug(f'get_hotels_list return {len(result)} results.')
    return result


def get_hotel_photos(hotel_id: str) -> list:
    """
    Return list of hotels photos urls.
    If error return empty list.
    """
    logger.debug(f'get_hotel_photos(hotel_id={hotel_id}) start.')
    max_num_photos = int(environ.get('MAX_PHOTOS'))
    url = 'https://hotels4.p.rapidapi.com/properties/get-hotel-photos'
    querystring = {'id': hotel_id}

    result = list()
    try:
        responce = request(
            method='get',
            url=url,
            headers=headers,
            params=querystring
        )
        
        data = json.loads(responce.text)
        try:
            for hotel_image in data['hotelImages']:
                # TODO: choose image sizes
                """
                1:  t
                2:  s
                3:  b
                9:  l
                11: n
                12: g
                13: d
                14: y
                15: z
                16: e
                17: w
                """
                result.append(
                    hotel_image['baseUrl'].replace('{size}', 'y')
                )
                if len(result) >= max_num_photos:
                    break
        except KeyError as e:
            logger.error(f'get_hotel_photos error: {e}.')

    except Exception as e:
        logger.error(f'get_hotel_photos error: {e}.')
    logger.debug(f'get_hotel_photos return {len(result)} results.')
    return result
