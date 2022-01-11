# -*- coding: utf-8 -*-
import sys, os
from PyQt5 import sip
from PyQt5 import QtNetwork,QtWebEngineCore,QtPrintSupport
from mmgui.asyncqt import run_on_ui_thread
from mmgui import App, BrowserWindow
import json
import subprocess
import webbrowser

# 基础表头
HeaderModel = ['appKey', 'UnityVersion', 'Define', '.Net_Version', 'Type']
IsCommon = True
config_path = './config/config.json'

# 构建BrowserWindow
app = App(headless=False)
win = None


CommonList = []
SpecialList = []

Environment = 'Rule'  # 安装包还是规则
IsTest = True  # 默认测试环境
IsUpload = 'true'

check_win=None


def open_url(url):
    webbrowser.open(url)


def on_create(ctx):
    global win
    win = BrowserWindow({
        "title": "DLL更新工具",
        "width": 1250,
        "height": 720,
        # "dev_mode": True
    })

    # 注册函数到JS层
    win.webview.bind_function("open_file", open_file)
    win.webview.bind_function("GetIsCommon", GetIsCommon)  # 改变IsCommon
    win.webview.bind_function("UpdateConfig", UpdateConfig)  # 更新配置表
    win.webview.bind_function("UpdateDLL", UpdateDLL)  # 得到开始更新指令
    win.webview.bind_function("getIsRule", getIsRule)  # 获取其他更新数据
    win.webview.bind_function("getIsUpload", getIsUpload)  # 获取其他更新数据
    win.webview.bind_function("getIsTest", getIsTest)  # 获取其他更新数据
    win.webview.bind_function("open_url", open_url)  # 获取其他更新数据
    win.webview.bind_function("open_check", open_window)  # 获取其他更新数据

    win.webview.load_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), "index.html"))
    # 测试CheckPage
    win.webview.bind_function("open_check", open_DLLCheck())
    # win.show()


@run_on_ui_thread                                        # 打开窗口加上装饰器 @run_on_ui_thread
def open_DLLCheck():
    global check_win
    check_win = BrowserWindow({
        "title": "DLL检查工具",
        "width": 1280,
        "height": 750,
        "dev_mode": True
    })
    check_win.webview.load_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), "CheckPage.html"))
    check_win.show()


def open_window():
    global win
    win.webview.bind_function("open_check", open_DLLCheck())  # 打开DLL检查工具


# 监听是否测试环境
def getIsTest(Test):
    global IsTest
    IsTest = Test


# 监听是否上传第三方
def getIsUpload(upload):
    global IsUpload
    if upload:
        IsUpload = 'true'
    else:
        IsUpload = 'false'


# 监听是否规则检查
def getIsRule(res):
    print(res)
    global Environment
    Environment = res


# testCommonID = '0a6fc6049a2f4544bddeba78a4f28520'   # test公用
# testSpecialID = 'cb0f911602d64d77ad94eebb754ee8e1'  # test特殊


testCommonID = 'df6c1f6867674a448c2af3ebc07ffb2e'   # 测试环境的公用
testSpecialID = '2f7170fe12694b32b010eaf0afa68613'  # 测试环境的特殊


formalCommonID = '093687d7efab4bff937bf5079f2c9537'   # 正式环境的公用
formalSpecialID = '0f92c7dc81b748c5842fda7e85f94067'  # 正式环境的特殊

def UpdateDLL(NeedUpdateList):
        QueryData = ''
        success = 0
        failure = 0
        # print(NeedUpdateList)
        IsRule = 'true'
        if IsTest:
            CommonID = testCommonID
            SpecialID = testSpecialID
        else:
            CommonID = formalCommonID
            SpecialID = formalSpecialID
        # 遍历每个元素的
        for item in NeedUpdateList:
            print(item)
            FrameworkVersion = item["FrameworkVersion"]
            Unity_Version = item["Unity_Version"]
            Define = item["Define"]
            if Environment == 'Package':    # Environment 控制IsRule
                IsRule='false'
            if IsCommon:
                    QueryData = " \"{\\" + f'"FrameworkVersion\\":\\"{FrameworkVersion}\\",\\"unity_version\\":\\"{Unity_Version}\\",\\"Define\\":\\"{Define}\\",\\"is_rule\\":{IsRule},\\"is_upload_dll\\":{IsUpload}' + '}"'
                    TestCommonCMD = f'curl -X POST https://devops.testplus.cn/ms/process/api/external/pipelines/{CommonID}/build -H "Content-Type: application/json" -d' + QueryData
                    print(TestCommonCMD)
                    result = subprocess.Popen(TestCommonCMD,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    r = str(result.stdout.readlines()[1])
                    if r.find('0') > -1:
                        success = success+1
                    else:
                        failure = failure+1

            else:
                    appKey=item["appKey"]
                    QueryData = " \"{\\" + f'"Appkey\\":\\"{appKey}\\",\\"FrameworkVersion\\":\\"{FrameworkVersion}\\",\\"unity_version\\":\\"{Unity_Version}\\",\\"Define\\":\\"{Define}\\",\\"is_rule\\":{IsRule} '+'}"'
                    TestSpecialCMD = f'curl -X POST https://devops.testplus.cn/ms/process/api/external/pipelines/{SpecialID}/build -H "Content-Type:application/json" -d' + QueryData
                    print(TestSpecialCMD)
                    result = subprocess.Popen(TestSpecialCMD,shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    r = str(result.stdout.readlines()[1])
                    if r.find('"status" : 0') > -1:
                        success = success + 1
                    else:
                        failure = failure + 1

        return f"成功提交{success}条,失败{failure}条 "


# 打开配置文件
def open_file():
    if os.path.exists(config_path):
        osCommandString = f"notepad.exe {config_path}"
        os.system(osCommandString)
    else:
        return '打开错误！'


def load_config():
    global CommonList
    global SpecialList
    load_config = {}
    with open(config_path) as conf:
        load_config = json.load(conf)
    CommonList = (list)(load_config["common"])
    SpecialList = (list)(load_config["special"])


# 控制给什么数据
def GetIsCommon(Common):
    global IsCommon
    IsCommon = Common
    load_config()
    if Common:
        return CommonList
    else:
        return SpecialList


def UpdateConfig(changeList):
    load_config()
    new_dict = {}
    updateName = 'CommonList'
    if IsCommon:
        new_dict["common"] = changeList
        new_dict["special"] = SpecialList
        # print('Common'+str(changeList))
    else:
        new_dict["common"] = CommonList
        new_dict["special"] = changeList
        updateName = 'SpecialList'
        # print('Special' + str(changeList))

    with open(config_path, 'w')as f:
        json.dump(new_dict, f)
    return f'更新了{updateName}'


app.on("create", on_create)
app.run()
