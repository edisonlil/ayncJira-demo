# 环境准备
# !pip3 install jira
# !pip3 install pandas
# !pip3 install openpyxl

# 参考资料：https://developer.atlassian.com/cloud/jira/platform

import pandas as pd
from jira import JIRA

# Jira 域名
JIRA_SERVER = 'http://xxx.xxx.xxx.xx:28080/'
# Jira账号（必须有建子任务权限）
JIRA_USER = "admin"
# Jira密码
JIRA_PWD = "xxx"

# 基础参数
# Jira 项目 code
PROJECT = "BDPT"

# 难度等级
difficultyLevelMap = {
    '不紧急不重要': '10900',
    '不紧急重要': '10901',
    '重要不紧急': '10902',
    '重要紧急': '10903',
}
# 工号对应关系
nameTransferId = {
    '小猴子': 'ID'


}
# link: http://139.198.168.71:28080/rest/api/2/project/BDPT/components
componentsMap = {
    "产品设计":"10125",
    "安装部署":"10123",
    "应用改造":"10124"
}

#模块对应关系

# 导入逻辑
# 无视哪次迭代，只识别故事编号
# jira工具
class JiraTool:
    # 初始化方法
    def __init__(self):
        self.server = JIRA_SERVER
        self.basic_auth = (JIRA_USER, JIRA_PWD)
        self.jiraClinet = None

    # 登陆
    def login(self):
        self.jiraClinet = JIRA(server=self.server, basic_auth=self.basic_auth)
        if self.jiraClinet is not None:
            return True
        else:
            return False

    # Excel 日期处理
    def processDate(self, rawDate):
        if isinstance(rawDate, pd._libs.tslibs.timestamps.Timestamp):
            return str(rawDate)[0:10]
        else:
            if rawDate != '' and "/" in rawDate:
                return rawDate.replace("/", "-").replace("\xa0", "")
            else:
                return rawDate.replace("\xa0", "")

    def getComponents(self,row):

        if getattr(row, '职责分类') is None:
            return []

        components = str(getattr(row, '职责分类')).split(",")

        result = []
        for component in components:

            result.append({
               "id":componentsMap[component]
            })
        pass

        return result
    pass
    def readExceltoJira(self, excelFilePath):
        df = pd.read_excel(excelFilePath,
                           sheet_name='任务管理',
                           skiprows=[1],
                           engine='openpyxl'
                           )

        for row in df.itertuples():


            # 预估工时
            originalEstimate = str(getattr(row, '计划完成时长')) + 'h'

            # 入参字段
            fields = {
                "project": {"key": PROJECT},
                "assignee": {"name": nameTransferId[getattr(row, '任务执行人')]},
                # "labels": [getattr(row, 'label')],
                "summary": getattr(row, '任务描述').strip().replace('\n', ''),
                # "customfield_10006": storyPoint,
                "timetracking": {
                    "originalEstimate": originalEstimate
                },
                # "customfield_11300": {"id": difficultyLevelMap[getattr(row, '重要紧急程度')]},
                "reporter": {"name": nameTransferId[getattr(row, '报告人')]},
                "components": self.getComponents(row)
                # "fixVersions": [{"name": str(getattr(row, '变更版本')).strip()}]
            }

            # # 任务类型，故事子任务，不挂史诗，没故事的是任务，挂史诗
            issueTypeSubTask = {"id": "10101", "name": "子任务"}
            issueTypeTask = {"id": "10100", "name": "任务"}


            if isinstance(getattr(row, '序号'), str):
                fields['parent'] = {"key": getattr(row, 'storyKey').strip()}
                fields['issuetype'] = issueTypeSubTask
            else:
               # fields['customfield_10000'] = getattr(row, 'epic')
                fields['issuetype'] = issueTypeTask

            # 任务描述
            if isinstance(getattr(row, '任务描述'), str):
                fields['description'] = getattr(row, '任务描述')
            else:
                fields['description'] = ''

            # 任务开始、结束时间
            startDate = getattr(row, '开始日期')
            # startDate = startDate.strip()
            endDate = getattr(row, '预计完成')
            # endDate = endDate.strip()
            # endDate = endDate[0:10]
            # print('endDate',endDate)

            from dateutil.parser import parse
            # print('startDate',startDate)
            # print(startDate.__format__('%Y/%m/%d'))

            try:
                startDate = startDate.__format__('%Y/%m/%d')
            except Exception as e:
                {}

            try:
                startDate = startDate.__format__('%Y-%m-%d')
            except Exception as e:
                {}

            try:
                endDate = endDate.__format__('%Y/%m/%d')
            except Exception as e:
                {}

            try:
                endDate = endDate.__format__('%Y-%m-%d')
            except Exception as e:
                {}

            # endDate = endDate.__format__('%Y/%m/%d')

            # startDate = startDate.replace("/", "-")
            # endDate   =  endDate.replace("/", "-")

            # if startDate is not None and (
            #         isinstance(startDate, str) or isinstance(startDate, pd._libs.tslibs.timestamps.Timestamp)):
            #     fields['customfield_10607'] = self.processDate(startDate)
            # if endDate is not None and (
            #         isinstance(startDate, str) or isinstance(startDate, pd._libs.tslibs.timestamps.Timestamp)):
            #     fields['customfield_10609'] = self.processDate(endDate)

            # print(fields)
            if self.jiraClinet is None:
                self.login
            create_issue = self.jiraClinet.create_issue(fields)
            print(create_issue)

            # 调用
            # 启动


if __name__ == "__main__":

    print("开始导入")
    jiraTool = JiraTool()
    jiraTool.login()

    jiraTool.readExceltoJira(r'./任务管理.xlsx')
    print("导入完毕")