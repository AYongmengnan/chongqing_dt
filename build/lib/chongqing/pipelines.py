# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
# from itemadapter import ItemAdapter
import pymysql
import time
from chongqing.public import *

test = 1
from urllib import request
import io
from PIL import Image


class ChongqingPipeline:
    def __init__(self):
        self.db = pymysql.connect(host='172.30.0.14', user='root', passwd='qT6I#5gR$gu!IHI1', db='bangqichat',
                                  charset='utf8', port=3306)
        # self.db = pymysql.connect(host='127.0.0.1', user='root', passwd='root', db='test', charset='utf8', port=3306)
        self.cur = self.db.cursor()

    def process_item(self, item, spider):
        print(item['link'])
        # print(item['title'])
        # print(item)
        base = item["base"]
        photo = self.get_photo(item)
        # photo = item["image"]
        photo = del_img(photo)
        item["image"] = del_img(item["image"])
        print('photo:', photo)
        if test > 0:
            if "最新数据!" in item["title"]:
                # is_hot = 0
                # this_hot_words = check_is_hot(item['title'][:-5])
                # if this_hot_words is True:
                #     print("this_hot_words:", this_hot_words)
                #     is_hot = 1
                #
                # is_top = check_is_zhiding(item['title'][:-5])
                # if is_top is True:
                #     print("check_is_zhiding:", is_top)
                #     is_top = 1

                # weight = get_weight_from_media(spider.name)
                if len(item['content']) > 0:
                    status, title, msg = world_replace(item['title'][:-5], 'tit', item["stype"])
                    if not status:
                        print('title敏感词过滤失败', msg)
                        return
                    c_status, content, c_msg = world_replace(item["content"], 'con', item["stype"])
                    if not c_status:
                        print('content敏感词过滤失败', c_msg)
                        return
                    print("stype:", item["stype"])
                    stauts, data = insert_mysql(item["snid"], spider.suid, item["stype"], title, item["image"], photo,
                                                content, item["link"], 0, spider.city, spider.area, 0)
                    print(data)
                    if stauts:
                        print("插入成功")
                    else:
                        print("插入失败")
                    spider.spider_status[base] = True
            else:
                zhongyang_find = "SELECT count(id) FROM ww_article WHERE linkurl = '%s' or title='%s'" % (
                item["link"], item['title'])
                try:
                    self.cur.execute(zhongyang_find)
                    self.db.commit()  # 事务提交
                    zhongyangId = self.cur.fetchone()[0]
                    if zhongyangId != 0:
                        print("数据库有了")
                        return
                except Exception as e:
                    print('查询错误!', e)
                    self.db.rollback()  # 事务回滚
                # is_hot = 0
                # this_hot_words = check_is_hot(item['title'])
                # if this_hot_words is True:
                #     print("this_hot_words:", this_hot_words)
                #     is_hot = 1
                #
                # is_top = check_is_zhiding(item['title'])
                # if is_top is True:
                #     print("check_is_zhiding:", is_top)
                #     is_top = 1
                #
                # weight = get_weight_from_media(spider.name)
                if len(item['content']) > 0:
                    status, title, msg = world_replace(item["title"], 'tit', item["stype"])
                    if not status:
                        print('title敏感词过滤失败', msg)
                        return
                    c_status, content, c_msg = world_replace(item["content"], 'con', item["stype"])
                    if not c_status:
                        print('content敏感词过滤失败', c_msg)
                        return
                    print("stype:", item["stype"])
                    stauts, data = insert_mysql(item["snid"], spider.suid, item["stype"], title, item["image"], photo,
                                                content, item["link"], 0, int(spider.city), int(spider.area), 0)
                    print(data)
                    if stauts:
                        print("插入成功")
                    else:
                        print("插入失败")
                    spider.spider_status[base] = True

    def close_spider(self, spider):
        self.cur.close()
        self.db.close()

    def get_photo(self, item):
        content = item["content"]
        url = item["link"]
        cont, image_list = refactoring_img(content, url)
        photo = ''
        if len(image_list) > 1:
            photo = '。'.join(image_list)
        if len(image_list) == 1:
            photo = image_list[0]
        return photo


def del_img(img_list):
    if "。" in img_list:
        res_list = img_list.split("。")
        image_list = []
        for img in res_list:
            try:
                response = request.urlopen(img)
                tmpIm = io.BytesIO(response.read())
                im = Image.open(tmpIm)
                if im.width < 200 or im.height < 200:
                    continue
                image_list.append(img)
            except Exception as e:
                continue
        picture = "。".join(image_list)
        return picture
    else:
        if img_list:
            try:
                response = request.urlopen(img_list)
                tmpIm = io.BytesIO(response.read())
                im = Image.open(tmpIm)
                if im.width < 200 or im.height < 200:
                    return ''
                return img_list
            except Exception as e:
                return ''
        return ''
