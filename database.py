import aiosqlite
import logging
from config import DATABASE_NAME










#-----------------------------------------------------------------------------------------------------------------------Инициализация базы данных
async def init_db():
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            # Создание таблицы users, если она еще не существует
            await db.execute(""
                             "CREATE TABLE IF NOT EXISTS users ("
                             "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                             "user_id INTEGER UNIQUE, "
                             "first_name TEXT, "
                             "last_name TEXT, "
                             "username TEXT, "
                             "user_added INTEGER NOT NULL, "
                             "user_blocked INTEGER NOT NULL, "
                             "type_of_notification TEXT, "
                             "notification_frequency TEXT,"
                             "created_at INTEGER)"
                             "")
            # Создание таблицы products, если она еще не существует
            await db.execute(""
                             "CREATE TABLE IF NOT EXISTS products ("
                             "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                             "user_id INTEGER NOT NULL,"
                             "product_url TEXT NOT NULL,"
                             "product_title  TEXT NOT NULL,"
                             "product_image_url TEXT,"
                             "FOREIGN KEY (user_id) REFERENCES users(id))"
                             "")
            # Создание таблицы product_price_history, если она еще не существует
            await db.execute(""
                             "CREATE TABLE IF NOT EXISTS product_price_history ("
                             "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                             "product_id INTEGER NOT NULL,"
                             "product_availability_status TEXT,"
                             "product_price REAL NOT NULL,"
                             "product_data_retrieval_time INTEGER,"
                             "FOREIGN KEY (product_id) REFERENCES products(id))"
                             "")
            await db.commit()
    except aiosqlite.Error as e:
        logging.error(f"Ошибка при инициализации базы данных: {e}")

#-----------------------------------------------------------------------------------------------------------------------добавление товара в базу
async def add_product(
    user_id: int,
    product_url: str,
    product_title: str,
    product_image_url: str,
    product_price: float,
    product_availability_status: str,
    product_data_retrieval_time: int
):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            # Проверяем есть ли такой продукт
            async with db.execute("SELECT * FROM products WHERE product_url = ? AND user_id = ?",
                                  (product_url, user_id,)) as cursor:
                result = await cursor.fetchone()
                if result is  None:
                    # Если не существует, добавляем новый продукт
                    await db.execute(""
                                     "INSERT INTO products ("
                                     "user_id,"
                                     "product_url,"
                                     "product_title,"
                                     "product_image_url"
                                     ") VALUES (?, ?, ?, ?)",(
                        user_id,
                        product_url,
                        product_title,
                        product_image_url,
                    ))
                    await db.commit()

    except Exception as e:
        logging.error(f"Ошибка при добавлении продукта: {e}")
