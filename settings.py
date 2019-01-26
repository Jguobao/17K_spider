#coding=utf-8

class Settings:
    """用于设置初始化爬虫的信息类"""
    def __init__(self):
        """初始化爬虫的属性设置"""
        # 爬取的起始页
        self.start_url="http://all.17k.com/lib/book/2_0_0_0_0_0_1_0_1.html?"
        # 小说与爬取信息保存路径
        self.save_path = "/home/jgb/python/python_jgb/17k_小说下载/"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36"}
