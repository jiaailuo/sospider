import requests
from dto.dotask import KettleCfg
from bs4 import BeautifulSoup


class KettleExecutor:
    def __init__(self, cfg: KettleCfg, bdate):
        self.cfg = cfg
        url = r"http://" + cfg.host + r"/kettle/executeJob/?rep=" + cfg.rep + "&job=" + cfg.job
        if cfg.auth is not None:
            url = url + "&" + cfg.auth
        if cfg.parameters is not None:
            for item in cfg.parameters:
                if cfg.parameters[item] is not None:
                    exec_url = url + "&" + item + "=" + cfg.parameters[item]
        self.exec_url = url.replace(r'{{bdate}}', bdate)
        self.job_id = None

    def ExecJob(self):
        # 启动Job调用
        print("请求kettleJob调用:", self.exec_url)
        try:
            res = requests.get(self.exec_url)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'lxml')
            if res.ok:
                self.job_id = soup.select("id")[0].text
                print("调用成功,JobID=", self.job_id)
        except Exception as ex:
            print("调用出错:", ex)

    @property
    def Status(self):
        # 查询Job执行状态
        url = r"http://" + self.cfg.host + r"/kettle/jobStatus/?xml=y&name="+self.cfg.job + "&id="+self.job_id
        try:
            res = requests.get(url)
            res.encoding = res.apparent_encoding
            soup = BeautifulSoup(res.text, 'lxml')
            if res.ok:
                return soup.text
        except Exception as ex:
            print("调用出错:", ex)
            return None

