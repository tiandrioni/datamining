from selenium import webdriver
from datetime import datetime, timedelta
from pymongo import MongoClient


def authorization(driver):
    try:
        start_url = 'https://e.mail.ru/inbox/'
        driver.get(start_url)
        username = 'vstavte_text'
        password = 'psJc0Ib%leS3b5i6KYuP'
        # ввод имени пользователя
        username_element = driver.find_element_by_class_name('input-0-2-51')
        username_element.send_keys(username)
        button = driver.find_element_by_class_name('inner-0-2-63')
        button.click()
        # ввод пароля
        password_element = driver.find_elements_by_class_name('input-0-2-51')[1]
        password_element.send_keys(password)
        button = driver.find_element_by_class_name('inner-0-2-63')
        button.click()
    except:
        authorization(driver)


def get_date(date_str):
    num_month = {'января': 1, 'февраля': 2, 'марта': 3, 'апредя': 4, 'мая': 5, 'июня': 6,
                 'июля': 7, 'августа': 8, 'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12}
    first_word = date_str.split(',')[0]
    if first_word == 'Сегодня':
        return datetime.now().date().strftime('%Y-%m-%d')
    elif first_word == 'Вчера':
        result = datetime.now().date() - timedelta(days=1)
        return result.strftime('%Y-%m-%d')
    else:
        # прошлые года
        if len(first_word.split(' ')) == 3:
            day, month, year = first_word.split()
            month = num_month[month]
            day = int(day)
            year = int(year)
            return datetime(year, month, day).strftime('%Y-%m-%d')
        # текущий год
        if len(first_word.split(' ')) == 2:
            day, month = first_word.split()
            month = num_month[month]
            day = int(day)
            year = datetime.now().year
            return datetime(year, month, day).strftime('%Y-%m-%d')


def check_message_to_db(new_message, db):
    return len(list(db.messages.find({'sender': new_message['sender'], 'header': new_message['header'],
                                      'date': new_message['date'], 'message': new_message['message']}))) != 0


def save_to_db(data, db):
    try:
        if isinstance(data, list):
            for message in data:
                if not check_message_to_db(message, db):
                    db.messages.insert_one(message)
                    print('Добавлено новое письмо в БД')
        else:
            if not check_message_to_db(data, db):
                db.messages.insert_one(data)
                print('Добавлено новое письмо в БД')
    except TypeError:
        print('Неверный формат данных')


def run():
    driver_path = r'T:\Programs\geckodriver.exe'
    driver = webdriver.Firefox(executable_path=driver_path)
    driver.implicitly_wait(10)
    authorization(driver)
    elements = driver.find_elements_by_class_name('js-tooltip-direction_letter-bottom')
    data = []
    links = [element.get_attribute('href') for element in elements]
    for link in links:
        driver.get(link)
        sender = driver.find_element_by_class_name('letter-contact').get_attribute('title')
        header = driver.find_element_by_class_name('thread__subject').text
        # дата получения
        date_str = driver.find_element_by_class_name('letter__date').text
        # текст письма
        message = driver.find_elements_by_class_name('letter-body')[0].text.strip()
        data.append({'sender': sender,
                     'header': header,
                     'date': get_date(date_str),
                     'message': message})
    for line in data:
        print(line)

    client = MongoClient('localhost', 27017)
    db = client['email_db']

    save_to_db(data, db)
    driver.close()


run()
