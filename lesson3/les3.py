from pymongo import MongoClient
from lesson2.hh_superjob_parser import JobParser


def check_vacancy_to_db(new_vacancy, db):
    """
    :param new_vacancy: вакансия, которую нужно проверить на наличие в БД (db)
    :param db: ДБ, в которой нужно найти вакансию (new_vacancy)
    :return: True - если вакансия есть в БД, False - если нет
    """
    return len(list(db.vacancies.find( {'vacancy_url': new_vacancy['vacancy_url']} ))) != 0


def save_to_db(db, data):
    try:
        if isinstance(data, list):
            for vacancy in data:
                if not check_vacancy_to_db(vacancy, db):
                    db.vacancies.insert_one(vacancy)
                    print('Добавлена новая вакансия')
        else:
            if not check_vacancy_to_db(data, db):
                db.vacancies.insert_one(data)
                print('Добавлена новая вакансия')
    except TypeError:
        print('Неверный формат данных')


def print_search_salary(salary_min, db):
    """
    :param salary_min: сумма заработной платы, выше которой нужно искать з/п по вакансиям
    :param db: база данных, по которой производится поиск
    :return: None
    """
    for itm in db.vacancies.find( {'$or': [{'salary_min': {'$gt': str(salary_min)}},
                                           {'salary_max': {'$gt': str(salary_min)}}]} ):
        print(itm)


def run():
    client = MongoClient('localhost', 27017)
    db = client['vacancies_db']

    # Вакансии с hh
    data_list = []
    url = 'https://hh.ru/search/vacancy'
    parser = JobParser(url, 'грузчик', data_list, num_pages=5)
    parser.run()
    save_to_db(db, data_list)

    # Вакансии с superjob
    data_list_sj = []
    url_sj = 'https://russia.superjob.ru/vacancy/search/'
    parser_sj = JobParser(url_sj, 'грузчик', data_list_sj, num_pages=5)
    parser_sj.run()
    save_to_db(db, data_list_sj)

    print('Вакансии, для которых з/п выше 70000 руб.')
    print_search_salary(70000, db)


run()
