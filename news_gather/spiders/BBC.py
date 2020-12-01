import scrapy
from bs4 import BeautifulSoup
from scrapy import Spider, Request
from scrapy.settings.default_settings import DEFAULT_REQUEST_HEADERS

from news_gather.items import NewsGatherItem


class BbcSpider(scrapy.Spider):
    name = 'BBC'
    allowed_domains = ['bbc.com']
    start_urls = 'https://www.bbc.com/news/live/world-asia-47639453/page/1'

    # first step to parse
    def start_requests(self):
        DEFAULT_REQUEST_HEADERS['Accept'] = '*/*'
        DEFAULT_REQUEST_HEADERS['Host'] = 'bbc.com'
        DEFAULT_REQUEST_HEADERS['Referer'] = 'http://bbc.com/'
        req = Request(self.start_urls.format(category="news"), callback=self.parse_list, meta={"title": "ContentList"},
                      encoding='utf-8')
        yield req

    # got the page and parse to get list of news
    def parse_list(self, response):
        news_list = response.xpath("//*[@id='lx-stream']/div[1]/ol/li")
        for news in news_list:
            msg = response.meta
            msg['title'] = news.xpath(".//header//h3/a/span/text()").get()
            msg['url'] = "https://" + DEFAULT_REQUEST_HEADERS['Host'] + news.xpath(".//header//h3/a/@href").get()
            # call parse_content to parse the passage and get content
            yield Request(msg["url"], callback=self.parse_content, meta=msg)
        # check if reach the end of website
        next_link = response.xpath("//a[@rel='next']/@href").get()
        print(next_link)
        # if not, seek next page
        if next_link:
            next_link = "https://" + DEFAULT_REQUEST_HEADERS['Host'] + next_link
            req = Request(next_link.format(category="news"), callback=self.parse_list,
                          meta={"title": "ContentList"},
                          encoding='utf-8')
            yield req

    def parse_content(self, response):
        if 'av' not in response.request.url:
            text = response.xpath("//article/div//p//text()").getall()
            content = ''
            # combine sentences
            for i in range(len(text)):
                if i == 0:
                    pass
                else:
                    content += text[i] + ' '
            publish_time = response.xpath("//time/@datetime").get()
            news_item = NewsGatherItem()
            news_item['title'] = response.meta.get("title", "")
            news_item['publish_time'] = publish_time
            news_item['content'] = content
            news_item['url'] = response.meta.get("url", "")

            pass
