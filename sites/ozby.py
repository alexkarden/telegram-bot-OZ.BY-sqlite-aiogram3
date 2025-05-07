from bs4 import BeautifulSoup
import logging
import re



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







def get_info_from_item_ozby(html_code):
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
    # if product_title:
    #     print(f"Заголовок: {product_title}")
    # if product_image_url:
    #     print(f"URL изображения: {product_image_url}")
    # if product_url:
    #     print(f"URL товара: {product_url}")
    #
    # if product_availability_status == 'В наличии' or 'Предзаказ':
    #     print(f"Статус товара: {product_availability_status}")
    #     if product_price:
    #         print(f"Основная цена: {product_price}")
    # else:
    #     print(f"Статус товара: {product_availability_status}")

    result = [
        product_title,
        product_url,
        product_image_url,
        product_price,
        product_availability_status
    ]

    return result


