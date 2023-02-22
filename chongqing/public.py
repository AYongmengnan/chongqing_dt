import json
import time
import requests
from urllib import parse
from lxml.html import tostring
from lxml import etree


def refactoring_img(article, prefix):
    images_list = []
    if not article:
        return article, []
    html = etree.HTML(article)
    imglist = html.xpath('//img')
    iframelist = html.xpath('//iframe')
    imglist += iframelist
    for img in imglist:
        try:
            src = img.xpath("@src")[0]
        except Exception as e:
            continue
        if "http" not in src:
            new = parse.urljoin(prefix, src)
            img.attrib['src'] = new
        if img not in iframelist and not check_is_404(img.attrib['src']):
            images_list.append(img.attrib['src'])

    a_tag_list = html.xpath("//a")
    for a in a_tag_list:
        href = a.xpath("@href")
        if href and href[0] != "#":
            new = parse.urljoin(prefix, href[0])
            a.attrib['href'] = new
    code = "utf-8"
    article = tostring(html, encoding=code).decode(code)
    return article, images_list


def check_is_404(url):
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == '404':
            return True
        else:
            return False
    except Exception as e:
        return False


def time_stamp(timeA):
    if '年' in timeA:
        timeA = timeA + " 00:00:00"
        timeArray = time.strptime(timeA, "%Y年%m月%d日 %H:%M:%S")

    elif '.' in timeA:
        if len(timeA) == 16:
            timeA = timeA + ":00"
        else:
            timeA = timeA + " 00:00:00"
        timeArray = time.strptime(timeA, "%Y.%m.%d %H:%M:%S")

    else:
        if '/' in timeA:
            timeA = timeA.replace('/', '-')
        if len(timeA) == 10:
            timeA = timeA + " 00:00:00"
        if len(timeA) == 16:
            timeA = timeA + ":00"
        if len(timeA) == 19:
            pass
        timeArray = time.strptime(timeA, "%Y-%m-%d %H:%M:%S")
    timeStamp = int(time.mktime(timeArray))
    return timeStamp


def get_photo(item):
    content = item["content"]
    url = item["link"]
    cont, image_list = refactoring_img(content, url)
    photo = ''
    if len(image_list) > 1:
        for img in image_list:
            photo += img + '。'
    if len(image_list) == 1:
        photo = image_list[0]
    return photo


def world_replace(content, stype, cont_type):
    try:
        url = 'http://172.30.0.9:9999/api/communal/getBadWord'
        data = {
            "str": content
        }
        res = requests.post(url, data=data)
        # post请求错误 直接返回
        if res.status_code != 200:
            return False, content, 'res.status_code:[{}]'.format(res.status_code)
        else:
            data = json.loads(res.text)
            # 接口返回错误 直接返回
            if data["code"] != 200:
                return False, content, 'replace:code[{}],msg[{}]'.format(data['code'], data['msg'])
            else:
                world_list = data["content"]
                # 无敏感词 直接返回
                if len(world_list) == 0:
                    return True, content, ''
                if stype == 'con':
                    # 新闻内容是视频类的 直接返回
                    if int(cont_type) == 2:
                        return True, content, ''
                    html_e = etree.HTML(content)
                    for m in list(set(world_list)):
                        xpath_ = """.//*[contains(./text(),'{}')]""".format(m)
                        m_p_l = html_e.xpath(xpath_)
                        for m_p in m_p_l:
                            new_text = m_p.text.replace(m, "*" * len(m))
                            m_p.text = new_text
                    return True, tostring(html_e, encoding='utf-8').decode('utf-8'), ''
                else:
                    for m in list(set(world_list)):
                        content = content.replace(m, "*" * len(m))
                    return True, content, ''
    except Exception as e:
        return False, content, repr(e)


def is_article_exists(uid, title, stype):
    url = "http://172.30.0.9:9999/api/elastissearch/judgeArticle"
    data = {
        "uid": uid,
        "title": title,
        "type": stype
    }
    res = requests.post(url, data=data)
    if res.status_code != 200:
        return False, 'res.status_code:[{}]'.format(res.status_code)
    else:
        data = json.loads(res.text)
        if data["code"] != 200:
            return False, 'replace:code[{}],msg[{}]'.format(data['code'], data['msg'])
        else:
            result = data["content"]["is_judge"]
            return result


def insert_mysql(nid, uid, stype, title, image, photo, content, linkurl, weight, city, area, is_top):
    # "http://{}/api/elastissearch/articleSave?nid=0&uid=0&type=1&weight=0&city=0&area=0&is_top=0"
    url = "http://172.30.0.9:9999/api/elastissearch/articleSave"
    data = {
        "nid": nid,
        "uid": uid,
        "type": stype,
        "title": title,
        "image": image,
        "photo": photo,
        "content": content,
        "linkurl": linkurl,
        "weight": weight,
        "city": city,
        "area": area,
        "is_top": is_top
    }
    res = requests.post(url, data=data)
    if res.status_code != 200:
        return False, 'res.status_code:[{}]'.format(res.status_code)
    else:
        data = json.loads(res.text)
        if data["code"] != 200:
            return False, 'replace:code[{}],msg[{}]'.format(data['code'], data['msg'])
        else:
            return True, data
