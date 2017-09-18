# -*- coding: utf-8 -*-

import datetime
import json
import random
import re
import requests
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from shadow.items import MovieItem

from fake_useragent import UserAgent
from pybloom import BloomFilter


class DoubanSpider(CrawlSpider):
    name = 'douban'
    user_agent = UserAgent().random
    allowed_domains = [
        'movie.douban.com',
    ]
    start_urls = ['https://movie.douban.com']
    seed = BloomFilter(capacity=10*1024*1024, error_rate=0.001)
    rules = (
        Rule(LinkExtractor(allow=(r'https://movie.douban.com/chart.*'))),
        Rule(LinkExtractor(allow=(r'https://movie.douban.com/top250'))),
        Rule(LinkExtractor(allow=(r'https://movie.douban.com/explore.*'))),
        Rule(LinkExtractor(allow=(r'https://movie.douban.com/review/.*/'))),
        Rule(LinkExtractor(allow=(r'https://movie.douban.com/note/\d+/'))),
        Rule(LinkExtractor(allow=(r'https://movie.douban.com/subject/\d+/[^cinema.*]')), callback='parse_item'),
    )

    def extract_info(self, response, xpath):
        data = response.xpath(xpath).extract()
        if not data:
            return ''
        data = data[0].strip()
        return data

    def get_id(self, item, url):
        id = re.match('.*/subject/(.*)/', url).group(1)
        if id:
            item['id'] = id

    def get_name(self, item, response):
        xpath = '//title/text()'
        data = self.extract_info(response, xpath)
        if data:
            item['name'] = data.replace('(豆瓣)', '')

    def get_img_url(self, item, response):
        xpath = '//div[@id="mainpic"]/a/img/@src'
        data = self.extract_info(response, xpath)
        if data:
            item['img_url'] = data
        else:
            xpath = '//div[@class="subject-img"]/a/img/@src'
            data = self.extract_info(response, xpath)
            if data:
                item['img_url'] = data

    def get_run_time(self, item, response):
        xpath = '//div[@id="info"]/span[@property="v:runtime"]/text()'
        data = self.extract_info(response, xpath)
        if data:
            item['run_time'] = data

    def parse_item(self, response):
        url = response.url
        try:
            movie = MovieItem()
            self.get_name(movie, response)
            self.get_img_url(movie, response)
            self.get_run_time(movie, response)
            self.get_id(movie, url)
            movie['url'] = url
            movie['add_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            yield movie
        except Exception as e:
            print('err === ', e)
            pass
