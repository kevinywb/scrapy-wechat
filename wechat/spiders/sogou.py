# -*- coding: utf-8 -*-
import scrapy
import time
# from utils import WechatUtils
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy import Request
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from wechat.items import WechatItem


class SogouSpider(scrapy.Spider):
    name = 'sogou'
    allowed_domains = [
        'weixin.sogou.com',
        'mp.weixin.qq.com'
    ]
    start_urls = [
        'https://weixin.sogou.com/weixin?query=%E8%8A%8B%E9%81%93%E6%BA%90%E7%A0%81'
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
        # self.utils = WechatUtils()
        # number of pages to crawl
        self.page_count = 0
        # index of pages to crawl
        self.page_index = 0
        # initialize
        super(SogouSpider, self).__init__()
        dispatcher.connect(self.closeSpider, signals.spider_closed)

    def closeSpider(self, spider):
        self.browser.quit()

    def parse(self, response):
        # parse article page
        if self.page_count > 0:
            item = WechatItem()
            item['date'] = self.today
            item['title'] = response.xpath(
                'normalize-space(//h2[@class="rich_media_title"]/text())').extract()[0]
            item['content'] = response.xpath(
                '//div[@class="rich_media_content "]').extract()[0]
            item['content'] = item['content'].replace('\n', '')
            item['content'] = item['content'].replace('\xa0', '&nbsp')
            # for x in response.xpath('//div[@class="rich_media_content "]').xpath('.//p|.//figure'):
            #     # extract image
            #     img = x.xpath('img')
            #     if len(img) > 0:
            #         src = img.xpath('@data-src')
            #         if len(src) > 0:
            #             src = src.extract()[0]
            #             src += '&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1'
            #             item['content'] += '![图片暂时无法加载](%s)' % (src)
            #             item['content'] += '&#10;&#10;'

            #     # extract code
            #     code = x.xpath('code//text()')
            #     if len(code) > 0:
            #         code = code.extract()[0]
            #         item['content'] += '&#10;&#10;'
            #         item['content'] += '```%s```' % (code)
            #         item['content'] += '&#10;&#10;'

            #     # extract text
            #     text = x.xpath('string(.)')
            #     if len(text) > 0:
            #         text = text.extract()[0]
            #         if text == '':
            #             item['content'] += '&#10;&#10;'
            #         item['content'] += text

            # item['content'] += '&#10;&#10;'
            # item['content'] = item['content'].replace('\xa0', '&nbsp;')
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
