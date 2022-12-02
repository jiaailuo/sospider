from datetime import date
import pandas as pd
from sqlalchemy import create_engine
import uuid
from datetime import datetime
import argparse


'''
数据爬虫基类，统一处理以下问题：
1. 规定命令行参数并负责解析
2. 处理爬虫采集数据入库问题

继承的爬虫只需处理以下内容:
1. 爬虫命名: 为爬虫设置唯一名称
2. 数据抓取：按日期要求爬取数据
3. 数据整理：将采集的数据按要求存放到self.storage中,基类统一处理入库问题

storage中的数据存储要求：
1. storage为DataFrame,整理后的数据的列名及数据类型要求如下:
    bdate: 指标日期|日期
    class: 分类名称|字符串
    value: 指标数值|浮点型
    indicator: 指标名称|字符
    
2. 数据示例:以全国CPI数据为例，采集后存储在storage中的数据应为以下结构:
bdate       class  value indicator
2022-10-31  城市    0.0   同比
2022-10-31  农村    0.1   同比
2022-10-31  城市    2.0   环比
2022-10-31  农村    2.5   环比

3. 附加说明:将采集的数据与指标库中的指标建立映射关系，实现指标准确入库
映射关系为: indicator.class => indicatorID
爬虫采集阶段不需要处理

'''

# engine = create_engine('mysql+pymysql://sq_dev:soquant.123@10.80.1.95:3306/sospider')
engine = create_engine('mysql+pymysql://dmp_user:jxm123.@47.105.107.235:3360/sofeeder')


class IJob:
    def __init__(self):
        # 接收命令行参数
        parser = argparse.ArgumentParser()
        parser.add_argument('--bdate', type=str, help="数据日期", required=True)
        parser.add_argument('--options', type=str, help="可选参数", required=False)
        args = parser.parse_args()
        print(args)
        # 需要采集的数据日期
        self.bdate = datetime.strptime(args.bdate, '%Y-%m-%d')
        # 采集扩展参数:Json格式
        self.options = args.options
        # 爬虫名称
        self.spidername = ''
        # 采集数据存储器
        self.storage = pd.DataFrame()
        # 以下为storage的列格式规范
        # self.storage['indicator'] = []
        # self.storage['bdate'] = []
        # self.storage['class'] = []
        # self.storage['value'] = []

    def Crawl(self):
        # 抓取数据，塞到self.data
        pass

    def Upload(self):
        # 将抓取的数据上传入库
        if len(self.storage) > 0:
            batch = uuid.uuid1().hex
            print("入库批次号:", batch)
            self.storage['batch'] = batch
            self.storage['spider'] = self.spidername
            ret = self.storage.to_sql(name='spider_extract_data', con=engine, if_exists="append", index=False)
            print("入库数据条数:", ret)


if __name__ == '__main__':
    job = IJob()
    job.Crawl()
    job.Upload()
