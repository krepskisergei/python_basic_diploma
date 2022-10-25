import sqlite3
from os import path, getcwd

from app.app_logger import get_logger


# initiate logger
logger = get_logger(__name__)


class DBConnector:
    """Basic class with SQLite database methods."""
    _conn: sqlite3.Connection

    def __init__(self, engine: str) -> None:
        """Create database instance by engine."""
        self._engine = engine
        self._connect()

    def _connect(self) -> None:
        """Add database connection to instance."""
        create = False
        db_path = path.join(getcwd(), self._engine)
        if not path.exists(db_path):
            create = True
        try:
            self._conn = sqlite3.connect(
                db_path,
                detect_types=sqlite3.PARSE_DECLTYPES,
                check_same_thread=False
            )
            logger.debug(f'Database connection to [{self._engine}] created.')
        except sqlite3.Error as e:
            raise self.DBConnectionError(*e.args)
        if create:
            self._create()

    def _create(self) -> None:
        """Create database structure from schema.sql file."""
        fn_dir = 'data'
        fn = 'schema.sql'
        fn_path = path.join(getcwd(), fn_dir, fn)
        if not path.exists(fn_path):
            raise self.DBConnectionError(
                f'SQL schema file [{fn_path}] not exists.')
        cursor = self._conn.cursor()
        with open(fn_path, 'r') as f:
            try:
                cursor.executescript(f.read())
                cursor.close()
                self._conn.commit()
                logger.debug(f'Database structure created from [{fn_path}].')
            except sqlite3.Error as e:
                cursor.close()
                self._conn.rollback()
                raise self._get_exception(e)

    # SQL methods
    def _select_one(
        self, q: str,
            v: list = [], rf: object = None) -> tuple | dict | int | str:
        """Return fetchone result of SQL query with rf row_factory."""
        logger.debug('_select_one query', q, v, rf)
        with self._conn.cursor() as c:
            if rf is not None:
                c.row_factory = self._row_factory(rf)
            try:
                c.execute(q, v)
                return c.fetchone()
            except sqlite3.Error as e:
                raise self._get_exception(e)

    def _select_all(
        self, q: str,
            v: list = [], rf: dict = None) -> list:
        """Return fetchall result of SQL query with rf row_factory."""
        logger.debug('_select_all query', q, v, rf)
        with self._conn.cursor() as c:
            if rf is not None:
                c.row_factory = self._row_factory(rf)
            try:
                c.execute(q, v)
                return c.fetchall()
            except sqlite3.Error as e:
                raise self._get_exception(e)

    def _update(self, q: str, v: list = []) -> None:
        """Execute update (INSERT, UPDATE) SQL query."""
        logger.debug('_update query', q, v)
        with self._conn.cursor() as c:
            try:
                c.execute(q, v)
                self._conn.commit()
            except sqlite3.Error as e:
                self._conn.rollback()
                raise self._get_exception(e)

    # Row factories
    def _row_factory(self, rf: dict | int | str = None) -> object:
        """Return row factory according rf instance."""
        def dict_factory(cursor: sqlite3.Cursor, row: sqlite3.Row) -> dict:
            """Dict row factory."""
            if row is None:
                return None
            data = {}
            for idx, col in enumerate(cursor.description):
                data[col[0]] = row[idx]
            return data

        def str_int_factory(row: sqlite3.Row) -> int | str:
            """Simple row factory for int and str."""
            if row is None:
                return None
            return row[0]

        if isinstance(rf, dict):
            return dict_factory
        if isinstance(rf, str) or isinstance(rf, int):
            return str_int_factory
        return None

    # Exceptions classes
    class _DBError(Exception):
        """Basic exception with logging."""
        _log_level = 0

        def __init__(self, *args: object) -> None:
            """Initiate DBError exception."""
            if self._log_level > 0:
                msg = ''
                if args:
                    msg = ' '.join(map(str, args))
                logger.log_msg(self._log_level, msg)
            super().__init__(*args)

    class DBConnectionError(_DBError):
        """Connection errors exception. Halt running."""
        _log_level = logger.CRITICAL

        def __init__(self, *args: object) -> None:
            super().__init__(*args)
            from sys import exit

            exit(128)

    class DBSyntaxError(_DBError):
        """SQL syntax errors exception."""
        _log_level = logger.DEBUG

    class DBUniqueError(_DBError):
        """SQL unique error exception."""
        _log_level = logger.INFO

    class DBDataError(_DBError):
        """SQL data errors exception."""
        _log_level = logger.WARNING

    class DBError(_DBError):
        """Unknown errors exception."""
        _log_level = logger.DEBUG

    # Exception methods
    def _get_exception(self, e: Exception) -> _DBError:
        """Return DBError subclass exceptions."""
        # DBUniqueError
        if isinstance(e, sqlite3.IntegrityError) and \
                str(e).upper().startswith('UNIQUE'):
            return self.DBUniqueError(*e.args)
        # DBSyntaxError
        if isinstance(e, sqlite3.OperationalError):
            return self.DBSyntaxError(*e.args)
        # DBDataError
        if isinstance(e, sqlite3.DatabaseError):
            raise self.DBDataError(*e.args)
        # other
        return self.DBError(*e.args)
