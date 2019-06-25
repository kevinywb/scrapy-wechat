# -*- coding: utf-8 -*-
import scrapy
import time
import pymongo
import html5lib
from utils import WechatUtils
from html2md import Html2Markdown
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy import Request
from scrapy import signals
from scrapy.conf import settings
from scrapy.xlib.pydispatch import dispatcher
from wechat.items import WechatItem


class SogouSpider(scrapy.Spider):
    name = 'sogou'
    allowed_domains = [
        'weixin.sogou.com',
        'mp.weixin.qq.com'
    ]
    start_urls = [
        # 'https://weixin.sogou.com/weixin?query=ImportNew'  # ImportNew
        # 'https://weixin.sogou.com/weixin?query=dotnet%E8%B7%A8%E5%B9%B3%E5%8F%B0'   # dotnet跨平台
        # 'https://weixin.sogou.com/weixin?query=%E9%98%BF%E9%87%8C%E6%8A%80%E6%9C%AF'  # 阿里技术
        # 'https://weixin.sogou.com/weixin?query=%E8%8A%8B%E9%81%93%E6%BA%90%E7%A0%81'  # 芋道源码
        'https://weixin.sogou.com/weixin?query=k8s%E4%B8%AD%E6%96%87%E7%A4%BE%E5%8C%BA'   # K8S中文社区
        # 'https://weixin.sogou.com/weixin?query=thoughtworks%E6%B4%9E%E8%A7%81'  # Thoughtworks洞见
    ]

    def __init__(self):
        # use headless mode
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument(
            'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.81 Safari/537.36')
        self.browser = webdriver.Chrome(chrome_options=chrome_options)
        # unified access to today's date
        self.today = time.strftime("%Y/%m/%d")
        # use common utils
        self.utils = WechatUtils()
        # number of pages to crawl
        self.page_count = 0
        # index of pages to crawl
        self.page_index = 0
        # connect to mongodb
        self.ocean = pymongo.MongoClient(
            host=settings['DB_MONGO_HOST'], port=settings['DB_MONGO_PORT'])['ocean']
        # initialize
        super(SogouSpider, self).__init__()
        dispatcher.connect(self.closeSpider, signals.spider_closed)

    def closeSpider(self, spider):
        self.browser.quit()
        self.ocean.quit()

    def parse(self, response):
        # parse article page
        if self.page_count > 0:
            item = WechatItem()
            item['date'] = self.today
            item['title'] = response.xpath(
                'normalize-space(//h2[@class="rich_media_title"]/text())').extract()[0]
            item['html'] = response.xpath(
                '//div[@class="rich_media_content "]').extract()[0]
            # fix incomplete tags
            html = html5lib.HTMLParser(tree=html5lib.getTreeBuilder("dom"))
            xml = html.parse(item['html']).toxml()
            # convert to markdown
            h2m = Html2Markdown()
            h2m.feed(xml)
            h2m.close()
            item['markdown'] = h2m.output
            yield item

        else:  # parse article list
            for x in response.xpath('//div[@class="weui_media_bd"]'):
                # only get today articles
                date = x.xpath(
                    'normalize-space(p[@class="weui_media_extra_info"]/text())').extract()[0]
                date = date.replace('年', '/')
                date = date.replace('月', '/')
                date = date.replace('日', '')
                if date == self.today.replace('/0', '/'):
                    self.page_count += 1

        # whether need to request the next page
        if self.page_index < self.page_count:
            yield Request(url=response.url, callback=self.parse)
