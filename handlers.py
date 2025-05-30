import logging
import time

from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext


from script import is_link_belongs_to_site
from database import add_new_product, add_user_db, get_product_from_id, check_price_product, delete_product_from_user
from keyboards import start_keyboard_inline, user_list_products_keyboard, user_info_product, product_delete_yes







router = Router()



@router.message(CommandStart())
async def cmd_start(message: Message):
    welcome_text = (
        f"👋 <b>Добро пожаловать, {message.from_user.first_name}!</b>\n"
        f"\n"
        f"🔅 С помощью этого бота вы сможете отследить изменение цены на понравившиеся товары в Интернет-магазинах:\n"
        f"oz.by\n"
        f"amd.by\n"
        f"oma.by\n"
        f"mila.by\n"
        f"mile.by\n"
        # f"sila.by\n"
        # f"21vek.by\n"
        f"detmir.by\n"
        f"onliner.by\n"
        f"hobbygames.by\n"
        f"znaemigraem.by\n"
        f"\n"
        f"🔅 Для начала отслеживания цены на товар отправьте боту ссылку на товар.\n")
    # Записываем пользователя в базу
    await add_user_db(message.from_user.id, message.from_user.first_name, message.from_user.last_name,
                      message.from_user.username)
    await message.answer(welcome_text, reply_markup=start_keyboard_inline, parse_mode=ParseMode.HTML)



@router.message(Command('menu'))
async def cmd_menu(message: Message):
    text = (
        f"<b>☑️ Главное меню</b>\n\n"
        f"🔅 Мои товары - <i>список отслеживаемых товаров</i>\n\n"
        f"🔅 Помощь - <i>полезная информация о боте</i>\n\n"
        f"🔅 Настройки - <i>глобальные настройки для всех отслеживаемых товаров</i>")

    await message.answer(text=text, reply_markup=start_keyboard_inline, parse_mode=ParseMode.HTML)



@router.message()
async def all_message(message: Message):
    try:
        text = message.text
        result = await is_link_belongs_to_site(text)
        # print(result)
        if result and result[0]:
            current_time = int(time.time())
            print(result)
            await add_new_product(result[1], result[0], result[2],result[3],result[4],current_time,0,message.from_user.id,result[5])


            texttg = (
                f"Товар <i><b>'{result[0]}'</b></i> добавлен и отслеживается."

            )
            await message.answer(texttg, reply_markup=start_keyboard_inline,parse_mode=ParseMode.HTML)
        else:
            await message.answer('Что-то пошло не так, например Вы прислали некоректную ссылку. Попробуйте прислать другую ссылку', parse_mode=ParseMode.HTML)
    except Exception as e:
        logging.error(f"Ошибка при обработке ссылки и записи нового товара в базу : {e}")
        await message.answer(f"Ошибка при обработке ссылки и записи нового товара в базу : {e}", parse_mode=ParseMode.HTML)





@router.callback_query()
async def callback_query(callback: CallbackQuery, state:FSMContext):
    data = callback.data
    if data == 'Мои товары':
        reply_markup_check = await user_list_products_keyboard(callback.message.chat.id)
        if str(reply_markup_check) != 'inline_keyboard=[]':
            text = f"🔅 <b>Список отслеживаемых товаров:</b>"
            reply_markup=reply_markup_check
        else:
            text = f"🔅 <b>Вы еще не добавили ни одного товара</b>"
            reply_markup = start_keyboard_inline
        await callback.message.answer( text=text, reply_markup= reply_markup, parse_mode=ParseMode.HTML)


    elif data.startswith('id_'):
        product_id = data.split('_')[1]
        product_info = await get_product_from_id(product_id)
        product_price = await check_price_product(product_id)
        photo = product_info[3]
        if product_price[3]:
            text_price = f'<b>Цена:</b> {product_price[3]} BYN\n\n'
        else:
            text_price = f''


        caption = (
            f'<b>Товар:</b> <a href="{product_info[1]}">{product_info[2]}</a>\n'
            f'<b>Статус:</b> {product_price[2]}\n\n'
            f'{text_price}'
        )
        await callback.message.answer_photo(photo=photo, caption=caption, reply_markup= await user_info_product(product_id), parse_mode=ParseMode.HTML)



    elif data.startswith('delete_'):  # Исправлено
        product_id = data.split('_')[1]
        await callback.message.answer(f"Вы действительно хотите удалить товар", reply_markup=await product_delete_yes(product_id), parse_mode=ParseMode.HTML)

    elif data.startswith('deleteyes_'):  # Исправлено
        product_id = data.split('_')[1]
        await delete_product_from_user(callback.message.chat.id,product_id)
        await callback.message.answer(f"Товар удален", reply_markup=start_keyboard_inline, parse_mode=ParseMode.HTML)

    elif data == 'Помощь':  # Исправлено
        text_help =(
        f"Помощь\n\n"
        f"С помощью этого бота вы сможете отследить изменение цены на понравившиеся товары в Интернет-магазинах:\n"
        f"oz.by\n"
        f"amd.by\n"
        f"oma.by\n"
        f"mila.by\n"
        f"mile.by\n"
        # f"21vek.by\n"
        f"detmir.by\n"
        f"onliner.by\n"
        f"hobbygames.by\n"
        f"znaemigraem.by\n"
        f"\n"
        f"🔅 Для начала отслеживания цены на товар отправьте боту ссылку на товар.\n"
        f"🔅 Если после отправки ссылки товар не добавился, то изучите саму ссылку и попробуйте удалить лишние символы в ссылке.\n"
        f"🔅 После успешного добавления товара, он начинает отслеживаться, как только измениться стоимость или статус (например статус  'Нет в наличии' сменится на 'В наличии'), Вы получите уведомление.\n"
        )
        await callback.message.answer(text_help, reply_markup=start_keyboard_inline, parse_mode=ParseMode.HTML)



    elif data == 'Главное меню':  # Исправлено
        text = (
            f"<b>☑️ Главное меню</b>\n\n"
            f"🔅 Мои товары - <i>список отслеживаемых товаров</i>\n\n"
            f"🔅 Помощь - <i>полезная информация о боте</i>\n\n"
            f"🔅 Настройки - <i>глобальные настройки для всех отслеживаемых товаров</i>")


        await callback.message.answer(text=text, reply_markup=start_keyboard_inline, parse_mode=ParseMode.HTML)