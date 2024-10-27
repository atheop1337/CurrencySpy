import aiosqlite
import logging
from typing import Union
from modules.libraries.utils import _Methods


class Database:
    def __init__(self, db: str):
        self.db_path = db

    async def create_tables(self):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.cursor() as cursor:
                await cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER UNIQUE,      
                        user_name TEXT NOT NULL,      
                        currency TEXT NOT NULL DEFAULT 'BTC',                                                     
                        interval INTEGER NOT NULL DEFAULT 300,
                        threshold INTEGER NOT NULL DEFAULT 50,
                        last_rate INTEGER
                    )
                    """
                )

                logging.info("Successfully created tables")
                await db.commit()

    async def add_user(self, user_id: int, user_name: str) -> Union[bool, int]:
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.cursor() as cursor:
                        await cursor.execute(
                            "INSERT INTO users (user_id, user_name) VALUES (?, ?)",
                            (user_id, user_name)
                        )
                        await db.commit()
                        logging.info(f"User {user_id} added successfully")
                        return True
        except aiosqlite.IntegrityError:
            logging.info(f"User with ID {user_id} already exists")
            return 409
        except Exception as e:
            logging.error(f"Failed to add user {user_id}: {e}")
            return False

    async def fetch_info(self, user_id: int) -> dict:
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.cursor() as cursor:
                    await cursor.execute(
                        "SELECT * FROM users WHERE user_id =?",
                        (user_id,)
                    )
                    result = await cursor.fetchone()
                    if result:
                        return {
                            "user_id": result[1],
                            "user_name": result[2],
                            "currency": result[3],
                            "interval": result[4],
                            "threshold": result[5],
                            "last_rate": result[6]
                        }
                    else:
                        logging.warning(f"No user found with ID {user_id}")
                        return None
        except Exception as e:
            logging.error(f"Failed to fetch user info for user {user_id}: {e}")
            return None

    async def info_updater(self, user_id: int, identity: str, value: any) -> bool:
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.cursor() as cursor:
                    await cursor.execute(
                        f"UPDATE users SET {identity} =? WHERE user_id =?",
                        (value, user_id)
                    )
                    await db.commit()
                    logging.info(f"User {user_id} updated successfully")
                    return True
        except Exception as e:
            logging.error(f"Failed to update user {user_id}: {e}")
            return False

    async def update_currency_price(self, user_id: int) -> bool:
        try:
            async with aiosqlite.connect(self.db_path) as db:
                async with db.cursor() as cursor:
                    await cursor.execute(
                        "SELECT currency FROM users WHERE user_id = ?",
                        (user_id,)
                    )
                    result = await cursor.fetchone()
                    
                    if result:
                        currency = result[0]
                        last_rate = await _Methods.get_currency_price(currency)
                        await cursor.execute(
                            "UPDATE users SET last_rate = ? WHERE user_id = ?",
                            (last_rate, user_id)
                        )
                        await db.commit()
                        logging.info(f"Currency price for user {user_id} updated successfully")
                        return True
                    else:
                        logging.warning(f"No currency found for user {user_id}")
                        return False
        except Exception as e:
            logging.error(f"Failed to get currency price for user {user_id}: {e}")
            return False
