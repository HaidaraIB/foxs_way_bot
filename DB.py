import sqlite3
import os
import re
import datetime
from asyncio import Lock

lock = Lock()


def lock_and_release(func):
    async def wrapper(*args, **kwargs):
        db = None
        cr = None
        try:
            await lock.acquire()
            db = sqlite3.connect(os.getenv("DB_PATH"))
            db.row_factory = sqlite3.Row
            cr = db.cursor()
            result = await func(*args, **kwargs, cr=cr)
            db.commit()
            if result:
                return result
        except sqlite3.Error as e:
            print(e)
        finally:
            cr.close()
            db.close()
            lock.release()

    return wrapper


def connect_and_close(func):
    def wrapper(*args, **kwargs):
        db = sqlite3.connect(os.getenv("DB_PATH"))
        db.row_factory = sqlite3.Row
        db.create_function("REGEXP", 2, regexp)
        cr = db.cursor()
        result = func(*args, **kwargs, cr=cr)
        cr.close()
        db.close()
        return result

    return wrapper


def regexp(expr, item):
    reg = re.compile(expr)
    return reg.search(item) is not None


class DB:

    @staticmethod
    def creat_tables():
        db = sqlite3.connect(os.getenv("DB_PATH"))
        cr = db.cursor()
        script = f"""

            CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY,
                name TEXT,
                username TEXT,
                banned INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS buy_orders(
                serial INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                buy_what TEXT,
                exchange_of TEXT,
                amount_to_buy REAL,
                exchange_amount REAL,
                amount_to_buy_curr TEXT,
                exchange_curr TEXT,
                percentage REAL,
                wallet TEXT,
                order_date TEXT,
                state TEXT DEFAULT 'processing',
                message_id INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS sell_orders(
                serial INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                sell_what TEXT,
                exchange_of TEXT,
                amount_to_sell REAL,
                exchange_amount REAL,
                amount_to_sell_curr TEXT,
                exchange_curr TEXT,
                percentage REAL,
                wallet TEXT,
                order_date TEXT,
                state TEXT DEFAULT 'processing',
                message_id INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS admins(
                id INTEGER PRIMARY KEY
            );


            INSERT OR IGNORE INTO admins VALUES({os.getenv("OWNER_ID")});

        """
        cr.executescript(script)

        db.commit()
        cr.close()
        db.close()

    @staticmethod
    @lock_and_release
    async def add_buy_order(
        user_id: int,
        buy_what: str,
        exchange_of: str,
        amount_to_buy: float,
        exchange_amount: float,
        percentage: float,
        wallet: str,
        amount_to_buy_curr: str,
        exchange_curr: str,
        cr: sqlite3.Cursor = None,
    ):
        cr.execute(
            """
                INSERT OR IGNORE INTO buy_orders(
                    user_id,
                    buy_what,
                    exchange_of,
                    amount_to_buy,
                    exchange_amount,
                    percentage,
                    wallet,
                    amount_to_buy_curr,
                    exchange_curr,
                    order_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                buy_what,
                exchange_of,
                amount_to_buy,
                exchange_amount,
                percentage,
                wallet,
                amount_to_buy_curr,
                exchange_curr,
                str(datetime.datetime.now().replace(microsecond=0)),
            ),
        )
        return cr.lastrowid
    

    @staticmethod
    @lock_and_release
    async def add_sell_order(
        user_id: int,
        sell_what: str,
        exchange_of: str,
        amount_to_sell: float,
        exchange_amount: float,
        percentage: float,
        wallet: str,
        amount_to_sell_curr: str,
        exchange_curr: str,
        cr: sqlite3.Cursor = None,
    ):
        cr.execute(
            """
                INSERT OR IGNORE INTO sell_orders(
                    user_id,
                    sell_what,
                    exchange_of,
                    amount_to_sell,
                    exchange_amount,
                    percentage,
                    wallet,
                    amount_to_sell_curr,
                    exchange_curr,
                    order_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                sell_what,
                exchange_of,
                amount_to_sell,
                exchange_amount,
                percentage,
                wallet,
                amount_to_sell_curr,
                exchange_curr,
                str(datetime.datetime.now().replace(microsecond=0)),
            ),
        )
        return cr.lastrowid

    @staticmethod
    @lock_and_release
    async def add_message_id(
        serial: int,
        message_id: int,
        op: str,
        cr: sqlite3.Cursor = None,
    ):
        cr.execute(
            f"UPDATE {op}_orders SET message_id = ? WHERE serial = ?",
            (
                message_id,
                serial,
            ),
        )
    
    @staticmethod
    @lock_and_release
    async def update_state(serial:int, op:str, state:str, cr:sqlite3.Cursor = None):
        cr.execute(f"UPDATE {op}_orders SET state = ? WHERE serial = ?", (state, serial))

    @staticmethod
    @connect_and_close
    def get_order(serial: int, op: str, cr: sqlite3.Cursor = None):
        cr.execute(f"SELECT * FROM {op}_orders WHERE serial = ?", (serial,))
        return cr.fetchone()

    @staticmethod
    @connect_and_close
    def check_admin(user_id: int, cr: sqlite3.Cursor = None):
        cr.execute(
            "SELECT * FROM admins WHERE id = ?",
            (user_id, ),
        )
        return cr.fetchone()

    @staticmethod
    @connect_and_close
    def get_admin_ids(cr: sqlite3.Cursor = None):
        cr.execute("SELECT * FROM admins")
        return cr.fetchall()

    @staticmethod
    @lock_and_release
    async def add_new_user(
        user_id: int, username: str, name: str, cr: sqlite3.Cursor = None
    ):
        username = username if username else " "
        name = name if name else " "
        cr.execute(
            "INSERT OR IGNORE INTO users(id, username, name) VALUES(?, ?, ?)",
            (user_id, username, name),
        )

    @staticmethod
    @lock_and_release
    async def add_new_admin(user_id: int, cr: sqlite3.Cursor = None):
        cr.execute(
            "INSERT OR IGNORE INTO admins(id) VALUES(?)",
            (user_id,),
        )

    @staticmethod
    @lock_and_release
    async def remove_admin(user_id: int, cr: sqlite3.Cursor = None):
        cr.execute(
            "DELETE FROM admins WHERE id = ?",
            (user_id,),
        )

    @staticmethod
    @connect_and_close
    def get_user(user_id: int, cr: sqlite3.Cursor = None):
        cr.execute(
            "SELECT * FROM users WHERE id = ?",
            (user_id,),
        )
        return cr.fetchone()

    @staticmethod
    @connect_and_close
    def get_all_users(cr: sqlite3.Cursor = None):
        cr.execute("SELECT * FROM users")
        return cr.fetchall()

    @staticmethod
    @lock_and_release
    async def set_banned(user_id:int, banned:int, cr:sqlite3.Cursor = None):
        cr.execute("UPDATE users SET banned = ? WHERE id = ?", (banned, user_id))