from job.ijob import IJob
import requests


class Middle(IJob):
    def Crawl(self):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Host': 'www.chinamoney.com.cn'
        }

        url = r'https://www.chinamoney.com.cn/ags/ms/cm-u-bk-ccpr/CcprHisNew?startDate=2022-11-21&endDate=2022-11-21' \
              r'&currency=USD/CNY'
        res = requests.get(url, headers=headers)
        print(res.text)
        if res.status_code == 200:
            self.storage["class"] = ["USD/CNY"]
            self.storage["bdate"] = ['2022/11/21']
            self.storage["value"] = [res.json()["records"][0]["values"][0]]
            self.storage["indicator"] = "中间价"
            print(self.storage)


if __name__ == '__main__':
    # 采集调用
    job = Middle()
    job.Crawl()
    job.Upload()

