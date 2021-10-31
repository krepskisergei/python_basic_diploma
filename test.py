import config

class Query:
    """
    Класс запроса пользователя
    Содержит данные для lowprice, highprice
    """
    __type: str
    __town: str = None
    __hotels_count: int = None
    __show_photo: bool = None
    
    def __init__(self, type: str) -> None:
        self.__type = type
        
    @property
    def type(self) -> str:
        return self.__type
    
    @property
    def town(self) -> str:
        return self.__town
    
    @property
    def hotels_count(self) -> int:
        return self.__hotels_count
    
    @property
    def show_photo(self) -> bool:
        return self.__show_photo
    
    @town.setter
    def town(self, town: str) -> None:
        self.__town = town
    
    @hotels_count.setter
    def hotels_count(self, hotels_count: int) -> None:
        self.__hotels_count = hotels_count \
            if hotels_count < config.RESULT_MAX_COUNT \
            else config.RESULT_MAX_COUNT
    
    @show_photo.setter
    def show_photo(self, show_photo: bool) -> None:
        self.__show_photo = show_photo


class BestDealQuery(Query):
    """
    Дочерний класс для запроса bestdeal.
    Объявляется без переменных.
    """
    __min_price: int = None
    __max_price: int = None
    __max_distance: int = None
    
    def __init__(self):
        super().__init__('bestdeal')
    
    @property
    def min_price(self) -> int:
        return self.__min_price
    
    @property
    def max_price(self) -> int:
        return self.__max_price
    
    @property
    def max_distance(self) -> int:
        return self.__max_distance
    
    @min_price.setter
    def min_price(self, min_price: int) -> None:
        self.__min_price = min_price
    
    @max_price.setter
    def max_price(self, max_price: int) -> None:
        self.__max_price = max_price
    
    @max_distance.setter
    def max_distance(self, max_distance: int) -> None:
        self.__max_distance = max_distance

q = BestDealQuery()
print(q.type)
print(q.town)
print(q.hotels_count)
print(q.show_photo)
q.town = 'Moscow'
q.hotels_count = 12
q.show_photo = False
print(q.type)
print(q.town)
print(q.hotels_count)
print(q.show_photo)