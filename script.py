import requests
import asyncio

from urllib.parse import urlparse
import logging

from sites.ozby import get_info_from_item_ozby
from sites.hobbygamesby import get_info_from_item_hobbygamesby




url='https://hobbygames.by/spagetti-vestern-2'


#-----------------------------------------------------------------------------------------------------------------------выбор сайтов
def is_link_belongs_to_site(url):
    # Разбираем URL с помощью urlparse
    parsed_url = urlparse(url)
    # Получаем сетевое имя из разобранного URL
    hostname = parsed_url.hostname
    if hostname == 'oz.by':
        result = get_info_from_item_ozby(get_item_from_url(url))
        print(result)
    elif hostname == 'hobbygames.by':
        result = get_info_from_item_hobbygamesby(get_item_from_url(url))
        print(result)
    else:
        print('Некоректная ссылка или работа с этим сайтом не поддерживается')



#-----------------------------------------------------------------------------------------------------------------------
def get_item_from_url(url):
    try:
        response = requests.get(url)  # Используйте requests.get для простоты
        response.raise_for_status()  # Проверка для HTTP ошибок (например, 404, 500 и т.д.)
        x = response.text  # Получаем JSON ответ от сервера
        return x
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")  # Вывод ошибки для отладки
    except Exception as err:
        logging.error(f"An error occurred: {err}")  # Общая обработка исключений









is_link_belongs_to_site(url)










