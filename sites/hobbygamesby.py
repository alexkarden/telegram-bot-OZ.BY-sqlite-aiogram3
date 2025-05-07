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


#-----------------------------------------------------------------------------------------------------------------------hobbygames.by
def get_info_from_item_hobbygamesby(html_code):
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




    # # Вывод результатов
    # if product_title:
    #     print(f"Заголовок: {product_title}")
    # if product_image_url:
    #     print(f"URL изображения: {product_image_url}")
    # if product_url:
    #     print(f"URL товара: {product_url}")
    # if product_availability_status == 'В наличии' or product_availability_status == 'Предзаказ':
    #     print(f"Статус товара: {product_availability_status}")
    #     if product_price:
    #         print(f"Цена: {product_price}")
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



