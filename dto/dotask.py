import datetime
import ast


class DoTaskDTO:
    def __init__(self, _dict: dict):
        self._dict = _dict
        self._executor = None
        try:
            if _dict.get('do') is not None:
                do = ast.literal_eval(_dict.get('do'))
                self._executor = do.get("executor")
                if self._executor == "kettle":
                    self._kettle = do.get("kettle")
                else:
                    print("不支持的执行器类型")
        except SyntaxError as error2:
            print("do配置错误,无效的JSON格式", _dict.get('do'))

    @property
    def id(self):
        return self._dict.get("id")

    @property
    def space(self):
        return self._dict.get("space")

    @property
    def name(self):
        return self._dict.get("name")

    @property
    def bdate(self):
        return datetime.datetime.strftime(self._dict.get("bdate"), "%Y-%m-%d")

    @property
    def options(self):
        return self._dict.get("options")

    @property
    def executor(self):
        return self._executor

    @property
    def kettle(self):
        return KettleCfg(self._kettle)


class KettleCfg:
    def __init__(self, _dict):
        self._dict = _dict

    @property
    def host(self):
        return self._dict.get("host")

    @property
    def rep(self):
        return self._dict.get("rep")

    @property
    def auth(self):
        return self._dict.get("auth")

    @property
    def job(self):
        return self._dict.get("job")

    @property
    def parameters(self):
        return self._dict.get("parameters")


