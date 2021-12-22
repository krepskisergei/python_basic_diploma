# python_basic_diploma/app/database.py
"""Database class for Sqlite3"""
import sqlite3
from os import path, getcwd, environ
from sys import exit

from app.logger import get_logger


# initialize logger
logger = get_logger(__name__)


class Database:
    """Sqlite3 Database class"""
    def __init__(self, database_name: str) -> None:
        """
        Create database connection.
        Attributes:
            database_name - name of sqlite3 (without .sqlite) database filename.
        """
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
        logger.debug('Database _create_db start.')
        
        connection = sqlite3.connect(f'{self._database_name}.sqlite')
        logger.info(
            f'Database created in file {self._database_name}.sqlite.')
        cursor = connection.cursor()
        try:
            with open(path.join(getcwd(), 'schema.sql'), 'r') as f:
                queries = f.read().split(';')
            try:
                for query in queries:
                    cursor.execute(query)
                logger.info(f'Database tables created.')
                connection.commit()
                cursor.close()
            except sqlite3.Error as e:
                logger.critical(f'Database _create_db SQL error: {e}.')
                exit()
        except FileExistsError as e:
            logger.error(f'Database _create_db schema file error: {e}.')
        logger.debug('End _create_db function.')

    def _connection(self):
        """Return connection to database."""
        logger.debug('Database _connection start.')
        db_name = f'{self._database_name}.sqlite'
        db_path = path.join(getcwd(), db_name)
        if not path.exists(db_path):
            self._create_db()
        logger.debug('Database _connection end.')
        return sqlite3.connect(db_name, check_same_thread=False)
    
    def _execute_query(
        self, query: str, values: list=[], 
        select: bool=False, lastrowid: bool = False) -> list | int | None:
        """
        Execute SQL query.
        Attributes:
            query - SQL query
            values - SQL query list of valuest (optional)
            select - set True if need to return SQL query results (use for SELECT queries)
            lastrowid - select True if need to return lastrowid (use for INSERT queries)
        Return:
            list - list of SQL SELECT query if select = True
            int - last_row_id of SQL INSERT query if lastrowid = True
            None - if select = False and lastrowid = False or SQL query error.
        """
        logger.debug((
            'Start _execute_query(\n'
            f'\tquery={query},\n\tvalues={values}\n'
            f'\tselect={select}\n\tlastrowid={lastrowid}\n) start.'
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
                logger.info(
                    f'Database _execute_query fetch {len(result)} results.')
            else:
                self._conn.commit()
                logger.info('Database _execute_query complete.')
                if lastrowid:
                    logger.debug(
                        f'Database _execute_query return {cursor.lastrowid}.')
                    return cursor.lastrowid
            cursor.close()
            logger.debug(f'Database _execute_query ends without errors.')
            return result if select else None
        except sqlite3.Error as e:
            logger.error(f'Database _execute_query error: {e}.')
            return None
    
    def _insert_dict(
        self, table: str, data: dict, last_row_id: bool=False) -> int | bool:
        """
        Generate SQL INSERT query and run it.
        Attributes:
            table - database table name
            data - dict with data (keys = table columnd, values = values)
            last_row_id - select True if need to return lastrowid
        Return:
            int - lastrowid if last_row_id = True
            True if ok, else return False.
        """
        logger.debug((
            'Database _insert_dict(\n'
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
            logger.debug('Database _insert_dict ends without errors.')
            if last_row_id:
                logger.debug(f'Database _insert_dict return {result}.')
                return result
            else:
                logger.debug('Database _insert_dict return True.')
                return True
        except sqlite3.Error as e:
            logger.error(f'Database _insert_dict error: {e}.')
            return False
    
    def insert_town(self, town_dict: dict) -> bool:
        """
        Set town data to database.
        Attributes:
            town_dict: dict with data (keys: name, destinationId, caption(optional))
        Return True if ok, else return False.
        """
        logger.debug(
            f'Database insert_town(town_dict={town_dict}) start.')
        try:
            return self._insert_dict('town_ids', town_dict)
        except Exception as e:
            logger.error(f'Database insert_town error: {e}.')
            return False
    
    def select_town(self, town_name: str) -> list:
        """
        Return list of dicts(name, destinationId, caption) from database.
        """
        logger.debug(f'Database select_town(town_name={town_name}) start.')
        select_town_query = (
            'SELECT name, destinationId, caption FROM town_ids '
            f'WHERE name = "{town_name.lower().title()}" '
            f'OR caption LIKE "{town_name}"'
        )
        return self._execute_query(query=select_town_query, select=True)
    
    def insert_session(self, session_dict: dict) -> int:
        """
        Insert UserQuery instance from Session instance.
        Attributes:
            session_dict - Session.dictionary
        Return last_row_id or 0 if error.
        """
        logger.debug(
            f'Database insert_session(session_dict={session_dict}) start.')
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
        Insert hotel data (if not exists) and search result in database.
        Attributes:
            user_session_id - Database.insert_session result
            hotel_dict - Hotel.dictionary
            price - Hotel.price
        Return hotel_id from hotels table.
        """
        logger.debug((
            'Database insert_hotel_and_search_result('
            f'user_session_id={user_session_id}, '
            f'hotel_dict={hotel_dict}, '
            f'price={price}) start.'
        ))
        # check hotel id in database
        query = (
            f"SELECT id FROM hotels WHERE id={hotel_dict['id']}")
        try:
            result = self._execute_query(query=query, select=True)
            if result and len(result) > 0:
                hotel_id = result[0]['id']
            else:
                hotel_id = self._insert_dict(
                    table='hotels', data=hotel_dict, last_row_id=True)
            search_result = {
                'user_history_id': user_session_id,
                'hotel_id': hotel_id,
                'hotel_price': price
            }
            if self._insert_dict(table='search_results', data=search_result):
                logger.debug((
                    'Database insert_hotel_and_search_result '
                    'return {hotel_id}.'))
                return hotel_id
            else:
                logger.error('Database insert_hotel_and_search_result error.')
                return 0
        except sqlite3.Error as e:
            logger.error(f'Database insert_hotel_and_search_result error: {e}.')
            return 0
    
    def insert_hotel_photos(self, hotel_id: int, photos: list) -> bool:
        """
        Insert photo url's to database.
        Attributes:
            hotel_id - Database.insert_hotel_and_search_result result
            photos - list of urls
        Return True if ok, else return False.
        """
        logger.debug((
            'Database insert_hotel_photos('
            f'hotel_id={hotel_id}, photos={photos}) start.'))
        try:
            for photo in photos:
                data = {
                    'hotel_id': hotel_id,
                    'url': photo
                }
                self._insert_dict(table='hotel_photos', data=data)
            logger.debug('Database insert_hotel_photos return True.')
            return True
        except sqlite3.Error as e:
            logger.error(f'Databse insert_hotel_photos error: {e}.')
            return False
    
    def get_hotel_photos(self, hotel_id: int) -> list:
        """
        Return list of dict(keys: url) with hotels photos urls by hotel_id.
        Attributes:
            hotel_id - Database.insert_hotel_and_search_result result
        """
        logger.debug(f'Database get_hotel_photos(hotel_id={hotel_id}) start.')
        query = (f'SELECT url FROM hotel_photos WHERE hotel_id={hotel_id}')
        return self._execute_query(query=query, select=True)


# get DB_NAME from environment
DB_NAME = environ.get('BOT_DB_NAME')
if DB_NAME:
    db = Database(DB_NAME)
else:
    logger.critical('No database name in environment.')
    exit()
