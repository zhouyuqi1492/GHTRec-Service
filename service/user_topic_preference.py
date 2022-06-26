import base64
import re
import warnings
import pickle
import json

import requests
from bs4 import BeautifulSoup

from readmeModule import repoCrawler
from crawl_github_des import GithubDesCrawler
from repo_topic_preference import Repo_Topic_Preferences

warnings.filterwarnings("ignore")
requests.adapters.DEFAULT_RETRIES = 5
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743/116 Safari/537.36',
    'Cookies': '__cfduid=d2a32448bf3044b5601341e7ef483a5691596878931; cf_clearance=c3ae9d1a244860d6dea39773410ef476926c61e5-1596878889-0-1z3a30315zecc1f62ez2f94fc4a-250; MVN_SESSION=eyJhbGciOiJIUzI1NiJ9.eyJkYXRhIjp7InVpZCI6Ijc5MGQ4ZjcxLWQ5NTktMTFlYS05OTZlLTc1YmM1YTFkZjI1ZCJ9LCJleHAiOjE2Mjg0MTUyODMsIm5iZiI6MTU5Njg3OTI4MywiaWF0IjoxNTk2ODc5MjgzfQ.JYcECQAXSISJshwhU9pd4HUwDu7B-lVkjxP9xzU2sv4; _ga=GA1.2.2073334969.1596878892; _gid=GA1.2.1778797561.1596878892; _gat=1'
}

# 设定一个user的数据结构
# userinfo = {
#     username;
#     repo_info = [
#         {
#             reponame;
#             readmetext;
#             destext;
#         }
#         ...
#     ]
# }


class User():
    def __init__(self, username):
        self.username = username
        self.history_repos = []
        self.get_public_repos()


    # 获取用户的仓库信息
    def get_public_repos(self):
        print('开始获取用户的基本数据: ', self.username)
        url_base = 'https://github.com/'
        judge = False
        url = url_base + self.username + '?tab=repositories&q=&type=public&language='
        judge = 1
        while judge:
            try:
                page = requests.get(url)
                judge = 0 
            except Exception as e:
                print(e)
                print('遭遇错误，休息10秒。。。。。。')
                time.sleep(10)
        soup = BeautifulSoup(page.text)
        try:
            repos_raw = [a.find('a').text for a in soup.find(id = 'user-repositories-list').find('ul').find_all(class_='wb-break-all')]
        except:
            return False
        repos = []
        if len(repos_raw) < 3:
            return False

        for item in repos_raw:
            item = item.replace('\n', '').replace(' ','')
            repos.append(item)
        
        # 在这里设置数量
        count = 0
        for repo in repos:
            repo_info = {}
            rmcontent = repoCrawler('trending_data/user_readme/').readmeServiceCrawler(repo, self.username)
            if rmcontent == False:
                continue
            else:
                if len(rmcontent)>200:
                    crawler = GithubDesCrawler()
                    crawler.config(repo, self.username)
                    description = crawler.crawl()
                    # 构建存储用户历史仓库的数据结构
                    repo_info['repo_name'] = repo
                    repo_info['readme_text'] = rmcontent
                    repo_info['des_text'] = description
                    self.history_repos.append(repo_info)
                    count += 1
                    # 合格的readme的数量
                    if count ==3:
                        break
                else:
                    continue
        return judge


    # 计算仓库的topic preference
    def cal_user_preference(self):
        print('start calculating user preferences...')
        repos_topic_preferences = []
        for repo in self.history_repos:
            print('start calculating '+repo['repo_name']+' topic preferences...')
            topic_preference = Repo_Topic_Preferences(repo['readme_text'], repo['des_text']).cal_topic_preferences()
            repos_topic_preferences.append(topic_preference)
        # 历史仓库的topic preference整合成用户的topic preference
        LABEL_IDX_PATH = "./files/label2idx.json"
        user_topic_preferences = [0 for x in range(134)]
        with open(LABEL_IDX_PATH, "r", encoding="utf-8") as f:
            label2idx = json.load(f)
        for repo_res in repos_topic_preferences:
            for item in repo_res:
                user_topic_preferences[label2idx[item[0]]] = 1
        return user_topic_preferences


