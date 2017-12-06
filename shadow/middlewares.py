# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

import re
import random
import requests
import time
import json

from scrapy import signals
from scrapy import exceptions
from scrapy.http import HtmlResponse

from fake_useragent import UserAgent
from shadow.spiders.douban import DoubanSpider
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ShadowSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RequestPorxy(object):

    def __init__(self):
        pass

    def process_request(self, request, spider):
        proxy_status = False
        while True:
            r = requests.get('http://127.0.0.1:8000/?types=0&count=20&country=国内')
            ip_ports = json.loads(r.text)
            ip_str = random.choice(ip_ports)
            ip = ip_str[0]
            port = ip_str[1]
            proxies={
                'http':'http://%s:%s' % (ip, port),
                'https':'http://%s:%s' % (ip, port),
            }
            r = requests.get('http://ip.chinaz.com/', proxies=proxies)
            if r.status_code == 200:
                request.meta["proxy"] = 'http://%s:%s' % (ip, port)
                print('use proxy ==== %s: %s' % (ip, port))
                break

class RequestMethodMiddle(object):

    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        self.driver = webdriver.Chrome(chrome_options=chrome_options)

    def process_request(self, request, spider):
        url = request.url
        if url in spider.seed:
            print('%s in seed : %s' % (url, url in spider.seed))
            raise exceptions.IgnoreRequest
        spider.seed.add(url)

        action_dict = {}
        if not spider.re_dict:
            return
        for pattern, value_dict in spider.re_dict.items():
            if re.match(pattern, url):
                action_dict = value_dict
                break

        if action_dict.get('class_name'):
            self.driver.get(url)
            wait = WebDriverWait(self.driver, 10)
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, action_dict['class_name'])))

            i = 0
            exec_js = action_dict.get('exec_js')
            while i <= 60:
                if action_dict.get('need_page_num'):
                    self.driver.execute_script(exec_js.format(num=i*10000))
                else:
                    self.driver.execute_script(exec_js)
                time.sleep(1.5)
                i += 1

            body = self.driver.page_source
            return HtmlResponse(self.driver.current_url, body=body, encoding='utf-8', request=request)
