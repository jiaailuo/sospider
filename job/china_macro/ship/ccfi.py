import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from job.ijob import IJob


class Ccfi(IJob):

    # 爬虫初始化:为爬虫设置一个唯一名称标识
    def __init__(self):
        IJob.__init__(self)
        self.spidername = "data_china_marco_ship_ccfi"

    def Crawl(self):
        # 跳过网站证书验证的警告
        requests.packages.urllib3.disable_warnings()

        url = r'https://www.sse.net.cn/index/singleIndex?indexType=ccfi'
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
        # 通过修改x的值获取上期x=1 和本期x=2的数据
        x = 2

        bdate = soup.find('tr').find_all('td')[x].text[2:12]
        data = pd.DataFrame()
        data["bdate"] = []
        data["class"] = []
        data["value"] = []
        data["indicator"] = []
        for item in items[1:]:
            ccfi = {
                "bdate": bdate,
                "class": re.sub('[a-zA-Z0-9\W]', '', item.select('td')[0].text).strip(),
                "value": item.select('td')[x].text,
                "indicator": "指数"

            }
            pos = len(data)
            data.loc[pos] = ccfi
        self.storage = data
        print(self.storage)



if __name__ == '__main__':
    job = Ccfi()
    job.Crawl()
    job.Upload()
