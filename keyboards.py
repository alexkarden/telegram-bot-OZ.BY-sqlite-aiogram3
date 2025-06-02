from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.enums import ParseMode



from database import get_user_list_product, check_price_product

#-----------------------------------------------------------------------------------------------------------------------клавиатура на старте
start_keyboard_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🛍 Мои товары", callback_data='Мои товары')],
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


            price = await check_price_product(product[0])
            product_id = "id_"+str(product[0])  # Преобразуем product_id в строку
            #print(product_id)
            if price[3] == None:
                circle = f" 🔴 "
            else:
                circle = f" 🟢 "
            text_keyboard = f"{price[3]} - {product[5]}{circle}{title}"
            button = InlineKeyboardButton(text=text_keyboard, callback_data=product_id)
            keyboard.append([button])  # Каждая кнопка в отдельной строке

    except Exception as e:
        print(f"An error occurred: {e}")  # Логирование ошибки
        return InlineKeyboardMarkup(inline_keyboard=[])  # Возвращаем пустую клавиатуру при ошибке

    keyboard.append([InlineKeyboardButton(text="☑️ Главное меню", callback_data="Главное меню")])
    # Возвращаем созданную клавиатуру
    return InlineKeyboardMarkup(inline_keyboard=keyboard)



#-----------------------------------------------------------------------------------------------------------------------клавиатура удаления товаров
async def user_info_product(product_id):
    user_delete_product_key = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛍 Мои товары", callback_data='Мои товары'),InlineKeyboardButton(text="Удалить товар", callback_data=f"delete_{product_id}")],[InlineKeyboardButton(text="☑️ Главное меню", callback_data='Главное меню')]])
    return user_delete_product_key


#-----------------------------------------------------------------------------------------------------------------------клавиатура подтверждения удаления товаров
async def product_delete_yes(product_id):
    user_delete_product_key = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Нет", callback_data='Мои товары'),InlineKeyboardButton(text="Да", callback_data=f"deleteyes_{product_id}")],[InlineKeyboardButton(text="☑️ Главное меню", callback_data='Главное меню')]])
    return user_delete_product_key
