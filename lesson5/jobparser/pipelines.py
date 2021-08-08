# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class JobparserPipeline(object):

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.db = client.vacancies_08_2021

    def process_item(self, item, spider):
        collection = self.db[spider.name]
        collection.insert_one(ItemAdapter(item).asdict())

        return item
