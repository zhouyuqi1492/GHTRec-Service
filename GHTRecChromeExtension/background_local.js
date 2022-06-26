/**
 * 这个版本的内容为backgroound脚本只在localstorage的实现
 * local storage存储的内容为 
 * {
 *  "daysetting": Integer,
 *  "preferTopics": Array[Integer],
 *  "username": String,
 *  "recommends": {
 *    "r1": Array[object],
 *    "r3": Array[object],
 *    "r7": Array[object],
 *  },
 *  "preferTopicVector": [] // not used!
 * }
 */

const date = new Date();
const SERVER_IP = "162.105.16.46:3001";
const DEBUG = true;

async function readLocalStorage(key) {
  return new Promise((resolve, reject) => {
    chrome.storage.local.get([key], function(result) {
      if (result[key] != undefined) {
        resolve(result[key]);
      } else {
        reject();
      }
    });
  })
}

// 更新用户的topic vector
const updateTopicTimer = setInterval(async () => {
  if (DEBUG || date.getHours() === 23) {
    let username = await readLocalStorage("username");
    if (username === "") return;
    if (DEBUG) console.log("[Background] GET username: ", username);
    let url = "http://" + SERVER_IP + "/generate_topic_preference?username=" + username;
    fetch(url, {
      method: 'GET',
      headers: new Headers({
        "Accept": "application/json; charset=utf-8"
      })
    })
      .then((response) => {
        if (response.ok) {
          return response.json();
        }
        throw new Error("Request Failed");
      })
      .then((result) => {
        if (!result.success) {
          return;
        }
        updatePreferTopics(result.preferTopics, result.preferTopicVector);
      })
      .catch((error) => {
        console.log(error);
      });
  }
}, 1000 * 10);


const updateRecommendTimer = setInterval(async () => {
  if (DEBUG || date.getHours() <= 3) {
    let preferTopicVector = await readLocalStorage("preferTopicVector");
    if (preferTopicVector.length === 0) return;
    if (DEBUG) console.log("[Background] GET preferTopicVector: ", preferTopicVector);
    let url = "http://" + SERVER_IP + "/generate_recommend?topic_preferences=" + JSON.stringify(preferTopicVector);
    fetch(url, {
      method: 'GET',
      headers: new Headers({
        "Accept": "application/json; charset=utf-8"
      })
    })
      .then((response) => {
        if (response.ok) {
          return response.json();
        }
        throw new Error("Request Failed");
      })
      .then((result) => {
        if (!result.success) {
          return;
        }
        updateRecommends(result);
      })
      .catch((error) => {
        console.log(error);
      });
  }
}, 1000 * 10);

function updatePreferTopics(newTopics, newTopicVector) {
  if (!newTopics instanceof Array) {
    return;
  }

  // 持久化结果
  chrome.storage.local.set({ preferTopics: newTopics });
  chrome.storage.local.set({ preferTopicVector: newTopicVector });

  if (DEBUG) clearInterval(updateTopicTimer);
}


function updateRecommends(newRecommends) {
  chrome.storage.local.set({ recommends: newRecommends });
  if (DEBUG) clearInterval(updateRecommendTimer);
}


// 插件安装时
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({
    username: "",
    preferTopics: [],
    preferTopicVector: [],
    recommends: {
      r1: [],
      r3: [],
      r7: [],
    },
    daysetting: 1,
  });
  console.log("欢迎安装GHTRec谷歌插件服务");
})

// 推送推荐仓库列表信息
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (tab.url.startsWith("https://github.com/trending")) {
    let recommends = await readLocalStorage("recommends");
    let daysetting = await readLocalStorage("daysetting");
    let message = {
      type: "UpdateRecommendContent",
      content: recommends[`r${daysetting}`]
    };
    chrome.tabs.sendMessage(tabId, message);
  }
});

// 监听主页面的新用户登陆
chrome.runtime.onMessage.addListener(
  function (request, sender) {
    if (request.type === "UpdateUserInfo") {
      chrome.storage.local.set({ username: request.content });
    }
  }
);

