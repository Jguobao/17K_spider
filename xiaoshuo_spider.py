# coding=utf-8
'''
作者：Jguobao
QQ:779188083
email:jgb2010start@163.com
'''
import requests
from lxml import etree
import json
from settings import Settings

class NovelSpider:
    def __init__(self):
        settings = Settings()
        self.start_url = settings.start_url
        self.url = "http://www.17k.com/list/1038316.html"  # "http://www.17k.com/chapter/2938105/36788407.html"
        self.headers = settings.headers
        self.path = settings.save_path
    def parse_url(self, url):
        response = requests.get(url, headers=self.headers)
        if response.status_code != 200:
            return None
        return response.content.decode()

    def get_detail_page(self, html_str, index=""):
        """
        获取阅读页的文本与标题
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

    def get_txt_name(self, html_str):

        """
        获取get网页的响应html_str
        """
        html_str_etree = etree.HTML(html_str)
        filename = html_str_etree.xpath("//div[@class='Main List']//h1/text()")[0] + '.txt' if len(html_str_etree.xpath("//div[@class='Main List']//h1")) > 0 else "无名"
        return filename

    def get_url_list(self, html_str):
        """
        获取的 章节以及 卷
        """
        item_list = []
        html_str_etree = etree.HTML(html_str)
        url_list = html_str_etree.xpath("//dl[@class='Volume']//dd/a/@href")
        volume_list = html_str_etree.xpath("//dl[@class='Volume']")  # 获取所有的卷 并且从卷下获取所有的卷标 章节
        for volume in volume_list:
            item = {}
            item['卷标'] = volume.xpath(".//span[@class='tit']/text()")[0]
            item['info'] = volume.xpath(".//span[@class='info']/text()")[0]
            # 获取下面的所有的a标签
            a_list_etree = volume.xpath("./dd/a")
            a_list = []
            for a in a_list_etree:
                item2 = {}
                title2 = a.xpath(".//span[@class='ellipsis']/text()")[0].strip()
                item2[title2] = "http://www.17k.com" + a.xpath("./@href")[0]
                a_list.append(item2)
            item['章节'] = a_list

            item_list.append(item)
            # 根据a标签列表获取所有章节与对应的链接
        url_list = ["http://www.17k.com" + url for url in url_list]

        return item_list

    def save_txt(self, txt_list, filename):
        """
        保存小说
        """
        with open(self.path + filename, "a", encoding='utf8') as f:
            f.write(txt_list[0])
            for wd in txt_list[1][:-2]:
                f.write(wd)

    def process_item_list(self, item_list, filename):  # 获取小说的章节内容并保存
        for item in item_list:
            volume_label = item['卷标']
            volume_info = item['info']
            item_list = item['章节']
            lens2 = len(item_list)
            for item in item_list:
                for i in item:
                    print(i)
                    title = i
                    html_detail_str = self.parse_url(item[i])
                    txt_list = list(self.get_detail_page(html_detail_str))
                    txt_list[0] = '\t\t' + title + '\n'
                    self.save_txt(txt_list, filename)

    def get_note_list(self, html_str):
        """
        获取小说列表页的的小说url列表
        """
        book_list = []
        html_str_etree = etree.HTML(html_str)
        detail_url_etree = html_str_etree.xpath("//tbody//tr[contains(@class,'bg')]")  # 获取了所有的tr标签
        print("合计：", len(detail_url_etree))
        next_url = html_str_etree.xpath("//div[@class='page']/a[contains(string(), '下一页')]/@href")[
            0]  # 获取含有下一页的按钮的url
        next_url = "http://all.17k.com/" + next_url if next_url != "‘javascript:void(0);" else None
        for detail in detail_url_etree:
            item = {}
            item['id'] = detail.xpath(".//td[@class='td1']//text()")[0]
            item['书名'] = detail.xpath(".//td[@class='td3']//a/text()")[0]
            item['href'] = detail.xpath(".//td[@class='td3']//a/@href")[0]
            item['href2'] = item['href'].replace('book', 'list')
            item['类别'] = detail.xpath(".//td[@class='td2']//a/text()")[0]
            item['作者'] = detail.xpath(".//td[@class='td6']//a/text()")[0]
            item['更新章节'] = detail.xpath(".//td[@class='td4']//a/text()")[0] if len(
                detail.xpath(".//td[@class='td4']//a/text()")) > 0 else None
            item['字数'] = detail.xpath(".//td[@class='td5']/text()")[0]
            item['更新时间'] = detail.xpath(".//td[@class='td7']/text()")[0].strip()
            item['状态'] = detail.xpath(".//td[@class='td8']//em/text()")[0].strip()
            self.save_json(item)
            book_list.append(item)
        return [book_list, next_url]

    def process_book_list(self, book_list):
        """
        处理小说列表页
        """
        for book in book_list:
            id = book['id']
            filename = book['书名']
            href2 = book['href2']
            family = book['类别']
            author = book['作者']
            filename = id + '-' + filename + '-' + family + '-' + author
            html_str = self.parse_url(href2)
            print(href2)
            item_list = self.get_url_list(html_str)
            self.process_item_list(item_list, filename)  # 处理一本小说

    def save_json(self, item):
        """
        保存json字符串，用于存储爬取的所有小说记录
        """
        with open(self.path+'info.json', 'a') as f:
            f.write(json.dumps(item, ensure_ascii=0, indent=2))

    def run(self, page_num=1):  # page_num 输入要爬取的页面数
        """
        逻辑run方法
        """
        page_num -= 1  #
        url_html = self.parse_url(self.start_url)
        book_list, next_url = self.get_note_list(url_html)
        self.process_book_list(book_list)
        if page_num > 0:
            for i in range(page_num):
                url_html = self.parse_url(next_url)
                book_list, next_url = self.get_note_list(url_html)
                print(book_list)

if __name__ == '__main__':
    ns = NovelSpider()  # 将要爬取得需要的信息归类到settings文件中
    ns.run(1) #run方法输入要爬取多少页
