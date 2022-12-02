数矿ETL项目(sospider)工程结构：
1. scheduler部分： 任务启动器,负责唤起任务，包含唤起采集任务及数据检查任务，使用python编写

2. etl部分：数据etl的具体作业，使用kettle编写。为方便调用：启用Kettle自带的Carte服务，该服务允许使用http启动kettle任务

3. spider部分：对kettle作业的补充，将网络数据爬取、解析等kettle不善于处理的环节使用python代码实现，kettle再通过脚本的方式进行调用
   该部分脚本存储在sospider/job目录下


注意事项：
1. PYTHONPATH环境变量设置
脚本中引用了部分自定义包,为保障spider部分的python脚本能正常调用，需要将管理脚本的目录(sopsider文件夹路径)配置在环境变量PYTHONPATH中

2. kettle自带的Carte服务启动
在windows上启动kettle的Carte服务的命令：carte.bat ./pwd/carte-config-master.xml
carte-config-master配置文件中可配置对外的IP、端口、用户名等
Carte服务可配置为windows服务，具体参考：yajsw-stable

3. 使用http调用作业的方式，该部分接口由Carte服务对外提供，同时Carte服务提供更多接口，如查询任务的执行状态等
启动作业调用示例：http://admin:admin@127.0.0.1:8080/kettle/executeJob/?rep=soquant&user=admin&pass=admin&job=pyspider&bdate=2022-11-30&path=ijob.py
其中: ip前面的用户名密码为调用carte服务API的用户名密码, 请求字符串中的user\pass表示连接资源库的用户名与密码,使用数据库资源库时有用
查询作业状态示例: http://admin:admin@127.0.0.1:8080/kettle/jobStatus/?name=pyspider&id=120f04b9-f6c6-40b8-8a6a-ef75bf582e06&xml=y
更多帮助：https://help.hitachivantara.com/Documentation/Pentaho/9.2/Developer_center/REST_API_Reference/Carte/030