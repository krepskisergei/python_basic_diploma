# python_basic_diploma/app/database.py
"""Database class for Sqlite3"""
import sqlite3
from os import path, getcwd, environ
from sys import exit

from app.logger import get_logger


logger = get_logger(__name__)


class Database:
    """Sqlite3 Database class"""
    def __init__(self, database_name: str) -> None:
        def dict_factory(cursor, row) -> dict:
            """Return values from database as dict."""
            d = dict()
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d
        
        logger.debug(
            f'Create Database entity. Database name [{database_name}].'
        )
        self._database_name = database_name
        self._conn = self._connection()
        self._conn.row_factory = dict_factory
        logger.info(f'Connection to database [{database_name}] established.')
    
    def _create_db(self):
        """Create database and tables."""
        logger.debug('Start _create_db function.')
        try:
            connection = sqlite3.connect(f'{self._database_name}.sqlite')
            logger.info(f'Database [{self._database_name}] created.')
            cursor = connection.cursor()
            try:
                with open(path.join(getcwd(), 'schema.sql'), 'r') as f:
                    queries = f.read().split(';')
                for query in queries:
                    cursor.execute(query)
                logger.info(f'Database tables created.')
                connection.commit()
                cursor.close()
            except FileExistsError as e:
                logger.error(f'SQLite _create_db error: {e}.')
        except Exception as e:
            logger.error(f'SQLite _create_db error: {e}.')
        logger.debug('End _create_db function.')

    def _connection(self):
        """Return connection to database."""
        logger.debug('Start _connection function.')
        db_name = f'{self._database_name}.sqlite'
        db_path = path.join(getcwd(), db_name)
        if not path.exists(db_path):
            self._create_db()
        logger.debug('End _connection function.')
        return sqlite3.connect(db_name, check_same_thread=False)
    
    def _execute_query(
        self, query: str, values: list=[], 
        select: bool=False, lastrowid: bool = False) -> list | int | None:
        logger.debug((
            'Start _execute_query(\n'
            f'\tquery={query},\n\tvalues={values}\n'
            f'\tselect={select}\n\tlastrowid={lastrowid}\n)'
        ))
        if select:
            lastrowid = False
        try:
            cursor = self._conn.cursor()
            if len(values) > 0:
                cursor.execute(query, values)
            else:
                cursor.execute(query)
            if select:
                result = cursor.fetchall()
                logger.info(f'SQLite query fetch {len(result)} results.')
            else:
                self._conn.commit()
                logger.info('SQLite query complete.')
                if lastrowid:
                    return cursor.lastrowid
            cursor.close()
            logger.debug('End _execute_query function.')
            return result if select else None
        except Exception as e:
            logger.error(f'SQLite _execute_query error: {e}.')
            return None
    
    def _insert_dict(
        self, table: str, data: dict, last_row_id: bool=False) -> int | bool:
        logger.debug((
            'Start _insert_dict(\n'
            f'\ttable={table},\n\tdata={data}\nlast_row_id={last_row_id}\n)'
        ))
        columns = list()
        values = list()
        for key, value in data.items():
            columns.append(key)
            values.append(value)
        query = 'INSERT INTO {table} ({columns}) VALUES ({values})'.format(
            table=table,
            columns=', '.join(columns),
            values=', '.join('?' * len(values))
        )
        try:
            result = self._execute_query(
                query=query, values=values, select=False, lastrowid=True
            )
            logger.debug('End _insert_dict function.')
            if last_row_id:
                return result
            else:
                return True
        except Exception as e:
            logger.error(f'SQLite _insert_dict error: {e}.')
            return False
    
    def insert_town(self, town_dict: dict) -> bool:
        logger.debug((
            'insert_town(\n'
            f'\ttown_dict={town_dict}\n)'
        ))
        try:
            return self._insert_dict('town_ids', town_dict)
        except Exception as e:
            logger.error(f'SQLite insert town error: {e}.')
            return False
    
    def select_town(self, town_name: str) -> list:
        logger.debug(f'select_town(town_name={town_name})')
        select_town_query = (
            'SELECT name, destinationId, caption FROM town_ids '
            f'WHERE name = "{town_name.lower().title()}" '
            f'OR caption LIKE "{town_name}"'
        )
        return self._execute_query(query=select_town_query, select=True)
    
    def insert_session(self, session_dict: dict) -> int:
        logger.debug(f'insert_session(\n\tsession_dict={session_dict}\n)')
        try:
            return self._insert_dict(
                'users_history', session_dict, last_row_id=True
            )
        except sqlite3.Error as e:
            logger.error(f'SQLite insert_session error: {e}.')
            return 0
    
    def insert_hotel_and_search_result(
        self, user_session_id: int, hotel_dict: dict, price: str) -> int:
        """
        Insert hotel data (if not exists) and search result data in database.
        Return hotel_id.
        """
        logger.debug((
            'insert_hotel_and_search_result(\n'
            f'\tuser_session_id={user_session_id}\n'
            f'\thotel_dict={hotel_dict}\n'
            f'\tprice={price}\n)'
        ))
        # check hotel id in database
        query = (
            f"SELECT id FROM hotels WHERE id={hotel_dict['id']}"
        )
        try:
            result = self._execute_query(query=query, select=True)
            if len(result) > 0:
                hotel_id = result[0]['id']
            else:
                hotel_id = self._insert_dict(
                    table='hotels', data=hotel_dict, last_row_id=True
                )
            search_result = {
                'user_history_id': user_session_id,
                'hotel_id': hotel_id,
                'hotel_price': price
            }
            if self._insert_dict(table='search_results', data=search_result):
                return hotel_id
        except sqlite3.Error as e:
            logger.error(f'SQLite insert_hotel error: {e}.')
            return 0
    
    def insert_hotel_photos(self, hotel_id: int, photos: list) -> bool:
        logger.debug((
            'insert_hotel_photos(\n'
            f'\thotel_id={hotel_id}\n\tphotos={photos}\n)'
        ))
        try:
            for photo in photos:
                data = {
                    'hotel_id': hotel_id,
                    'url': photo
                }
                self._insert_dict(table='hotel_photos', data=data)
            return True
        except sqlite3.Error as e:
            logger.error(f'insert_hotel_photos error: {e}.')
            return False
    
    def get_hotel_photos(self, hotel_id: int) -> list:
        logger.debug(f'get_hote_photos(hotel_id={hotel_id})')
        query = (f'SELECT url FROM hotel_photos WHERE hotel_id={hotel_id}')
        return self._execute_query(query=query, select=True)


DB_NAME = environ.get('BOT_DB_NAME')
if DB_NAME:
    db = Database(DB_NAME)
else:
    logger.critical('No database name in environment.')
    exit()
