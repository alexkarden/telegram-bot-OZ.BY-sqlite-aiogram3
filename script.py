import requests
import asyncio
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging
import re
from database import add_product



# 1. product_title — для заголовка товара
#    (явно указывает, что переменная — заголовок именно продукта)
#
# 2. product_url — для URL товара
#    (ссылка на страницу продукта)
#
# 3. product_image_url — для URL изображения товара
#    (ссылка именно на изображение продукта)
#
# 4. product_price — для цены товара
#    (стоимость продукта)
#
# 5. product_availability_status — для статуса наличия товара
#    (отражает наличие или отсутствие продукта)
#
# 6. product_data_retrieval_time — время получения  данных о продукте










url='https://hobbygames.by/amerikanskij-vertolet-apach-an-64'





















#-----------------------------------------------------------------------------------------------------------------------выбор сайтов
def is_link_belongs_to_site(url):
    # Разбираем URL с помощью urlparse
    parsed_url = urlparse(url)
    # Получаем сетевое имя из разобранного URL
    hostname = parsed_url.hostname
    if hostname == 'oz.by':
        get_info_from_item_oz(get_item_from_url(url))
    elif hostname == 'hobbygames.by':
        get_info_from_item_hobbygames(get_item_from_url(url))
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


#-----------------------------------------------------------------------------------------------------------------------oz.by
def get_info_from_item_oz(html_code):
    soup = BeautifulSoup(html_code, 'html.parser')
    # Извлечение заголовка
    title = soup.find('h1', itemprop='name')
    if title:
        product_title = title.text
    else:
        product_title = None
        logging.warning("Заголовок отсутствует.")

    # Извлечение URL товара
    url_meta = soup.find('meta', property='og:url')
    if url_meta and 'content' in url_meta.attrs:
        product_url = url_meta['content']
    else:
        product_url = None
        logging.warning("URL товара отсутствует.")

    # Извлечение URL изображения
    image_meta = soup.find('meta', property='og:image')
    if image_meta and 'content' in image_meta.attrs:
        product_image_url = image_meta['content']
    else:
        product_image_url = None
        logging.warning("URL изображения отсутствует.")

    # Извлечение основной цены

    main_price_span = soup.find('span', class_='b-product-control__text_main')
    if main_price_span:
        # Получаем весь текст внутри span, включая дочерние, но удаляем теги, оставляя только текст
        full_text = main_price_span.get_text(separator=' ', strip=True)
        # Теперь используем регулярное выражение для извлечения числа с запятой перед 'р.' или просто числа
        price_pattern = r'(\d+,\d+)\s*р\.?'
        price_match = re.search(price_pattern, full_text)
        if price_match:
            price_text = price_match.group(1).replace(',', '.')  # Заменяем запятую на точку
            try:
                product_price = float(price_text)

            except ValueError:
                print("Ошибка при преобразовании цены в число.")
        else:
            product_price = None

    else:
        product_price = None




    # Извлечение информации о наличии товара
    availability_info1 = soup.find('span', class_='b-product-control__text_info')
    availability_info2 = soup.find('div', class_='b-product-control__sub b-product-control__sub_mover')
    if availability_info1:
        product_availability_status = "Нет в наличии"
    elif availability_info2:
        product_availability_status = "В наличии"
    else:
        product_availability_status = None
        logging.warning("Информация о наличии товара отсутствует.")



    # Вывод результатов
    if product_title:
        print(f"Заголовок: {product_title}")
    if product_image_url:
        print(f"URL изображения: {product_image_url}")
    if product_url:
        print(f"URL товара: {product_url}")

    if product_availability_status == 'В наличии' or 'Предзаказ':
        print(f"Статус товара: {product_availability_status}")
        if product_price:
            print(f"Основная цена: {product_price}")
    else:
        print(f"Статус товара: {product_availability_status}")
    asyncio.run(
        add_product(22, product_url, product_title, product_image_url, product_price, product_availability_status, 1))


#-----------------------------------------------------------------------------------------------------------------------hobbygames.by
def get_info_from_item_hobbygames(html_code):
    soup = BeautifulSoup(html_code, 'html.parser')
    # Извлечение заголовка
    title = soup.find('h1')
    if title:
        product_title = title.text.strip()
    else:
        product_title = None
        logging.warning("Заголовок отсутствует.")

    # Извлечение URL товара
    link_tag = soup.find('link', rel='canonical')
    if link_tag:
        product_url = link_tag.get('href')

    else:
        product_url = None
        logging.warning("URL товара отсутствует.")

    # Извлечение URL изображения
    image_meta = soup.find('meta', property='og:image')
    if image_meta and 'content' in image_meta.attrs:
        product_image_url = image_meta['content']
    else:
        product_image_url = None
        logging.warning("URL изображения отсутствует.")

    # Извлечение основной цены
    price_div = soup.find('div', class_='product-card-price__current')
    if price_div:
        # Получаем текст, удаляем ненужные символы и пробелы
        price_text = price_div.get_text(strip=True)
        # Удаляем символы, отличные от цифр и точки

        match = re.search(r'([\d.,]+)', price_text)
        if match:
            price_str = match.group(1).replace(',', '.')  # заменяем запятые на точки, если есть
            # Преобразуем строку в число типа float (real)
            product_price = float(price_str)
        else:
            product_price = None
    else:
        product_price = None




    # Извлечение информации о наличии товара
    availability_info1 = soup.find('body', class_='product-info product-info_by not-available')
    availability_info2 = soup.find('body', class_='product-info product-info_by')
    availability_info3 = soup.find('body', class_='product-info product-info_by preorder')
    if availability_info1:
        product_availability_status = "Нет в наличии"
    elif availability_info2:
        product_availability_status = "В наличии"
    elif availability_info3:
        product_availability_status = "Предзаказ"
    else:
        product_availability_status = None
        logging.warning("Информация о наличии отсутствует")




    # Вывод результатов
    if product_title:
        print(f"Заголовок: {product_title}")
    if product_image_url:
        print(f"URL изображения: {product_image_url}")
    if product_url:
        print(f"URL товара: {product_url}")
    if product_availability_status == 'В наличии' or product_availability_status == 'Предзаказ':
        print(f"Статус товара: {product_availability_status}")
        if product_price:
            print(f"Цена: {product_price}")
    else:
        print(f"Статус товара: {product_availability_status}")

    asyncio.run(
        add_product(22, product_url, product_title, product_image_url, product_price, product_availability_status, 1))

    asyncio.run(
        add_product(42, product_url, product_title, product_image_url, product_price, product_availability_status, 1))















is_link_belongs_to_site(url)










