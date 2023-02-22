import scrapy
from scrapy import Selector
from chongqing.items import ChongqingItem
from chongqing.public import *

'''
    巫山县人民政府
'''


class CqCqwsGovCnSpider(scrapy.Spider):
    name = 'cq_cqws_gov_cn'
    allowed_domains = ['cqws.gov.cn']
    start_urls = ['http://cqws.gov.cn/zwxx_258/qxdt/']
    city = '500000'
    area = '500237'
    suid = 67160
    spider_status = {}
    spider_a_list = {}

    def parse(self, response):
        url = self.start_urls[0]
        base = "dynamic"
        snid = 95
        stype = 1
        self.spider_status[base] = False
        self.spider_a_list[base] = []
        li_list = response.xpath('//ul[@class="new-list"]/li').getall()
        print("crawl li length:", len(li_list))
        cont_url_list = []
        for li in reversed(li_list):
            if not li:
                continue
            content_url = Selector(text=li).xpath('//a/@href').extract_first()
            if content_url:
                if 'http' not in content_url:
                    content_url = parse.urljoin(url, content_url)
                cont_url_list.append((content_url, li))
        self.spider_a_list[base] = cont_url_list
        if len(cont_url_list) == 0:
            print('pass')
        else:
            li = cont_url_list[-1][1]
            title = Selector(text=li).xpath('//a/@title').extract_first().strip()
            num = is_article_exists(self.suid, title, 1)
            if num == 0:
                index = 0
                url, li_tag = self.spider_a_list[base][index]
                yield scrapy.Request(url, callback=self.parse_content,
                                     meta={"li_tag": li_tag, "index": index, "base": base, "url": url, "snid": snid,
                                           "stype": stype}, dont_filter=True)
            else:
                print("数据库已有最新数据了!")
                index = len(self.spider_a_list[base]) - 1
                url, li_tag = self.spider_a_list[base][index]
                yield scrapy.Request(url, callback=self.parse_detail_content,
                                     meta={"li_tag": li_tag, "index": index, "base": base, "url": url, "snid": snid,
                                           "stype": stype}, dont_filter=True)

    def parse_content(self, response):
        base, index, snid, stype = None, None, None, None
        try:
            item = ChongqingItem()
            url = response.meta["url"]
            base = response.meta["base"]
            li_tag = response.meta["li_tag"]
            index = response.meta["index"]
            snid = response.meta["snid"]
            stype = response.meta["stype"]
            title = Selector(text=li_tag).xpath('//a/@title').extract_first()
            time_text = Selector(text=li_tag).xpath('//span/text()').extract_first()
            content = response.xpath('//div[contains(@class,"view TRS_UEDITOR")]').getall()
            # if not content:
            #     content = response.xpath('//div[@class="view TRS_UEDITOR trs_paper_default trs_web"]').getall()
            img = ''
            if len(content) == 0:
                return
            con_text = ''
            for con in content:
                con_text += con
            article, images = refactoring_img(con_text, url)
            image = images[0] if images else ''
            img_link = img if img else image
            item["title"] = title.strip()
            item["con_time"] = time_stamp(time_text.strip())
            item["link"] = url
            item["image"] = img_link
            item["content"] = article
            item["base"] = base
            item["snid"] = snid
            item["stype"] = stype
            yield item
        except Exception as e:
            print('解析新闻出错:', repr(e))
        finally:
            if self.spider_status[base] is False and index < len(self.spider_a_list[base]) - 1:
                index = index + 1
                url, li_tag = self.spider_a_list[base][index]
                yield scrapy.Request(url, callback=self.parse_content,
                                     meta={"li_tag": li_tag, "index": index, 'base': base, "url": url, "snid": snid,
                                           "stype": stype},
                                     dont_filter=True)

    def parse_detail_content(self, response):
        base, index, snid, stype = None, None, None, None
        try:
            item = ChongqingItem()
            url = response.meta["url"]
            base = response.meta["base"]
            li_tag = response.meta["li_tag"]
            index = response.meta["index"]
            snid = response.meta["snid"]
            stype = response.meta["stype"]
            title = Selector(text=li_tag).xpath('//a/@title').extract_first()
            time_text = Selector(text=li_tag).xpath('//span/text()').extract_first()
            content = response.xpath('//div[contains(@class,"view TRS_UEDITOR")]').getall()
            # if not content:
            #     content = response.xpath('//div[@class="view TRS_UEDITOR trs_paper_default trs_web"]').getall()
            img = ''
            if len(content) == 0:
                return
            con_text = ''
            for con in content:
                con_text += con
            article, images = refactoring_img(con_text, url)
            image = images[0] if images else ''
            img_link = img if img else image
            item["title"] = title.strip() + "最新数据!"
            item["con_time"] = time_stamp(time_text.strip())
            item["link"] = url
            item["image"] = img_link
            item["content"] = article
            item["base"] = base
            item["snid"] = snid
            item["stype"] = stype
            yield item
        except Exception as e:
            print('解析新闻出错:', repr(e))
