# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class WechatPipeline(object):
    def process_item(self, item, spider):
        article = dict(item)
        spider.ocean.article.update(
            {'title': article['title']},
            {
                'title': article['title'],
                'date': article['date'],
                'html': article['html'],
                'markdown': article['markdown']
            },
            True
        )
        return item
