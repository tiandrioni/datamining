import requests
from datetime import datetime, timedelta
from lxml import html

yandex_link = 'https://yandex.ru/news'
mail_ru_link = 'https://news.mail.ru'
lenta_ru_link = 'https://lenta.ru'


class NewsParser:

    headers = {"User-Agent": "R2-D2"}

    def __init__(self, start_url):
        self.start_url = start_url
        self.check_lenta_ru = start_url == lenta_ru_link

    def _get_response(self, url):
        return requests.get(url, headers=self.headers)

    def _get_html_element(self, url):
        response = self._get_response(url)
        return html.fromstring(response.text)

    def _get_urls(self):
        elements = self._get_html_element(self.start_url)
        find_list = ['//li[@class="list__item"]/a/@href',           # mail.ru
                     '//li[@class="list__item"]/span/a/@href',
                     '//div[@class="daynews__item"]/a/@href',
                     '//td[@class="daynews__main"]/div/a/@href',
                     '//a[@class="newsitem__title link-holder"]/@href',
                     '//div[@class="item"]/a/@href'                 # lenta.ru
                     ]
        urls = elements.xpath(' | '.join(find_list))
        urls_new = []
        for url in urls:
            if self.check_lenta_ru:
                if not url.startswith('https') and not url.startswith('/extlink'):
                    urls_new.append(self.start_url + url)
            else:
                urls_new.append(url)
        return urls_new

    def _get_news_data(self, url):
        elements = self._get_html_element(url)
        return elements

    def run_gen(self):
        for url in self._get_urls():
            elements = self._get_news_data(url)
            source_find_list = ['//a[@class="link color_gray breadcrumbs__link"]/span']
            if self.check_lenta_ru:
                source = 'lenta.ru'
            else:
                source = elements.xpath(' | '.join(source_find_list))[0].text

            header_find_list = ['//h1', '//h1[@class="mg-story__title"]/a']
            header = elements.xpath(' | '.join(header_find_list))[0].text

            date_find_list = ['//span[@class="note__text breadcrumbs__text js-ago"]/@datetime',
                              '//time[@class="g-date"]/@datetime']
            date_of_publication = datetime.strptime(elements.xpath(' | '.join(date_find_list))[0],
                                                    '%Y-%m-%dT%H:%M:%S%z')

            yield {'source': source,
                   'header': header,
                   'url': url,
                   'date_of_publication': date_of_publication.strftime('%Y-%m-%d')}


class YandexNews(NewsParser):

    def run_gen(self):
        elements = self._get_html_element(self.start_url)
        news_elements = elements.xpath('//article')
        for new_element in news_elements:
            source = new_element.xpath('.//a[@class="mg-card__source-link"]')[0].text
            header = new_element.xpath('.//a[@class="mg-card__link"]/h2')[0].text
            url = new_element.xpath('.//a[@class="mg-card__link"]/@href')
            date_of_publication = datetime.now()
            if new_element.xpath('.//span[@class="mg-card-source__time"]')[0].text.startswith('вчера'):
                date_of_publication = datetime.now() - timedelta(days=1)
            yield {
                    'source': source,
                    'header': header,
                    'url': url,
                    'date_of_publication': date_of_publication.strftime('%Y-%m-%d')
                  }


def add_news_to_list(data_list, parser_news):
    for data in parser_news.run_gen():
        data_list.append(data)


if __name__ == '__main__':
    news_list = []

    parser = YandexNews(yandex_link)
    add_news_to_list(news_list, parser)

    parser = NewsParser(mail_ru_link)
    add_news_to_list(news_list, parser)

    parser = NewsParser(lenta_ru_link)
    add_news_to_list(news_list, parser)

    # Последние новости
    for news in news_list:
        print(news)
