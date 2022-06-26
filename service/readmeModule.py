# ****************************************
# 2020.12
# 本程序用于对仓库的readme文件的判断和获取
# ****************************************

import requests
from bs4 import BeautifulSoup
import json
import chardet
import time
import os
import base64
import re
import warnings
warnings.filterwarnings("ignore")
requests.adapters.DEFAULT_RETRIES = 5
headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743/116 Safari/537.36',
            'Cookies': '__cfduid=d2a32448bf3044b5601341e7ef483a5691596878931; cf_clearance=c3ae9d1a244860d6dea39773410ef476926c61e5-1596878889-0-1z3a30315zecc1f62ez2f94fc4a-250; MVN_SESSION=eyJhbGciOiJIUzI1NiJ9.eyJkYXRhIjp7InVpZCI6Ijc5MGQ4ZjcxLWQ5NTktMTFlYS05OTZlLTc1YmM1YTFkZjI1ZCJ9LCJleHAiOjE2Mjg0MTUyODMsIm5iZiI6MTU5Njg3OTI4MywiaWF0IjoxNTk2ODc5MjgzfQ.JYcECQAXSISJshwhU9pd4HUwDu7B-lVkjxP9xzU2sv4; _ga=GA1.2.2073334969.1596878892; _gid=GA1.2.1778797561.1596878892; _gat=1'
        }

class repoCrawler():
    def __init__(self, path="", url_repo = 'https://api.github.com/repos/'):
        self.path = path
        self.url_repo = url_repo  # 使用在readMongoRepo中

    def getRepoFileList(self, url = 'https://github.com/square/picasso' ):
        # 防止被封
        key = 1
        while key == 1:
            try:
                s = requests.Session()
                s.keep_alive = False 
                res = s.get(url, headers = headers, verify = False)
                s.close()
                contents = res.content
                key = 0
            except Exception as e:
                print(e)

        # html解析
        soup = BeautifulSoup(contents, 'lxml')
        #print(soup)
        # gain categories
        files_list = []
        files = soup.find(class_ = 'js-details-container Details').find_all(class_ = 'Box-row')
        #print(len(list(files)))
        for item in files:
            file_name = item.find(role = 'rowheader').find('span').find('a').text
            files_list.append(file_name)
        #print(files_list)
        return files_list

    def readmeServiceCrawler(self, url, full_name):
        err = None
        try:
            files_list = self.getRepoFileList(url)
            #print('https://github.com/' + repo, ' : ', files_list)
            if 'README.md' in files_list:
                repo_file = 'README.md'
            elif 'readme.txt' in files_list:
                repo_file = 'readme.txt'
            elif 'readme.md' in files_list:
                repo_file = 'readme.md'
            else:
                err = "readme not exist"
                return None, err
            print('读取readme ing......')
            file_url = self.url_repo + full_name +'/contents/'+repo_file
            print(file_url)
            # 防止爬虫被封
            key = 1
            while key == 1:
                try:
                    s = requests.Session()
                    s.keep_alive = False 
                    s.auth = ('a373f96e9ee213497383', '30f0dec3fa4b22555e05b55c78da42cbaebfebdb')
                    res = s.get(file_url, headers = headers, verify = False)
                    s.close()
                    key = 0
                except Exception as e:
                    print(e)
                    time.sleep(10)
            contents = res.content
            strings = contents.decode('utf-8')
            jsonarray = json.loads(strings)
            rmcontent_encoded = jsonarray['content']
            rmcontent = base64.b64decode(rmcontent_encoded).decode('utf-8')
            # 通过正则表达式去除其中的html标签
            pattern = re.compile(r'<[^>]+>',re.S)
            rmcontent = pattern.sub('', rmcontent)
            return rmcontent, None
        except Exception as e:
            err = "error in readmeServiceCrawler"
            print(e)
            return None, err


if __name__ == '__main__':
    t = repoCrawler()
    print(t.getRepoFileList())

        