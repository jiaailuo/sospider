import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

from job.ijob import IJob


class Cicfi(IJob):

    # 爬虫初始化:为爬虫设置一个唯一名称标识
    def __init__(self):
        IJob.__init__(self)
        self.spidername = "data_china_marco_ship_cicfi"

    def Crawl(self):
        # 跳过网站证书验证的警告
        requests.packages.urllib3.disable_warnings()

        url = r'https://www.sse.net.cn/index/singleIndex?indexType=cicfi'
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Host': 'www.sse.net.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/107.0.0.0 Safari/537.36 ',
            'Cookie': 'BIGipServerPOOL_SSE=2875566272.37151.0000; JSESSIONID=DAD247D270763B4BA86E5A575FF9F84A',
            'Origin': 'https://www.sse.net.cn'
        }
        res = requests.post(url, headers=headers, verify=False)
        res.encoding = 'utf-8'
        soup = BeautifulSoup(res.text, 'lxml')
        items = soup.select('body.body div#content.container div.row div#center div#right table.lb1 tbody tr')

        # 因为网站需要登录无法查看历史数据所以只能查看上期和本期数据
        # 当x=1时显示上期的数据  当x=2时显示本期数据
        x = 2

        bdate = soup.find('tr').find_all('td')[x].text[2:12]
        data = pd.DataFrame()
        data["bdate"] = []
        data["class"] = []
        data["indicator"] = []
        data["value"] = []
        for item in items[1:]:
            cfets = {
                "bdate": bdate,
                "class": item.select('td')[0].text,
                "indicator": "指数",
                "value": item.select('td')[x].text.strip()
            }
            data.loc[len(data)] = cfets
            #  因为空字符串不是空值所以 data.dropna()删除不了,必须将空字符串变成空值
            #  如果x不等于空字符串，就返回原值，否则返回None
            data = data.applymap(lambda x: np.where(x != '', x, None))
            data.dropna(inplace=True)
        self.storage = data
        print(self.storage)


if __name__ == '__main__':
    job = Cicfi()
    job.Crawl()
    job.Upload()
