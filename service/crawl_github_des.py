import os
import json
import pickle
from posix import listdir
import time
import sys
import logging
import random

import requests


class GithubDesCrawler(object):
    def __init__(self):
        self.repo_name = ""
        self.user_name = ""
    
    def Request(self, url, retry=5):
        header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
            "Authorization":"token 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",
            "Content-Type":"application/json",
            "Accept":"application/vnd.github.mercy-preview+json"
        }
        judge = 1
        while judge:
            try:
                response = requests.get(url, headers=header)
                i = 0
                # print(response.status_code)
                while response.status_code != 200 and i < retry:
                    time.sleep(random.randint(5, 10))
                    response = requests.get(url, headers=header)
                    i += 1
                judge = 0
            except:
                # print(response.status_code)
                # sys.exit()

                time.sleep(random.randint(5, 10))

        if response.status_code != 200:
            return False, None
        return True, response.json()
    
    def crawl(self):
        github_url = "https://api.github.com/repos/{}/{}".format(self.user_name, self.repo_name)

        succeed, response = self.Request(github_url)
        if not succeed:
            print("Crawling {}({}) failed".format(self.user_name, self.repo_name))
            return ""
        if isinstance(response, dict):
            description = response.get("description", "")
            return description
        
        return ""

    def config(self, repo_name, user_name):
        self.repo_name = repo_name
        self.user_name = user_name

crawler = GithubDesCrawler()
def start_crawl(data_dir, save_file):
    f  = open(save_file, "a+", encoding="utf-8")
    crawled_filenames = set()
    for sub_dir in os.listdir(data_dir):
        curr_dir = os.path.join(data_dir, sub_dir)
        if not os.path.isdir(curr_dir):
            continue
        if sub_dir == ".DS_store":
            continue

        for filename in os.listdir(curr_dir):
            if filename in crawled_filenames:
                continue
            user_name, repo_name = filename[:-4].split(",")
            logger.info("Start Finishing crawling {}({})".format(user_name, repo_name))
            crawler.config(repo_name, user_name)
            description = crawler.crawl()
            crawled_filenames.add(filename)

            f.write("{}\t{}\n".format(filename, description))

def crawl_for_test(data_dir, save_file):
    outf = open(save_file, "a+", encoding="utf-8")
    crawled_filenames = set()
    for sub_dir_1 in os.listdir(data_dir): # 2020 
        # print(sub_dir_1)
        curr_dir_1 = os.path.join(data_dir, sub_dir_1) 
        for sub_dir_2 in os.listdir(curr_dir_1): # c
            # print(sub_dir_2)
            curr_dir_2 = os.path.join(curr_dir_1, sub_dir_2)
            for sub_dir_3 in os.listdir(curr_dir_2): # atc1441-ATC_MiThe
                # print(sub_dir_3)
                curr_dir3 = os.path.join(curr_dir_2, sub_dir_3)
                if not os.path.isdir(curr_dir3):
                    continue
                for sub_dir4 in os.listdir(curr_dir3):
                    curr_dir = os.path.join(curr_dir3, sub_dir4)
                    if not os.path.isdir(curr_dir):
                        continue
                    for filename in os.listdir(curr_dir):
                        # print(filename)
                        # print(curr_dir, filename, sep="//")
                        # break
                        splits = filename.strip()[:-4].split("+")
                        if len(splits) < 2:
                            continue
                        user_name, repo_name = splits[0], splits[1]
                        if repo_name in crawled_filenames:
                            continue
                        logger.info("Start Finishing crawling {}({})".format(user_name, repo_name))
                        crawler.config(repo_name, user_name)
                        description = crawler.crawl()
                        crawled_filenames.add(repo_name)

                        outf.write("{}+{}\t{}\n".format(user_name, repo_name, description))
    outf.close()

def correct(data_dir):
    filenames = []
    for sub_dir_1 in os.listdir(data_dir): # 2020 
        # print(sub_dir_1)
        curr_dir_1 = os.path.join(data_dir, sub_dir_1) 
        for sub_dir_2 in os.listdir(curr_dir_1): # c
            # print(sub_dir_2)
            curr_dir_2 = os.path.join(curr_dir_1, sub_dir_2)
            for sub_dir_3 in os.listdir(curr_dir_2): # atc1441-ATC_MiThe
                # print(sub_dir_3)
                curr_dir3 = os.path.join(curr_dir_2, sub_dir_3)
                if not os.path.isdir(curr_dir3):
                    continue
                for sub_dir4 in os.listdir(curr_dir3):
                    curr_dir = os.path.join(curr_dir3, sub_dir4)
                    if not os.path.isdir(curr_dir):
                        continue
                    for filename in os.listdir(curr_dir):
                        filenames.append(os.path.join(curr_dir, filename))
    print(len(filenames))
    with open("dst.pkl", "wb") as f:
        pickle.dump(filenames, f)

def test():
    gd = GithubDesCrawler()
    gd.config("remix", "remix-run")
    gd.Request("https://api.github.com/repos/remix-run/remix")

if __name__ == "__main__":
    # correct("./history")
    # crawl_for_test("./history", "./repo_des/test_repo_description_part2.txt")
    test()

