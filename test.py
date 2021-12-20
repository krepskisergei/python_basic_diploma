import unittest
from os import environ
from unittest.case import TestCase

from app.service import check_environment
from app.classes import UserQuery, Session
from app.dialogs import DISPLAY_PHOTOS_TRUE, DISPLAY_PHOTOS_FALSE


check_environment()
handler = '/bestdeal'
test_dict = {
    'command': handler,
    'town_id': 12345,
    'min_price': 100,
    'max_price': 200,
    'min_distance': 2,
    'max_distance': 5,
    'results_num': int(environ.get('MAX_RESULTS')),
    'display_photos': True
}

class UserQueryTest(unittest.TestCase):
    class_entity = UserQuery(handler)

    def test_update(self):
        self.assertEqual(
            self.class_entity.update(town_id='moscow'), False
        )
        self.assertEqual(
            self.class_entity.update(town_id=str(test_dict['town_id'])), 
            True
        )

        self.assertEqual(self.class_entity.update(min_price='-'), False)
        self.assertEqual(
            self.class_entity.update(min_price=str(test_dict['min_price'])), 
            True
        )

        self.assertEqual(self.class_entity.update(max_price='-'), False)
        self.assertEqual(
            self.class_entity.update(max_price=str(test_dict['max_price'])), 
            True
        )

        self.assertEqual(self.class_entity.update(min_dist='-'), False)
        self.assertEqual(
            self.class_entity.update(min_dist=str(test_dict['min_distance'])), 
            True
        )

        self.assertEqual(self.class_entity.update(max_dist='-'), False)
        self.assertEqual(
            self.class_entity.update(max_dist=str(test_dict['max_distance'])), 
            True
        )
        
        self.assertEqual(self.class_entity.update(results_num='-'), False)
        self.assertEqual(self.class_entity.update(results_num='10000'), True)

        self.assertEqual(self.class_entity.update(display_photos='-'), False)
        self.assertEqual(
            self.class_entity.update(display_photos=DISPLAY_PHOTOS_TRUE), 
            True
        )

        self.assertEqual(self.class_entity.dictionary, test_dict)


class SessionTest(unittest.TestCase):
    def test_session(self):
        sessions = Session()
        chat_id = '111111'
        chat_id_clear = 'test_clear'
        
        self.assertEqual(sessions.create(chat_id, handler), True)
        self.assertEqual(sessions.create(chat_id_clear, ''), True)
        self.assertEqual(sessions.clear(''), False)
        self.assertEqual(sessions.clear(chat_id_clear), True)

        for key, value in test_dict.items():
            if key == 'display_photos':
                value = DISPLAY_PHOTOS_TRUE
            if key != 'command':
                self.assertEqual(sessions.update(chat_id, key, str(value)), True, msg=key)

        


if __name__ == '__main__':
    unittest.main()
