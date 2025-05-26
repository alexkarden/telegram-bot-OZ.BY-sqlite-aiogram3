from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

from database import get_user_list_product

#-----------------------------------------------------------------------------------------------------------------------клавиатура на старте
start_keyboard_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Мои товары", callback_data='Мои товары')],
    [InlineKeyboardButton(text="Помощь", callback_data='Помощь'),InlineKeyboardButton(text="⚙️ Настройки", callback_data='Настройки')]
    ])

#-----------------------------------------------------------------------------------------------------------------------клавиатура списка товаров
async def user_list_products_keyboard(user_id):
    keyboard = []
    try:
        products = await get_user_list_product(user_id)

        # Проверка на получение продуктов
        if not products:
            return InlineKeyboardMarkup(inline_keyboard=[])  # Возвращаем пустую клавиатуру, если нет продуктов

        for product in products:
            title = product[2]
            product_id = "id_"+str(product[0])  # Преобразуем product_id в строку
            #print(product_id)
            button = InlineKeyboardButton(text=title, callback_data=product_id)
            keyboard.append([button])  # Каждая кнопка в отдельной строке

    except Exception as e:
        print(f"An error occurred: {e}")  # Логирование ошибки
        return InlineKeyboardMarkup(inline_keyboard=[])  # Возвращаем пустую клавиатуру при ошибке

    # Возвращаем созданную клавиатуру
    return InlineKeyboardMarkup(inline_keyboard=keyboard)



#-----------------------------------------------------------------------------------------------------------------------клавиатура удаления товаров
async def user_info_product(product_id):
    user_delete_product_key = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Мои товары", callback_data='Мои товары'),InlineKeyboardButton(text="Удалить товар", callback_data=f"delete_{product_id}")]])
    return user_delete_product_key



