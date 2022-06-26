# ****************************************
# 2021.5
# 本程序用于抓取github trending历史页面的仓库页面的仓库, 维护一个数据集池子，定期更新mongodb里面的内容
# 目标 2021年的trending的每天的总页面/常见编程语言的页面+每天能收集到的月trending页面/常见编程语言的月热度
# ****************************************

from typing import Pattern
from urllib import request
import requests
from bs4 import BeautifulSoup
import json
import chardet
import time
import os
import pymongo
import base64
import re
import warnings
import pickle
import datetime

from readmeModule import repoCrawler
from crawl_github_des import GithubDesCrawler
from repo_topic_preference import Repo_Topic_Preferences
from bert_test_for_asentence import test
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
warnings.filterwarnings("ignore")
requests.adapters.DEFAULT_RETRIES = 5
headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743/116 Safari/537.36',
            'Cookies': '__cfduid=d2a32448bf3044b5601341e7ef483a5691596878931; cf_clearance=c3ae9d1a244860d6dea39773410ef476926c61e5-1596878889-0-1z3a30315zecc1f62ez2f94fc4a-250; MVN_SESSION=eyJhbGciOiJIUzI1NiJ9.eyJkYXRhIjp7InVpZCI6Ijc5MGQ4ZjcxLWQ5NTktMTFlYS05OTZlLTc1YmM1YTFkZjI1ZCJ9LCJleHAiOjE2Mjg0MTUyODMsIm5iZiI6MTU5Njg3OTI4MywiaWF0IjoxNTk2ODc5MjgzfQ.JYcECQAXSISJshwhU9pd4HUwDu7B-lVkjxP9xzU2sv4; _ga=GA1.2.2073334969.1596878892; _gid=GA1.2.1778797561.1596878892; _gat=1'
}

class trendingCrawler():
    def __init__(self, date_specify = ''):
        if date_specify != '':
            today = date_specify
        else:
            today = time.strftime("%Y%m%d", time.localtime()) 
        self.trending_page_crawler(today)

    def trending_page_crawler(self, today):
        myclient = pymongo.MongoClient('mongodb://localhost:27017/')
        db = myclient['GHTRec_Service']
        collist = db.collection_names()
        lans = ['', 'python', 'java', 'javascript', 'c', 'go']
        collection = db[today]
        url =  'https://web.archive.org/web/' + today + '/https://github.com/trending'
        url_redirect = request.urlopen(url).geturl()
        pattern = '/(\d+)/'
        today = re.search(pattern, url_redirect).group(1)[:8]
        if today in collist:
            print('该日期已存在...no need to update...')
            return 0
        else:
            # 增加语言后
            for lan in lans:
                if lan == '':
                    url_update = url_redirect
                else:
                    url_update = url_redirect + '/' + lan + '?since=daily'
                judge = 1
                print('---------------------------------')
                print('开始爬取: ', url_update)
                while judge:
                    try:
                        res = requests.get(url_update)
                        judge = 0
                    except Exception as e:
                        print(e)
                        print('遭遇错误，休息10秒。。。。。。')
                        time.sleep(10)
                soup = BeautifulSoup(res.text, 'lxml')
                rows = soup.find_all(class_ = 'Box-row')
                full_names = []
                for row in rows:
                    href = row.find('h1').find('a').get('href')
                    print('---------------------------------')
                    print(href)
                    trending_repo = {}
                    repo_owner = href.split('/')[-2]    #
                    repo_name = href.split('/')[-1]     #
                    repo_fullname = repo_owner + '/' + repo_name    #
                    # 调用github api获取repo的基本信息
                    url_info = 'https://api.github.com/repos/' + repo_fullname
                    s = requests.Session()
                    s.keep_alive = False 
                    s.auth = ('a373f96e9ee213497383', '30f0dec3fa4b22555e05b55c78da42cbaebfebdb')
                    res = s.get(url_info, headers = headers, verify = False)
                    repo_info = json.loads(res.text)
                    repocrawler = repoCrawler()
                    repo_readme, err = repocrawler.readmeServiceCrawler(repo_info['html_url'], repo_info['full_name'])
                    if err!=None:
                        print('no readme...')
                        continue
                    crawler = GithubDesCrawler()
                    crawler.config(repo_name, repo_owner)
                    repo_des = crawler.crawl()
                    if repo_des == "":
                        print('no description...')
                        continue
                    # 创建mongodb的document
                    trending_repo['repo_owner'] = repo_owner
                    trending_repo['repo_name'] = repo_name
                    trending_repo['repo_info'] = repo_info
                    trending_repo['repo_readme'] = repo_readme
                    trending_repo['repo_des'] = repo_des
                    # try: 
                    #     if trending_repo['repo_des'] == None and trending_repo['repo_readme'] != None:
                    #         text = trending_repo['repo_readme']
                    #     elif trending_repo['repo_des'] != None and trending_repo['repo_readme'] == None:
                    #         text = trending_repo['repo_des']
                    #     elif trending_repo['repo_des'] == None and trending_repo['repo_readme'] == None:
                    #         continue
                    #     else:
                    #         text = trending_repo['repo_des'] + trending_repo['repo_readme']
                    # except Exception as e:
                    #     print(today + lan + repo_name + ':', e)
                    #     continue
                    # try:
                    #     prediction = test(text)
                    #     LABEL_IDX_PATH = "./files/label2idx.json"
                    #     user_topic_preferences = [0 for x in range(134)]
                    #     with open(LABEL_IDX_PATH, "r", encoding="utf-8") as f:
                    #         label2idx = json.load(f)

                    #     for item in prediction:
                    #         user_topic_preferences[label2idx[item[0]]] = 1
                    #     trending_repo['topic_preferences'] = user_topic_preferences
                    # except Exception as e:
                    #     print(today + lan + repo_name + ':', e)
                    #     continue
                    collection.insert_one(trending_repo)
                    print('collect repo success...')


def gen_dates(recent = 7):
    dates = []
    today = datetime.date.today()
    while recent!=0:
        dates.append(str(today).replace('-', ''))
        recent -= 1
        today = today - datetime.timedelta(days=1)
    return dates

def cal_topic_preference():
    myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    db = myclient['GHTRec_Service']
    collist = db.collection_names()
    for col in collist:
        items = db[col].find({}, no_cursor_timeout = True)
        for item in items:
            keys = item.keys()
            keys = list(keys)
            if 'topic_preferences' in keys:
                print('{} has already updated...'.format(item['repo_name']))
                continue
            # 更新数据
            des_text = item['repo_des']
            readme_text = item['repo_readme']
            if des_text == None and readme_text != None:
                text = readme_text
            elif des_text != None and readme_text== None:
                text = des_text
            elif des_text == None and readme_text == None:
                continue
            else:
                text = des_text+readme_text
            prediction = test(text)
            LABEL_IDX_PATH = "./files/label2idx.json"
            user_topic_preferences = [0 for x in range(134)]
            with open(LABEL_IDX_PATH, "r", encoding="utf-8") as f:
                label2idx = json.load(f)
            for mark in prediction:
                user_topic_preferences[label2idx[mark[0]]] = 1
            db[col].update({'_id':item['_id']}, { "$set": { "topic_preferences": user_topic_preferences } })
            print('update {} success...'.format(item['repo_name']))


def crawl_single_trending_page(url):
    myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    db = myclient['GHTRec_Service']
    collist = db.collection_names()
    lans = ['', 'python', 'java', 'javascript', 'c', 'go']
    pattern = '/(\d+)/'
    today = re.search(pattern, url).group(1)[:8]
    collection = db[today]
    if today in collist:
        print('该日期已存在...no need to update...')
        return 0
    else:
        # 增加语言后
        for lan in lans:
            if lan == '':
                url_update = url
            else:
                url_update = url + '/' + lan + '?since=daily'
            judge = 1
            print('---------------------------------')
            print('开始爬取: ', url_update)
            while judge:
                try:
                    res = requests.get(url_update)
                    judge = 0
                except Exception as e:
                    print(e)
                    print('遭遇错误，休息10秒。。。。。。')
                    time.sleep(10)
            soup = BeautifulSoup(res.text, 'lxml')
            rows = soup.find_all(class_ = 'Box-row')
            full_names = []
            for row in rows:
                href = row.find('h1').find('a').get('href')
                print('---------------------------------')
                print(href)
                trending_repo = {}
                repo_owner = href.split('/')[-2]    #
                repo_name = href.split('/')[-1]     #
                repo_fullname = repo_owner + '/' + repo_name    #
                # 调用github api获取repo的基本信息
                url_info = 'https://api.github.com/repos/' + repo_fullname
                s = requests.Session()
                s.keep_alive = False 
                s.auth = ('a373f96e9ee213497383', '30f0dec3fa4b22555e05b55c78da42cbaebfebdb')
                res = s.get(url_info, headers = headers, verify = False)
                repo_info = json.loads(res.text)
                repocrawler = repoCrawler()
                try:
                    repo_readme, err = repocrawler.readmeServiceCrawler(repo_info['html_url'], repo_info['full_name'])
                except Exception as e:
                    print(e)
                    continue
                if err!=None:
                    print('no readme...')
                    continue
                crawler = GithubDesCrawler()
                crawler.config(repo_name, repo_owner)
                repo_des = crawler.crawl()
                if repo_des == "":
                    print('no description...')
                    continue
                # 创建mongodb的document
                trending_repo['repo_owner'] = repo_owner
                trending_repo['repo_name'] = repo_name
                trending_repo['repo_info'] = repo_info
                trending_repo['repo_readme'] = repo_readme
                trending_repo['repo_des'] = repo_des
                collection.insert_one(trending_repo)
                print('collect repo success...')


if __name__ == '__main__':
    # res = requests.get('https://web.archive.org/web/20210519/https://github.com/trending')
    # print(res.url)
    # dates = gen_dates(7)
    # for date in dates:
    #     trendingCrawler(date)
    cal_topic_preference()
    # crawl_single_trending_page('https://web.archive.org/web/20211123000036/https://github.com/trending')