from job.ijob import IJob
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError
import os
import uuid
from tempfile import TemporaryDirectory


# 爬虫类继承IJob类
class Ppi(IJob):

    # 爬虫初始化:为爬虫设置一个唯一名称标识
    def __init__(self):
        IJob.__init__(self)
        self.spidername = "data_china_marco_ppi"

    # 爬虫采集动作:执行具体的采集任务,将采集后的数据按self.storage中的列要求写到self.storage中
    def Crawl(self):
        url = self.fetch_content_url()
        print("PPI新闻发布URL:", url)
        if url is not None:
            excel_file_url = self.fetch_file_url(url)
            print("PPI数据文件URL:", excel_file_url)
            if excel_file_url is not None:
                try:
                    self.extract_content(excel_file_url)
                except HTTPError as httpError:
                    print(httpError)

    def extract_content(self, excel_file_url):
        with TemporaryDirectory() as dirname:
            # 下载文件
            local_path = os.path.join(dirname, uuid.uuid1().hex + ".xlsx")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/86.0.4240.111 Safari/537.36',
                'Upgrade-Insecure-Requests': '1'
            }
            r = requests.get(excel_file_url, headers=headers, stream=True)
            with open(local_path, 'wb') as f:
                for ch in r:
                    f.write(ch)
                f.close()
            # 抽取数据
            data1 = pd.read_excel(local_path, skiprows=3, header=None, names=['分类', '同比', '环比', '累计同比'])
            # 数据预处理
            data2 = data1.melt(id_vars="分类", var_name="indicator", value_name="value").dropna()
            data3 = data2.rename(columns={"分类": "class"})
            data3['class'] = data3['class'].str.replace(' ', '')
            data3['bdate'] = self.bdate
            self.storage = data3
            print(self.storage)


    def fetch_content_url(self):
        # 尝试获取包含[居民消费价格]的网页链接
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/92.0.4515.107 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Host': 'www.stats.gov.cn',
            'Accept-Encoding': 'gzip, deflate'
        }
        url = r'http://www.stats.gov.cn/tjsj/zxfb/index.html'
        res = requests.get(url, headers=headers)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'lxml')
        items = soup.select('div.home div.main div.center div.center_list li')
        keyword = '{0}份工业生产者出厂价格'.format(datetime.strftime(self.bdate, '%Y年%m月'))
        for item in items:
            if len(item.select('font.cont_tit03')) == 1:
                if item.select('font.cont_tit03')[0].text.startswith(keyword):
                    href = item.select('a')[0]["href"][1:]
                    return r'http://www.stats.gov.cn/tjsj/zxfb{0}'.format(href)

    def fetch_file_url(self, url):
        # 尝试获取包含[居民消息价格]的excel文件链接
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/92.0.4515.107 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Host': 'www.stats.gov.cn',
            'Accept-Encoding': 'gzip, deflate'
        }
        res = requests.get(url, headers=headers)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'lxml')
        items = soup.select('div.main div.center div.center_xilan p.MsoNormal span font a')
        if len(items) == 1:
            return url.replace(Path(url).name, '') + items[0]["href"][2:]


if __name__ == '__main__':
    # 采集调用
    job = Ppi()
    job.Crawl()
    job.Upload()



