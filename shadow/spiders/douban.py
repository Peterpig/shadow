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
    re_dict = {
            r'^https://movie.douban.com/typerank': {
                'class_name': 'movie-list-item',
                'exec_js': "var q = document.documentElement.scrollTop={num};",
                'need_page_num': True,
            },
            r'^https://movie.douban.com/tag/$': {
                'class_name': 'item',
                'exec_js': "document.getElementsByClassName('more')[0].click()",
                'need_page_num': False,
            },
            r'^https://movie.douban.com/explore': {
                'class_name': 'item',
                'exec_js': "if($('.more').text() == '加载更多'){$('.more').click()}",
                'need_page_num': False,
            },
        }

    rules = (
        Rule(LinkExtractor(allow=(r'https://movie.douban.com/chart.*'))),
        Rule(LinkExtractor(allow=(r'https://movie.douban.com/top250'))),
        Rule(LinkExtractor(allow=(r'https://movie.douban.com/explore.*')), follow=True, callback='parse_url_for_tag'),
        Rule(LinkExtractor(allow=(r'httsp://movie.douban.com/tag/*')), follow=True, callback='parse_url_for_tag'),
        Rule(LinkExtractor(allow=(r'https://movie.douban.com/review/.*/')), callback='parse_url_for_review'),
        Rule(LinkExtractor(allow=(r'https://movie.douban.com/note/\d+/'))),
        Rule(LinkExtractor(allow=(r'https://movie.douban.com/typerank')), follow=True, callback='parse_url_for_rank'),
        Rule(LinkExtractor(allow=(r'https://movie.douban.com/subject/\d+/*')), follow=True, callback='parse_item'),
        Rule(LinkExtractor(allow=(r'https://movie.douban.com/celebrity/\d+/$'))),
        Rule(LinkExtractor(allow=(r'https://movie.douban.com/awards*'))),
        Rule(LinkExtractor(allow=(r'https://movie.douban.com/cinema/\w+/'))),
    )

    def extract_info(self, response, xpath):
        data = response.xpath(xpath).extract()
        if not data:
            return ''
        data = data[0].strip()
        return data
    
    def extrace_info_list(self, response, xpath):
        data = response.xpath(xpath)
        if not data:
            return ''
        return [d.extract().strip() for d in data]

    def get_id(self, item, url):
        douban_id = re.match('.*/subject/(.*)/', url).group(1)
        item['id'] = douban_id

    def get_name(self, item, response):
        xpath = '//div[@id="content"]/h1/span[1]/text()'
        data = self.extract_info(response, xpath)
        item['name'] = data.replace('(豆瓣)', '')

    def get_img_url(self, item, response):
        xpath = '//div[@id="mainpic"]/a/img/@src'
        data = self.extract_info(response, xpath)
        if data:
            item['img_url'] = data
        else:
            xpath = '//div[@class="subject-img"]/a/img/@src'
            data = self.extract_info(response, xpath)
            item['img_url'] = data

    def get_run_time(self, item, response):
        xpath = '//div[@id="info"]/span[@property="v:runtime"]/text()'
        data = self.extract_info(response, xpath)
        item['run_time'] = data

    def get_genre(self, item, response):
        xpath = '//div[@id="info"]/span[@property="v:genre"]/text()'
        data = response.xpath(xpath)
        item['genre'] = [d.extract().strip() for d in data]
    
    def get_release_date(self, item, response):
        xpath = '//div[@id="info"]/span[@property="v:initialReleaseDate"]/text()'
        data = self.extrace_info_list(response, xpath)
        item['release_date'] = data

    def parse_url_for_review(self, response):
        xpath = '//div[@class="subject-img"]/a/@href'
        url = self.extract_info(response, xpath)
        if url and url not in self.seed:
            yield scrapy.Request(url, callback=self.parse_item)

    def parse_url_for_rank(self, response):
        xpath = '//div[@class="movie-content"]/a/@href'
        urls = response.xpath(xpath).extract()
        for url in urls:
            yield scrapy.Request(url, callback=self.parse_item)

    def parse_url_for_tag(self, response):
        xpath = '//div[@class="list-wp"]//a/@href'
        urls = response.xpath(xpath).extract()
        for url in urls:
            yield scrapy.Request(url, callback=self.parse_item)

    def parse_item(self, response):
        url = response.url
        try:
            movie = MovieItem()
            self.get_name(movie, response)
            self.get_img_url(movie, response)
            self.get_run_time(movie, response)
            self.get_id(movie, url)
            self.get_genre(movie, response)
            self.get_release_date(movie, response)
            movie['url'] = url
            movie['add_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            yield movie
        except Exception as e:
            print('err === ', e)
            pass
