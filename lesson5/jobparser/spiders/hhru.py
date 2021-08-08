import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem
from urllib.parse import urljoin


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']

    def __init__(self, vacancy):
        self.start_urls = [f'https://hh.ru/search/vacancy?text={vacancy}']

    def parse(self, response: HtmlResponse):
        next_page = response.css('span.bloko-form-spacer a::attr(href)').extract_first()
        next_page = urljoin(response.url, next_page)
        yield response.follow(next_page, callback=self.parse)

        vacancy_urls = response.css('span.g-user-content a.bloko-link::attr(href)').extract()
        for url in vacancy_urls:
            yield response.follow(url, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.css('div.vacancy-title h1.bloko-header-1::text').extract_first()
        salary_str = response.css('div.vacancy-title p.vacancy-salary span::text').extract_first()
        salary_min, salary_max, salary_negotiable, salary_dimension = self._min_max_salary(salary_str)
        yield JobparserItem(name=name, salary_min=salary_min, salary_max=salary_max,
                            salary_negotiable=salary_negotiable, salary_dimension=salary_dimension,
                            url=response.url, source='hh.ru')

    def _min_max_salary(self, salary_str):
        salary_max = None
        salary_negotiable = False
        salary_min = None
        try:
            if salary_str == 'з/п не указана':
                salary_dimension = None
            else:
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
            return salary_min, salary_max, salary_negotiable, salary_dimension