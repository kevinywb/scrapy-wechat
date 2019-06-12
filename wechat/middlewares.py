# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import time
import uuid
from scrapy import signals
from scrapy.http import HtmlResponse
from fake_useragent import UserAgent


class WechatSpiderMiddleware(object):
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


class WechatDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        s.ua = UserAgent()
        s.ua_type = crawler.settings.get('RANDOM_UA_TYPE')
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        request.headers['User-Agent'] = getattr(self.ua, self.ua_type)
        request.cookies['SUV'] = ''.join(str(uuid.uuid4()).split('-'))

        # request a page that does not exist
        if spider.browser.current_url.find('http') < 0:
            spider.browser.get(request.url)

        # set delay between two requests
        time.sleep(3)

        # go to article list
        if spider.page_count == 0:
            spider.browser.find_element_by_xpath(
                '//p[@class="tit"]/a').click()
            # switch to new window
            handles = spider.browser.window_handles
            spider.browser.switch_to.window(handles[-1])
        else:  # go back article list
            if spider.page_index > 0:
                spider.browser.back()
                # set delay between two requests
                time.sleep(3)
            # go to article content
            spider.browser.find_elements_by_xpath(
                '//div[@class="weui_media_bd"]')[spider.page_index].click()
            # prepare to go to next page
            spider.page_index += 1

        # set delay between two requests
        time.sleep(3)

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return HtmlResponse(url=spider.browser.current_url,
                            body=spider.browser.page_source,
                            encoding="utf-8",
                            request=request)

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
