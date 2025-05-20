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
                             "product_url TEXT NOT NULL,"
                             "product_title  TEXT NOT NULL,"
                             "product_image_url TEXT,"
                             "status INTEGER NOT NULL)"
                             "")

            # Создание таблицы product_price_history, если она еще не существует
            await db.execute(""
                             "CREATE TABLE IF NOT EXISTS product_price_history ("
                             "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                             "product_id INTEGER NOT NULL,"
                             "product_availability_status TEXT,"
                             "product_price REAL,"
                             "product_data_retrieval_time INTEGER)"
                             "")
            await db.commit()
    except aiosqlite.Error as e:
        logging.error(f"Ошибка при инициализации базы данных: {e}")

#-----------------------------------------------------------------------------------------------------------------------добавление товара в базу
async def add_new_product(
    product_url: str,
    product_title: str,
    product_image_url: str,
    product_price: float,
    product_availability_status: str,
    product_data_retrieval_time: int,
    status: int
):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            # Проверяем есть ли такой продукт
            async with db.execute("SELECT * FROM products WHERE product_url = ?",
                                  (product_url,)) as cursor:
                result = await cursor.fetchone()
                if result is  None:
                    # Если не существует, добавляем новый продукт
                    await db.execute(""
                                     "INSERT INTO products ("
                                     "product_url,"
                                     "product_title,"
                                     "product_image_url,"
                                     "status"
                                     ") VALUES (?, ?, ?, ?)",(
                        product_url,
                        product_title,
                        product_image_url,
                        status,
                    ))
                    await db.commit()


                    # Получение последнего добавленного ID
                    async with db.execute("SELECT last_insert_rowid()") as cursor:
                        row = await cursor.fetchone()
                        product_id = row[0]


                    # И если не существует, добавляем данные о ценах, наличии и датах
                    await db.execute(""
                                     "INSERT INTO product_price_history ("
                                     "product_id,"
                                     "product_availability_status,"
                                     "product_data_retrieval_time,"
                                     "product_price"
                                     ") VALUES (?, ?, ?, ?)", (
                                         product_id,
                                         product_availability_status,
                                         product_data_retrieval_time,
                                         product_price,
                                     ))


                    await db.commit()

    except Exception as e:
        logging.error(f"Ошибка при добавлении продукта: {e}")

#-----------------------------------------------------------------------------------------------------------------------Формируем список товаров которые надо обновлять
async def get_list_product():
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            # Получаем все продукты из таблицы
            async with db.execute("SELECT * FROM products") as cursor:
                result = await cursor.fetchall()
                # Возвращаем только 1-й и 2-й элемент из каждой строки
                filtered_result = [(row[0], row[1]) for row in result]
                return filtered_result
    except Exception as e:
        logging.error(f"Ошибка при добавлении продукта: {e}")


#-----------------------------------------------------------------------------------------------------------------------Проверяем последнюю цену товара
async def check_price_product(product_id):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            # Получаем все продукты из таблицы
            async with db.execute("SELECT * FROM product_price_history WHERE product_id = ? and product_data_retrieval_time=(SELECT MAX(product_data_retrieval_time) from product_price_history WHERE product_id = ?)",
                                  (product_id,product_id,)) as cursor:

                result = await cursor.fetchone()

                return result
    except Exception as e:
        logging.error(f"Ошибка при добавлении продукта: {e}")


#-----------------------------------------------------------------------------------------------------------------------Записываем новую цену
async def add_new_price_product(product_id,product_availability_status, product_data_retrieval_time, product_price):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            # Записываем новую цену
            await db.execute(""
                             "INSERT INTO product_price_history ("
                             "product_id,"
                             "product_availability_status,"
                             "product_data_retrieval_time,"
                             "product_price"
                             ") VALUES (?, ?, ?, ?)", (
                                 product_id,
                                 product_availability_status,
                                 product_data_retrieval_time,
                                 product_price,
                             ))
            # Устанавливаем статус для товара
            await db.execute(""
                             "UPDATE products SET status=0 WHERE id = ?",(product_id,))

            await db.commit()
    except Exception as e:
        logging.error(f"Ошибка при добавлении продукта: {e}")