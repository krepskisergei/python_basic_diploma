# location_id
LOCATION_ID_START = '🌍 Введите название города:'
LOCATION_ID_CLARIFY = 'Уточните город:'
LOCATION_ID_WRONG = '❌ Город не найден. Попробуйте еще раз.'
LOCATION_ID_COMPLETE = 'Выбран город 🌆 *{}*'
# check_in
CHECK_IN_START = '🗓 Выберите дату заезда:'
CHECK_IN_WRONG = '❌ Дата заезда не верная. Попробуйте еще раз.'
CHECK_IN_COMPLETE = 'Выбрана дата заезда 📆 *{}*.'
# check_out
CHECK_OUT_START = '🗓 Выберите дату выезда:'
CHECK_OUT_WRONG = '❌ Дата выезда не верная. Попробуйте еще раз.'
CHECK_OUT_COMPLETE = 'Выбрана дата выезда 📅 *{}*.'
# price_min
PRICE_MIN_START = '💰 Введите минимальную цену:'
PRICE_MIN_WRONG = '❌ Цена должа быть числом. Попробуйте еще раз.'
PRICE_MIN_COMPLETE = 'Минимальная цена 💰 *{:.2f} {}*.'
# price_max
PRICE_MAX_START = '💰 Введите максимальную цену:'
PRICE_MAX_WRONG = (
    '❌ Цена должа быть числом больше минимальной цены. '
    'Попробуйте еще раз.')
PRICE_MAX_COMPLETE = 'Максимальная цена 💰 *{:.2f} {}*.'
# distance_min
DISTANCE_MIN_START = '📏 Введите минимальное расстояние от центра города:'
DISTANCE_MIN_WRONG = (
    '❌ Расстояние должно быть числом больше нуля. Попробуйте еще раз')
DISTANCE_MIN_COMPLETE = (
    'Минимальное расстояние от центра города 📏 *{:.1f} {}*.')
# distance_max
DISTANCE_MAX_START = '📏 Введите максимальную удаленность от центра города:'
DISTANCE_MAX_WRONG = (
    '❌ Расстояние должно быть числом больше нуля '
    'и больше минимального расстояния. Попробуйте еще раз')
DISTANCE_MAX_COMPLETE = (
    'Максимальная удаленность от центра города 📏 *{:.1f}*.')
# results_num
RESULTS_NUM_START = '📝 Введите количество результатов (не больше {:d}):'
RESULTS_NUM_WRONG = (
    '❌ Количество должно быть числом больше нуля. Поробуйте еще раз.')
RESULTS_NUM_COMPLETE = 'Количество результатов 📝 *{:d}*.'
# photos_show
PHOTOS_SHOW_START = '🖼 Отображать фотографии?'
PHOTOS_SHOW_WRONG = 'Я не знаю такого значения'
# photos_num
PHOTOS_NUM_START = '🖼 Введителе количество фотографий отеля (не больше {:d}):'
PHOTOS_NUM_WRONG = '❌ Количество должно быть числом. Поробуйте еще раз.'
PHOTOS_NUM_COMPLETE = 'Количество фотографий 🖼 *{:d}*.'
# complete
COMPLETE_START = '🏨 Найдено предложений: *{:d}*'
COMPLETE_WRONG = '🛎 Предложений не найдено. Попробуйте еще раз.'

# Bot messages
UNKNOWN_ERROR = '😖 _Ooooppps_. Ошибка. 🤭'
ERROR_CONTENT = 'Извините, но зачем Вы мне это шлете? 🤷‍♂️'

# Command messages
COMMAND_LOWPRICE = 'Команда *LowPrice* покажет лучшие предложения.'
COMMAND_HIGHPRICE = 'Команда *HighPrice* покажет дорогие предложения.'
COMMAND_BESTDEAL = (
    'Команда *BestDeal* подберет лучшие предложения '
    'по заданной цене и расположению.')
COMMAND_START = """Добро пожаловать в *sb_too_easy_travel*.
Используйте следующие команды:
_/help_ — помощь по командам бота
_/lowprice_ — вывод самых дешёвых отелей в городе
_/highprice_ — вывод самых дорогих отелей в городе
_/bestdeal_ — вывод отелей, подходящих по цене и расположению от центра
_/history_ — вывод истории поиска отелей"""
COMMAND_HELP = """_/lowprice_ — вывод самых дешёвых отелей в городе
_/highprice_ — вывод самых дорогих отелей в городе
_/bestdeal_ — вывод отелей, подходящих по цене и расположению от центра
_/history_ — вывод истории поиска отелей"""

# SEARCH_RESULT
HOTEL_MESSAGE = """🏨 Отель *{}* {}
🌏 Адрес *{}*
🚶‍♂️ *{:.1f} {}* от центра
💰 Цена *{:.0f} {}*
"""
HOTEL_BOOK = 'Забронировать'

# UserSession
USER_SESSION = """⏲ *{}*
💬 команда {}
🌍 {}
🗓 {} - {}
{}📝 {:d}
🖼 {:d}
"""
USER_SESSION_FLOATS = """💰 {:.0f} - {:.0f} {}
📏 {:.1f} - {:.1f} {}
"""
