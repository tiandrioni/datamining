from selenium import webdriver
from datetime import datetime
from pymongo import MongoClient
from urllib.parse import urljoin
from selenium.common.exceptions import NoSuchElementException


def check_product_to_db(product, db):
    return len(list(db.products.find({'product_name': product['product_name'], 'price': product['price'],
                                      'overview': product['overview'], 'url': product['url'],
                                      'date': product['date']}))) != 0


def save_to_db(data, db):
    try:
        if isinstance(data, list):
            for product in data:
                if not check_product_to_db(product, db):
                    db.products.insert_one(product)
                    print('Добавлена новая запись в БД')
        else:
            if not check_product_to_db(data, db):
                db.products.insert_one(data)
                print('Добавлена новая запись в БД')
    except TypeError:
        print('Неверный формат данных')


def run():
    driver_path = r'T:\Programs\geckodriver.exe'
    driver = webdriver.Firefox(executable_path=driver_path)
    driver.implicitly_wait(10)

    # Связной
    start_url = 'https://www.svyaznoy.ru'
    driver.get(start_url)
    hot_button = driver.find_element_by_class_name('b-second-line__header__link')
    hot_button.click()
    data = []
    elements = driver.find_elements_by_class_name('b-product-block__main-link')
    urls = [element.get_attribute('href') for element in elements]
    for url in urls:
        driver.get(urljoin(start_url, url))
        product_name = driver.find_element_by_class_name('b-offer-title').text
        price = driver.find_element_by_class_name('b-offer-box__price').text
        overview = driver.find_element_by_class_name('b-tech-offer__text').text
        data.append({'product_name': product_name, 'price': price,
                     'overview': overview, 'url': url,
                     'date': datetime.now().strftime('%Y-%m-%d')})

    # ОНЛАЙН ТРЕЙД
    start_url = 'https://www.onlinetrade.ru/'
    driver.get(start_url)
    container = driver.find_elements_by_id('tabs_hits')[0]
    elements = container.find_elements_by_class_name('indexGoods__item__name')
    urls = [element.get_attribute('href') for element in elements]
    for url in urls:
        driver.get(urljoin(start_url, url))
        try:
            product_name = driver.find_element_by_tag_name('h1').text
        except NoSuchElementException:
            product_name = None
        try:
            price = driver.find_element_by_class_name('js__actualPrice').text
        except NoSuchElementException:
            price = None
        try:
            overview = driver.find_element_by_class_name('descr__columnCell').text
        except NoSuchElementException:
            overview = None
        data.append({'product_name': product_name, 'price': price,
                     'overview': overview, 'url': url,
                     'date': datetime.now().strftime('%Y-%m-%d')})
    for line in data:
        print(line)

    client = MongoClient('localhost', 27017)
    db = client['tehno_db']

    save_to_db(data, db)
    driver.close()


run()
