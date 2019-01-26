# coding=utf-8
import requests
from lxml import etree
import json
import re


class NovelSpider:
    def __init__(self):
        self.url = "http://www.17k.com/list/2931242.html"  # "http://www.17k.com/chapter/2938105/36788407.html"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"}

    def parse_url(self, url):
        print(url)
        response = requests.get(url, headers=self.headers)
        return response.content.decode()

    def get_detail_page(self, html_str, index=""):
    """获取阅读页的文本与标题
    """
        if index != "":
            index = str(index) + "."
        html_str_etree = etree.HTML(html_str)
        title = html_str_etree.xpath("//div[@class='readAreaBox content']/h1/text()")[0]
        word = html_str_etree.xpath("//div[@class='readAreaBox content']/div[@class='p']/text()")
        word = ["  " + w.strip() + "\n" if len(w.strip()) > 0 else None for w in word]
        title = "\t\t\t" + index + title.strip() + "\n"
        for w in word[:]:
            if w is None:
                word.remove(w)
        return title, word[:-1]

    # //div[@class='Main List']//h1 获取书名
    # //dl[@class='Volume']//dd/a/@href
    def get_txt_name(self, html_str):
    """获取get网页的响应html_str
    """
        html_str_etree = etree.HTML(html_str)
        filename = html_str_etree.xpath("//div[@class='Main List']//h1/text()")[0] + '.txt' if len(
            html_str_etree.xpath("//div[@class='Main List']//h1")) > 0 else "无名"
        return filename

    def get_url_list(self, html_str):
    """获取的 章节以及 卷
    """
        html_str_etree = etree.HTML(html_str)
        url_list = html_str_etree.xpath("//dl[@class='Volume']//dd/a/@href")
        url_list = ["http://www.17k.com" + url for url in url_list]
        return url_list

    def save_txt(self, txt_list, filename):
        with open(filename, "a", encoding='utf8') as f:
            f.write(txt_list[0])
            for wd in txt_list[1][:-2]:
                f.write(wd)

    def run(self):
        html_str = self.parse_url(self.url)  # 获取小说主页
        filename = self.get_txt_name(html_str)
        print(filename)
        # 获取详情页的url列表
        url_list = self.get_url_list(html_str)#更新在其中添加获取的 章节以及 卷
        for url_detail in url_list:
            html_detail_str = self.parse_url(url_detail)
            index = url_list.index(url_detail)+1
            txt_list = self.get_detail_page(html_detail_str, index=index)
            # print(txt_list)
            self.save_txt(txt_list, filename)
        print("%s:保存成功" % filename)


if __name__ == '__main__':
    ns = NovelSpider()
    ns.run()
