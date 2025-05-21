import aiosqlite
import logging
import time

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
            # Создание таблицы user_products, если она еще не существует
            await db.execute(""
                             "CREATE TABLE IF NOT EXISTS user_products ("
                             "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                             "user_id INTEGER,"
                             "product_id INTEGER)"
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
    status: int,
    user_id: int
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


            async with db.execute("SELECT * FROM products WHERE product_url = ?", (product_url,)) as cursor:
                result = await cursor.fetchone()
                product_id = result[0]

                async with db.execute("SELECT * FROM user_products WHERE user_id = ? AND product_id = ?",
                                          (user_id, product_id,)) as cursor:
                    result = await cursor.fetchone()
                    if result is None:
                        # И если не существует, добавляем товар к пользователю
                        await db.execute(""
                                         "INSERT INTO user_products ("
                                         "user_id,"
                                         "product_id"
                                         ") VALUES (?, ?)", (
                                             user_id,
                                             product_id,
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
        logging.error(f"Ошибка при извлечении цены товара: {e}")


#-----------------------------------------------------------------------------------------------------------------------Возвращаем последние 2 записи
async def check_last_two_price_times(product_id):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            # Получаем два последних времени извлечения данных для указанного продукта
            async with db.execute("SELECT product_price FROM product_price_history WHERE product_id = ?"
                                  "ORDER BY product_data_retrieval_time DESC LIMIT 2", (product_id,)) as cursor:

                result = await cursor.fetchall()

                if result:
                    if len(result) == 1:
                        # Если найдена только одна запись, возвращаем список с двумя одинаковыми значениями
                        last_price = result[0][0]
                        return [last_price, last_price]
                    else:
                        # Если найдено больше одной записи, возвращаем реальные последние два значения
                        last_two_price = [row[0] for row in result]
                        return last_two_price
                else:
                    logging.warning(f"Не найдены записи для продукта с ID: {product_id}")
                    return None  # Возвращаем None, если записи не найдены

    except Exception as e:
        logging.error(f"Ошибка при проверке времени извлечения цены продукта: {e}")
        return None  # Возвращаем None в случае возникновения ошибки





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
                             "UPDATE products SET status=1 WHERE id = ?",(product_id,))

            await db.commit()
    except Exception as e:
        logging.error(f"Ошибка при добавлении продукта: {e}")




#-----------------------------------------------------------------------------------------------------------------------Добавляем нового пользователя
# Добавление пользователя в базу данных
async def add_user_db(user_id, first_name, last_name, username):
    created_at = int(time.time())
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            # Проверка, существует ли пользователь в базе данных
            async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
                result = await cursor.fetchone()
                if result is not None:
                    # Если пользователь существует, можно обновить его данные
                    await db.execute("UPDATE users SET first_name = ?, last_name = ?, username = ?, user_added = ? WHERE user_id = ? ", (first_name, last_name, username, 1, user_id))
                    logging.info(f"Пользователь с ID {user_id} обновлен в базе данных.")
                else:
                    # Если не существует, добавляем нового пользователя
                    await db.execute("INSERT INTO users (user_id, first_name, last_name, username, user_added, user_blocked, created_at, type_of_notification, notification_frequency ) VALUES (?, ?, ?, ?, ?, ?, ?, ?,?)", (user_id, first_name, last_name, username, 1, 0, created_at,'full','never'))
                    logging.info(f"Пользователь с ID {user_id} добавлен в базу данных.")
                await db.commit()
    except aiosqlite.Error as e:
        logging.error(f"Ошибка при добавлении пользователя в базу данных: {e}")
    except Exception as e:
        logging.error(f"Произошла неожиданная ошибка: {e}")


#-----------------------------------------------------------------------------------------------------------------------Извлекаем список товаров для рассылки
async def get_list_product_for_rassilka(status):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            # Получаем все продукты из таблицы которые надо разослать
            async with db.execute("SELECT * FROM products WHERE status =?", (status,)) as cursor:
                result = await cursor.fetchall()
                return result
    except Exception as e:
        logging.error(f"Ошибка при добавлении продукта: {e}")

#-----------------------------------------------------------------------------------------------------------------------Извлекаем список пользователей для рассылки
async def get_list_users_for_rassilka(product_id):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            # Получаем все продукты из таблицы которые надо разослать
            async with db.execute("SELECT * FROM user_products WHERE product_id =?", (product_id,)) as cursor:
                result = await cursor.fetchall()
                return result
    except Exception as e:
        logging.error(f"Ошибка при добавлении продукта: {e}")


#-----------------------------------------------------------------------------------------------------------------------Извлекаем список пользователей для рассылки
async def change_status_product(status, product_id):
    try:
        async with aiosqlite.connect(DATABASE_NAME) as db:
            # Получаем все продукты из таблицы которые надо разослать
            await db.execute(
                "UPDATE products SET status = ? WHERE id = ? ",
                (status, product_id))

            await db.commit()


    except Exception as e:
        logging.error(f"Ошибка при обновлении статуса: {e}")