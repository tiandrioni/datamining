import requests
import bs4
from urllib.parse import urljoin
import pandas as pd


class JobParser:

    headers = {"User-Agent": "R2-D2"}

    def __init__(self, start_url, vacancy, data_list, num_pages=2):
        self.start_url = start_url
        self.vacancy = vacancy
        self.data_list = data_list   # список, в который будет вестись запись результатов поиска
        self.num_pages = num_pages
        self.check_hh_ru = start_url.startswith('https://hh.ru')

    def _params_response(self, page):
        if self.check_hh_ru:   # поиск на hh.ru
            return {'st': 'searchVacancy',
                    'text': self.vacancy,
                    'area': 113,  # поиск по всей России (1 - Москва, 2 - Питер)
                    'page': page}    # в запросе нумерация страниц начинается с 0
        else:
            return {'keywords': self.vacancy,
                    'page': page + 1}  # в запросе нумерация страниц начинается с 1

    def _get_response(self, url, page):
        return requests.get(url, params=self._params_response(page), headers=self.headers)

    def _get_soup(self, url, page):
        response = self._get_response(url, page)
        return bs4.BeautifulSoup(response.text, "lxml")

    @property
    def find_params(self):
        if self.check_hh_ru:   # поиск на hh.ru
            return {'vacancies':    {'find_tag': 'div',
                                     'find_attr_type': 'class',
                                     'find_attr_value': 'vacancy-serp-item'},
                    'vacancy_name': {'find_tag': 'a',
                                     'find_attr_type': 'data-qa',
                                     'find_attr_value': 'vacancy-serp__vacancy-title'},
                    'salary':       {'find_tag': 'span',
                                     'find_attr_type': 'data-qa',
                                     'find_attr_value': 'vacancy-serp__vacancy-compensation'},
                    'vacancy_url':  {'find_tag': 'a',
                                     'find_attr_type': 'data-qa',
                                     'find_attr_value': 'vacancy-serp__vacancy-title'},
                    'company_location': {'find_tag': 'span',
                                         'find_attr_type': 'data-qa',
                                         'find_attr_value': 'vacancy-serp__vacancy-address'},
                    'company_name': {'find_tag': 'a',
                                     'find_attr_type': 'data-qa',
                                     'find_attr_value': 'vacancy-serp__vacancy-employer'},
                    }
        else:
            return {'vacancies':    {'find_tag': 'div',
                                     'find_attr_type': 'class',
                                     'find_attr_value': 'f-test-vacancy-item'},
                    'vacancy_name': {'find_tag': 'a',
                                     'find_attr_type': 'class',
                                     'find_attr_value': 'icMQ_'},
                    'salary':       {'find_tag': 'span',
                                     'find_attr_type': 'class',
                                     'find_attr_value': 'f-test-text-company-item-salary'},
                    'vacancy_url':  {'find_tag': 'a',
                                     'find_attr_type': 'class',
                                     'find_attr_value': 'icMQ_'},
                    'company_location': {'find_tag': 'span',
                                         'find_attr_type': 'class',
                                         'find_attr_value': 'f-test-text-company-item-location'},
                    'company_name': {'find_tag': 'span',
                                     'find_attr_type': 'class',
                                     'find_attr_value': 'f-test-text-vacancy-item-company-name'},
                    }

    def _find_func(self, vacancy, property_name):
        dict_property = self.find_params[property_name]
        return vacancy.find(dict_property['find_tag'],
                            attrs={dict_property['find_attr_type']: dict_property['find_attr_value']})

    def _get_url(self, url):
        if self.check_hh_ru:
            return url
        else:
            return urljoin(self.start_url, url)

    def _get_location(self, text):
        if self.check_hh_ru:
            return text
        else:
            return text.split(' • ')[1]

    def _min_max_salary(self, salary_str):
        if self.check_hh_ru:
            salary_max = None
            salary_negotiable = False
            salary_min = None
            try:
                salary_list = salary_str.split(' ')
                salary_dimension = salary_list[-1]
                if salary_list[0] == 'от':
                    salary_min = ''.join(salary_list[1].split('\u202f'))
                elif salary_list[0] == 'до':
                    salary_max = ''.join(salary_list[1].split('\u202f'))
                elif salary_list[1] == '–':
                    salary_min = ''.join(salary_list[0].split('\u202f'))
                    salary_max = ''.join(salary_list[2].split('\u202f'))
                else:
                    salary_min = ''.join(salary_list[0].split('\u202f'))
                    salary_max = salary_min
            except AttributeError:
                salary_dimension = None
            finally:
                return {'salary_min': salary_min,
                        'salary_max': salary_max,
                        'salary_negotiable': salary_negotiable,
                        'salary_dimension': salary_dimension}
        else:
            salary_list = salary_str.split('\xa0')
            salary_max = None
            salary_negotiable = False
            salary_min = None
            salary_dimension = salary_list[-1]
            if salary_str == 'По договорённости':
                salary_negotiable = True
                salary_dimension = None
            elif salary_list[0] == 'от':
                salary_min = salary_list[1] + salary_list[2]
            elif salary_list[0] == 'до':
                salary_max = salary_list[1] + salary_list[2]
            elif salary_list[2] == '—':
                salary_min = salary_list[0] + salary_list[1]
                salary_max = salary_list[3] + salary_list[4]
            else:
                salary_min = salary_list[0] + salary_list[1]
                salary_max = salary_min

            return {'salary_min': salary_min,
                    'salary_max': salary_max,
                    'salary_negotiable': salary_negotiable,
                    'salary_dimension': salary_dimension}

    def run(self):
        for page in range(self.num_pages):
            soup = self._get_soup(self.start_url, page)
            dict_property = self.find_params['vacancies']
            vacancies = soup.find_all(dict_property['find_tag'],
                                      attrs={dict_property['find_attr_type']: dict_property['find_attr_value']})
            for vacancy in vacancies:
                vacancy_name = self._find_func(vacancy, 'vacancy_name').text
                try:
                    salary = self._find_func(vacancy, 'salary').text
                except AttributeError:
                    salary = None
                try:
                    company_name = self._find_func(vacancy, 'company_name').text
                except AttributeError:
                    company_name = None
                vacancy_url = self._get_url(self._find_func(vacancy, 'vacancy_url')['href'])
                company_location = self._get_location(self._find_func(vacancy, 'company_location').text)
                data = {'vacancy_name': vacancy_name,
                        'company_name': company_name,
                        'company_location': company_location,
                        'vacancy_url': vacancy_url,
                        **self._min_max_salary(salary)}
                self.data_list.append(data)


if __name__ == '__main__':
    data_list = []
    url_1 = 'https://hh.ru/search/vacancy'
    parser_1 = JobParser(url_1, 'грузчик', data_list)
    parser_1.run()
    url_2 = 'https://russia.superjob.ru/vacancy/search/'
    parser_2 = JobParser(url_2, 'грузчик', data_list)
    parser_2.run()
    df = pd.DataFrame(data_list, columns=['vacancy_name', 'company_name', 'company_location', 'vacancy_url',
                                          'salary_min', 'salary_max', 'salary_negotiable', 'salary_dimension'])
    print(df.head())