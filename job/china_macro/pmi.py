import os
import re
import uuid
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import HTTPError

import requests
import pandas as pd
from job.ijob import IJob
from bs4 import BeautifulSoup


class Pmi(IJob):

    def __init__(self):
        IJob.__init__(self)
        self.spidername = "data_china_marco_pmi"
        # more init

    def Crawl(self):
        url = self.fetch_content_url()
        print("PMI新闻发布URL:", url)
        if url is not None:
            self.pmi_url(url)
            excel_file_url = self.fetch_file_url(url)
            print("PMI数据文件URL:", excel_file_url)
            if excel_file_url is not None:
                try:
                    self.extract_content(excel_file_url)
                except HTTPError as httpError:
                    print(httpError)

    def extract_content(self, excel_file_url):
        #  创建临时文件
        with TemporaryDirectory() as dirname:
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

            #  获取制造业最新一个月的数据
            data1 = pd.read_excel(local_path, skiprows=14, sheet_name='制造业',
                                  names=['时间', 'PMI', '生产', '新订单', '原材料库存', '从业人员', '供应商配送时间',
                                         '新出口订单', '进口', '采购量', '主要原材料购进价格', '出厂价格', '产成品库存',
                                         '在手订单', '生产经营活动预期'])
            data2 = data1.melt(id_vars="时间", var_name='indicator', value_name='value').dropna()
            data3 = data2.rename(columns={"时间": "bdate", "indicator": "class"})
            data3['bdate'] = self.bdate
            data3["indicator"] = "指数"

            #  获取非制造业最新一个月的数据
            data4 = pd.read_excel(local_path, sheet_name='非制造业', skiprows=14,
                                  names=['时间', '商务活动', '新订单', '投入品价格', '销售价格', '从业人员',
                                         '业务活动预期',
                                         '新出口订单', '在手订单', '存货', '供应商配送时间'])
            data5 = data4.melt(id_vars="时间", var_name='indicator', value_name='value').dropna()
            data6 = data5.rename(columns={"时间": "bdate", "indicator": "class"})
            data6['bdate'] = self.bdate
            data6["indicator"] = "指数"
            # 合并交集的同时,重置索引
            self.storage = pd.concat([self.storage, data3, data6]).reset_index(drop=True)
            print(self.storage)

    def fetch_content_url(self):
        # 尝试获取excel数据的网页链接
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/107.0.0.0 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Host': 'www.stats.gov.cn',
            'Accept-Encoding': 'gzip, deflate'
        }
        url = r'http://www.stats.gov.cn/tjsj/zxfb/'
        res = requests.get(url, headers=headers)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'lxml')
        items = soup.select('div.home div.main div.center div.center_list li')
        keyword = '{0}中国采购经理指数运行情况'.format(datetime.strftime(self.bdate, '%Y年%m月'))
        for item in items:
            if len(item.select('font.cont_tit03')) == 1:
                if item.select('font.cont_tit03')[0].text.startswith(keyword):
                    href = item.select('a')[0]["href"][1:]
                    return r'http://www.stats.gov.cn/tjsj/zxfb{0}'.format(href)

    def fetch_file_url(self, url):
        # 尝试获取包含[采购经理指数]的excel文件链接
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/107.0.0.0 Safari/537.36',
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

    def pmi_url(self, url):
        # 尝试获取综合Pmi的指数
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                      '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/107.0.0.0 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Host': 'www.stats.gov.cn',
            'Accept-Encoding': 'gzip, deflate'
        }
        res = requests.get(url, headers=headers)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, 'lxml')
        items = soup.select('div.main div.center div.center_xilan p.MsoNormal span')[769].text
        cfets = pd.DataFrame()
        cfets["bdate"] = self.bdate,
        cfets["class"] = "综合PMI",
        cfets["indicator"] = "指数",
        cfets["value"] = items.replace('%', '')
        self.storage = cfets



if __name__ == '__main__':
    # 采集调用
    job = Pmi()
    job.Crawl()
    job.Upload()
