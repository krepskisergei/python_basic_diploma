import sqlite3
from os import path, getcwd

from app.logger import get_logger


# initiate logger
logger = get_logger(__name__)


class SqliteDatabase:
    """Basic class with SQLite database methods."""
    # Exception
    class DBError(Exception):
        """Basic class of database exception with logging."""
        _log_level: int = 0

        def __init__(self, *args) -> None:
            """Initiate DBError exception."""
            if self._log_level > 0:
                msg = ''
                if args:
                    msg = ' '.join(map(str, args))
                logger.log_message(msg, self._log_level)
            super().__init__(*args)

    class DBConnectionError(DBError):
        """Exception for connection errors. Halt running."""
        _log_level: int = logger.CRITICAL

        def __init__(self, *args) -> None:
            super().__init__(*args)
            from sys import exit
            exit(128)

    class DBDataError(DBError):
        """Exception for null affects for databse."""
        _log_level: int = logger.WARNING

    class DBSyntaxError(DBError):
        """Exception for SQL syntax errors."""
        _log_level: int = logger.DEBUG

    class DBUniqueError(DBError):
        """Exception for UNIQUE SQL errors."""
        _log_level: int = logger.INFO

    class DBUnknownError(DBError):
        """Exception for all unknown SQL errors."""
        _log_level: int = logger.DEBUG

    def _exception(self, e: Exception) -> DBError:
        """Return DBError subclass exceptions."""
        if isinstance(e, sqlite3.IntegrityError) and \
                str(e).upper().startswith('UNIQUE'):
            return self.DBUniqueError(*e.args)
        if isinstance(e, sqlite3.OperationalError):
            return self.DBSyntaxError(*e.args)
        if isinstance(e, sqlite3.DatabaseError):
            return self.DBDataError(*e.args)
        return self.DBUnknownError(*e.args)

    # SqliteDatabase
    def __init__(self, engine: str) -> None:
        """
        Create database connection by engine.
        """
        self._engine = engine
        self._connect()

    def _connect(self) -> None:
        """Add connection."""
        create_db = False
        db_path = path.join(getcwd(), self._engine)
        if not path.exists(db_path):
            create_db = True
        try:
            self._connection = sqlite3.connect(
                db_path,
                detect_types=sqlite3.PARSE_DECLTYPES,
                check_same_thread=False
            )
        except sqlite3.Error as e:
            raise self.DBConnectionError(str(e))
        if create_db:
            self._create_db()

    def _create_db(self) -> None:
        """Create db structure from schema.sql file."""
        schema_fn = 'schema.sql'
        schema_path = path.join(getcwd(), 'database', schema_fn)
        if not path.exists(schema_path):
            raise self.DBConnectionError('SQL schema file exists error.')
        cursor = self._connection.cursor()
        with open(schema_path, 'r') as f:
            try:
                cursor.executescript(f.read())
                cursor.close()
                self._connection.commit()
            except sqlite3.Error as e:
                cursor.close()
                self._connection.rollback()
                raise self._exception(e)

    def _row_factory(self, rf: dict | int | str = None) -> object:
        """Return row factory according rf instance."""
        def dict_factory(cursor: sqlite3.Cursor, row: sqlite3.Row) -> dict:
            """Dict row factory."""
            if row is None:
                return None
            result = {}
            for idx, col in enumerate(cursor.description):
                result[col[0]] = row[idx]
            return result

        def simple_factory(row: sqlite3.Row) -> int | str:
            """Simple row factory for int and str."""
            if row is None:
                return None
            return row[0]

        if isinstance(rf, dict):
            return dict_factory
        if isinstance(rf, int) or isinstance(rf, str):
            return simple_factory
        return None

    @logger.debug_func
    def _select_one(
        self, query: str, values: list = [],
            rf: dict | int | str = None) -> tuple | dict | int | str:
        """Return fetchone result of SQL query with rf row_factory."""
        cursor = self._connection.cursor()
        if rf is not None:
            cursor.row_factory = self._row_factory(rf)
        try:
            cursor.execute(query, values)
            result = cursor.fetchone()
            cursor.close()
        except sqlite3.Error as e:
            cursor.close()
            raise self._exception(e)
        return result

    @logger.debug_func
    def _select_all(
        self, query: str, values: list = [],
            rf: dict | int | str = None) -> list:
        """Return fetchall result of SQL query with rf row_factory."""
        cursor = self._connection.cursor()
        if rf is not None:
            cursor.row_factory = self._row_factory(rf)
        try:
            cursor.execute(query, values)
            result = cursor.fetchall()
            cursor.close()
        except sqlite3.Error as e:
            cursor.close()
            raise self._exception(e)
        return result

    @logger.debug_func
    def _update(self, query: str, values: list = []) -> None:
        """Execute update (INSERT, UPDATE) SQL query."""
        cursor = self._connection.cursor()
        try:
            cursor.execute(query, values)
            """
            TODO: sqlite3 allways return -1. Uncomment in postgresql.
            if cursor.rowcount == 0:
                raise self.DBDataError(
                    f'No affect with query: {query}', *values)
            """
            cursor.close()
            self._connection.commit()
        except sqlite3.Error as e:
            cursor.close()
            self._connection.rollback()
            raise self._exception(e)
