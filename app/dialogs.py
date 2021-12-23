# python_basic_diploma/app/dialogs.py
"""Content all messages by bot"""
from os import environ

START_MESSAGE = """Добро пожаловать в *sb_too_easy_travel*.
Используйте следующие команды:
_/help_ — помощь по командам бота
_/lowprice_ — вывод самых дешёвых отелей в городе
_/highprice_ — вывод самых дорогих отелей в городе
_/bestdeal_ — вывод отелей, наиболее подходящих по цене и расположению от центра
_/history_ — вывод истории поиска отелей"""

HELP_MEASSAGE = """_/lowprice_ — вывод самых дешёвых отелей в городе
_/highprice_ — вывод самых дорогих отелей в городе
_/bestdeal_ — вывод отелей, наиболее подходящих по цене и расположению от центра
_/history_ — вывод истории поиска отелей"""

ERROR_CONTENT_MESSAGE = 'Извините, но зачем Вы мне это шлете? 🤷‍♂️'

UNKNOWN_ERROR_MESSAGE = 'Ooops'

LOWPRICE_MESSAGE = 'Команда *LowPrice* покажет лучшие предложения.'
HIGHPRICE_MESSSAGE = 'Команда *HighPrice* покажет дорогие предложения.'
BESTDEAL_MESSAGE = 'Команда *BestDeal* подберет лучшие предложения по заданной цене и расположению.'

GET_TOWN_MESSAGE = '*Введите название города*:'
WRONG_TOWN_MESSAGE = 'Я не знаю такого города. Попробуйте еще раз.'
TOWN_SELECTED_MESSAGE = 'Выбран город '
SELECT_TOWN_MESSAGE = 'Выберите нужный город или уточните запрос.'

GET_CHECK_IN_MESSAGE = 'День заезда'
GET_CHECK_OUT_MESSAGE = 'День выезда'

GET_RESULTS_NUM_MESSAGE = f'*Введите требуемое количество результатов* (1 - {environ.get("MAX_RESULTS")}):'
WRONG_RESULTS_NUM_MESSAGE = 'Количество должно быть числом.'
SELECT_RESULTS_NUM_MESSAGE = 'Количество результатов '

GET_DISPLAY_PHOTOS = '*Отображать фотографии*?'
DISPLAY_PHOTOS_TRUE = 'Да'
DISPLAY_PHOTOS_FALSE = 'Нет'
WRONG_DISPLAY_PHOTOS = 'Неизвестное значение. *Отображать фотографии*?'
SELECT_DISPLAY_PHOTOS = 'Отображать фотографии: '

GET_MIN_PRICE = 'Введите *минимальную* стоимость.'
GET_MAX_PRICE = 'Введите *максимальную* стоимость.'
WRONG_PRICE = 'Стоимость должна быть целым числом.'

GET_MIN_DISTANCE = 'Введите *минимальное* расстояние от центра (м).'
GET_MAX_DISTANCE = 'Введите *максимальное* расстояние от центра (м).'
WRONG_DISTANCE = 'Расстояние должно быть целым числом.'

RESULTS_MESSAGE = '*Найдено отелей:*'
NO_RESULTS_MESSAGE = 'Поиск не дал результатов. Попробуйте изменить параметры.'
HOTEL_URL_SCHEMA = 'https://ru.hotels.com/ho[id]/?q-check-in=[check_in]&q-check-out=[check_out]&q-rooms=1&q-room-0-adults=1&q-room-0-children=0'
HOTEL_DESCRIPTION = """🏨 Отель *[name]*
🌏 Адрес *[address]*
🚶‍♂️ *[distance]* от центра
💰 Цена *[price]*"""
HOTEL_BOOK_MESSAGE = 'Забронировать'
