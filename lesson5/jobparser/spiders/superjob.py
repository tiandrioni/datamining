import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem
from urllib.parse import urljoin


class SuperjobSpider(scrapy.Spider):
    name = 'superjob'
    allowed_domains = ['superjob.ru']
    start_urls = ['http://superjob.ru/']

    def __init__(self, vacancy):
        self.start_urls = [f'https://www.superjob.ru/vacancy/search/?keywords={vacancy}']

    def parse(self, response: HtmlResponse):
        next_page = response.css('a.f-test-button-dalshe::attr(href)').extract_first()
        next_page = urljoin(response.url, next_page)
        yield response.follow(next_page, callback=self.parse)

        vacancy_urls = response.css('div._1h3Zg a.icMQ_::attr(href)').extract()
        for url in vacancy_urls:
            yield response.follow(url, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.css('div._3MVeX h1._1h3Zg::text').extract_first()
        salary_str = ''.join(response.css('span.ZON4b *::text').extract())
        salary_min, salary_max, salary_negotiable, salary_dimension = self._min_max_salary(salary_str)
        yield JobparserItem(name=name, salary_min=salary_min, salary_max=salary_max,
                            salary_negotiable=salary_negotiable, salary_dimension=salary_dimension,
                            url=response.url, source='superjob.ru')

    def _min_max_salary(self, salary_str):
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

        return salary_min, salary_max, salary_negotiable, salary_dimension
