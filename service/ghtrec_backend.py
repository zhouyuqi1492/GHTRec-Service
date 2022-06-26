from flask import Flask, jsonify, render_template, request
from flask_cors import cross_origin, CORS
from user_topic_preference import User
import time
import pymongo

app = Flask(__name__)
CORS(app, resources=r'/*')

@app.route('/_gen_topic_preferences')
@cross_origin()
def gen_topic_preferences():
    username = request.args.get('username')
    print('starting generate user topic preferences...'+username)
    # 调用User类自动生成topic preference
    user = User(username)
    user_topic_preferences = user.cal_user_preference()
    print('用户' + username + '的主题偏好计算得到：', user_topic_preferences)
    return jsonify(result=user_topic_preferences)

@app.route('/_gen_recommendation')
@cross_origin()
def gen_recommendation():
    arg_tp_str = request.args.get('topic_preferences')
    usr_topic_preferences = arg_tp_str.split(',')
    today = time.strftime("%Y%m%d", time.localtime())
    # 生成 不同范围内的日期 (取出最大的1,3,7天)
    r1 = recommendation(usr_topic_preferences, 1)
    for i in range(len(r1)):
        r1[i].pop("_id")
    r3 = recommendation(usr_topic_preferences, 3)
    for i in range(len(r3)):
        r3[i].pop("_id")
    r7 = recommendation(usr_topic_preferences, 7)
    for i in range(len(r7)):
        r7[i].pop("_id")
    print([repo['repo_name'] for repo in r1])
    print([repo['repo_name'] for repo in r3])
    # r1 = [ 'Asabeneh/30-Days-Of-Python','EleutherAI/gpt-neo', 'Zero-S1/JD_tools', 'opencve/opencve', 'THUMNLab/AutoGL', 'owid/covid-19-data', 'sherlock-project/sherlock', 'mingrammer/diagrams', 'jrieke/traingenerator', 'donnemartin/system-design-primer', 'bitcoinbook/bitcoinbook', 'machin3io/MACHIN3tools',  'jerry3747/taobao_seckill', 'bregman-arie/devops-exercises', 'back8/github_huanghyw_jd_seckill', 'onelivesleft/PrettyErrors', 'QUANTAXIS/QUANTAXIS', 'microsoft/AI-System', 'mxrch/GHunt', 'AlexxIT/SonoffLAN', 'PiotrMachowski/Xiaomi-cloud-tokens-extractor', 'pythonstock/stock', 'alexschimpf/Snkrs-Bot', '3b1b/manim']
    # r3 = ['SleepyBag/Statistical-Learning-Methods', 'Asabeneh/30-Days-Of-Python','SleepyBag/Statistical-Lea7rning-Methods', 'QUANTAXIS/QUANTAXIS','owid/covid-19-data', 'sherlock-project/sherlock', 'mingrammer/diagrams', 'EleutherAI/gpt-neo', 'raspberrypi/documentation', 'onelivesleft/PrettyErrors', 'kholia/OSX-KVM', 'alexschimpf/Snkrs-Bot', 'QingdaoU/OnlineJudge', 'microsoft/AI-System', 'AlexxIT/SonoffLAN', 'Endermanch/MalwareDatabase', 'bitcoinbook/bitcoinbook', 'tasmota/tasmotizer', 'jrieke/traingenerator', '3b1b/videos', 'back8/github_huanghyw_jd_seckill', 'THUMNLab/AutoGL', 'onelivesleft/PrettyErrors', 'QUANTAXIS/QUANTAXIS','machin3io/MACHIN3tools']
    # r7 = ['SleepyBag/Statistical-Learning-Methods', 'mxrch/GHunt','Asabeneh/30-Days-Of-Python', 'Endermanch/MalwareDatabase', 'boston-dynamics/spot-sdk', '3b1b/videos', 'donnemartin/system-design-primer','EleutherAI/gpt-neo', 'raspberrypi/documentation', 'onelivesleft/PrettyErrors', 'kholia/OSX-KVM', 'alexschimpf/Snkrs-Bot', 'QingdaoU/OnlineJudge', 'microsoft/AI-System', 'AlexxIT/SonoffLAN', 'Endermanch/MalwareDatabase', 'bitcoinbook/bitcoinbook', 'tasmota/tasmotizer', 'jrieke/traingenerator', '3b1b/videos', 'back8/github_huanghyw_jd_seckill', 'THUMNLab/AutoGL', 'tychxn/jd-assistant', 'pythonstock/stock', 'machin3io/MACHIN3tools']
    return jsonify(r1 = r1, r3=r3, r7=r7) 

@app.route('/')
@cross_origin()
def index():
    return "这是GHTRec服务的后台"

def recommendation(usr_topic_preferences, dates_length):
    myclient = pymongo.MongoClient('mongodb://localhost:27017/')
    db = myclient['GHTRec_Service']
    collist = db.collection_names()
    collist_sorted = sorted(collist, reverse=True)
    dates = collist_sorted[:dates_length]
    recommendation_res = []
    repo_collection = []
    repo_fullname = []
    for date in dates:
        col = db[date]
        for repo in col.find():
            # 去重
            if repo['repo_owner']+'/'+repo['repo_name'] in repo_fullname:
                continue
            repo_collection.append(repo)
            repo_fullname.append(repo['repo_owner']+'/'+repo['repo_name'])
    # idx2sims
    repo_sims = {}
    for i in range(len(repo_collection)):
        current_topic_preferences = repo_collection[i]['topic_preferences']
        sim = 0
        for j in range(len(current_topic_preferences)):
            if current_topic_preferences[j] == 1 and  usr_topic_preferences[j] == '1':
                sim += 1
        repo_sims[i] = sim
    # 排序
    repo_sims_sorted = sorted(repo_sims.items(), key = lambda x:x[1], reverse = True)
    for item in repo_sims_sorted[:25]:
        recommendation_res.append(repo_collection[item[0]])

    return recommendation_res
