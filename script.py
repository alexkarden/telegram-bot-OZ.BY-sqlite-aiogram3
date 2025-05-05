import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging


site = 'oz.by'
url='https://oz.by/books/more10818420.html?lfklgdhfgghjfg'


def is_link_belongs_to_site(url, site):
    # Разбираем URL с помощью urlparse
    parsed_url = urlparse(url)
    # Получаем сетевое имя из разобранного URL
    hostname = parsed_url.hostname
    # Сравниваем с заданным сайтом
    return hostname == site











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



def get_info_from_item(html_code):
    soup = BeautifulSoup(html_code, 'html.parser')
    # Извлечение заголовка
    title = soup.find('h1', itemprop='name')
    if title:
        title_text = title.text
    else:
        title_text = None
        logging.warning("Заголовок отсутствует.")

    # Извлечение URL изображения
    image_meta = soup.find('meta', property='og:image')
    if image_meta and 'content' in image_meta.attrs:
        image_url = image_meta['content']
    else:
        image_url = None
        logging.warning("URL изображения отсутствует.")

    # Извлечение основной цены
    main_price_span = soup.find('span', class_='b-product-control__text_main')
    if main_price_span and main_price_span.contents:
        main_price = main_price_span.contents[0].strip()
    else:
        main_price = None
        logging.warning("Основная цена отсутствует.")

    # Извлечение информации о наличии товара
    availability_info = soup.find('span', class_='b-product-control__text_info')
    if availability_info:
        availability_text = availability_info.text.strip()
    else:
        availability_text = None
        logging.warning("Информация о наличии товара отсутствует.")

    # Извлечение дополнительной информации о наличии товара
    availability_info2 = soup.find('div', class_='b-product-control__sub b-product-control__sub_mover')
    if availability_info2:
        availability_text2 = availability_info2.find('span', class_='b-product-control__text').text.strip()
    else:
        availability_text2 = None
        logging.warning("Дополнительная информация о наличии товара отсутствует.")






    # Вывод результатов
    if title_text:
        print(f"Заголовок: {title_text}")
    if image_url:
        print(f"URL изображения: {image_url}")
    if main_price:
        print(f"Основная цена: {main_price}")
        # Вывод результатов
    if availability_text:
        print(f"Статус товара: {availability_text}")
    # Вывод результатов
    if availability_text2:
        print(f"Статус товара: {availability_text2}")





if is_link_belongs_to_site(url, site):
    print(f"Ссылка'{url}' принадлежит сайту '{site}'.")
else:
    print(f"Ссылка '{url}' не принадлежит сайту '{site}'.")

get_info_from_item(get_item_from_url(url))













