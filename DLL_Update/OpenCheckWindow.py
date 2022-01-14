# coding:gbk
import json
import os
import requests

DataList = []
config_path='./config/check_config.json'
Urlconfig_path='./config/url_config.json'


def initWindow():
    global DataList
    global UrlDic
    if os.path.exists(config_path):     # 加载配置表
        with open(config_path) as conf:
            load_config = json.load(conf)
            DataList = (list)(load_config)

    if os.path.exists(Urlconfig_path):    # 加载接口配置
        with open(Urlconfig_path) as conf:
            load_config = json.load(conf)
            UrlDic = (dict)(load_config)
    return DataList, UrlDic


def SaveDataList(DList):
    global DataList
    DataList = DList
    with open(config_path, 'w')as f:
        json.dump(DataList, f)

Result=[]
def SendRequest(NeedList):
    urlList = {
        "Packages": {
            "test": "http://10.11.82.77:8787/resource/download/project/file",
            "formal": "http://10.11.11.61/resource/download/project/file",
        },
        "Rule": {
            "test": "http://10.11.66.233/v1/api/download/project/update/file",
            "formal": "http://10.11.82.74/v1/api/download/project/update/file",
        }
    }
    for item in NeedList:
        url = ''
        if item["Belong"] == "Test-Package":
            url = urlList["Packages"]["test"]
        elif item["Belong"] == "Test-Rule":
            url = urlList["Rule"]["test"]
        elif item["Belong"] == "Formal-Package":
            url = urlList["Packages"]["formal"]
        elif item["Belong"] == "Formal-Rule":
            url = urlList["Rule"]["formal"]
        payload={
            "appKey": item["appKey"],
            "engineVersion": item["Unity_Version"]
        }
        response = requests.post(url, data=payload)       # 输出response.json()

        # 查询结果存储
        Result.append({f"{item['appKey']}":{
            response
        }})
    print(Result)




