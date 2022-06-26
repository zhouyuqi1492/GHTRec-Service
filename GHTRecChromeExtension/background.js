/**
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
const SERVER_IP = "162.105.16.46";
const DEBUG = true;

let recommends = {
  r1: [],
  r3: [],
  r7: []
};
let daysetting = 1;
let preferTopics = [];
let preferTopicVector = [];
let username = "";


const debugTimer = setInterval(() => {
  console.log("username", username);
  console.log("daysetting", daysetting);
  console.log("preferTopics", preferTopics);
  console.log("preferTopicVector", preferTopicVector);
  console.log("recommends", recommends);
}, 1000 * 10);

// 更新用户的topic vector
const updateTopicTimer = setInterval(() => {
  if (DEBUG || (date.getHours() === 23 && username !== "")) {
    let url = "http://" + SERVER_IP + ":3001/generate_topic_preference?username=" + username;
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
      updatePreferTopics(result.preferTopics, result.preferTopicVector);
    })
    .catch((error) => {
      console.log(error);
    });
  }
}, 1000 * 10);


const updateRecommendTimer = setInterval(() => {
  if (DEBUG || (date.getHours() <= 3 && preferTopicVector.length !== 0)) {
    let url = "http://" + SERVER_IP + ":3001/generate_recommend?topic_preferences=" + JSON.stringify(preferTopicVector);
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
      updateRecommends(result);
    })
    .catch((error) => {
      console.log(error);
    });
  }
}, 1000 * 10);

function updatePreferTopics(newTopics, newTopicVector) {
  // if (username === "") return;
  if (!newTopics instanceof Array) {
    return;
  }
  if (JSON.stringify(newTopics) === JSON.stringify(preferTopics)) {
    // clearInterval(updateTopicTimer);
    return;
  }
  
  // preferTopics.length = newTopics.length;
  // for (let i = 0; i < newTopics.length; i++) {
  //   preferTopics[i] = newTopics[i];
  // }
  // preferTopicVector = newTopicVector;

  // 持久化结果
  chrome.storage.local.set({ preferTopics: newTopics });
  chrome.storage.local.set({ preferTopicVector: newTopicVector });
}


function updateRecommends(newRecommends) {
  // if (username === "") {
  //   return;
  // }

  // recommends.r1 = newRecommends.r1;
  // recommends.r3 = newRecommends.r3;
  // recommends.r7 = newRecommends.r7;
  
  // 持久化结果
  chrome.storage.local.set({ recommends: newRecommends });
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
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (tab.url.startsWith("https://github.com/trending")) {
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
      // username = request.content;
      chrome.storage.local.set({ username: request.content });
    }
  }
);

// 监听本地存储发生改变
chrome.storage.onChanged.addListener((changes, namespace) => {
  for (let [key, { oldValue, newValue }] of Object.entries(changes)) {
    if (DEBUG) console.log(`[Background] Value of ${key} changed from ${oldValue} to ${newValue}`);
    if (key === "daysetting") {
      daysetting = newValue;
      // if (newValue == 1) {
      //   chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      //     let message = {
      //       type: "UpdateRecommendContent",
      //       content: recommend["r1"]
      //     }
      //     chrome.tabs.sendMessage(tabs[0].id, message);
      //   })
      // } else if (newValue == 3) {
      //   chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      //     let message = {
      //       type: "UpdateRecommendContent",
      //       content: recommend["r3"]
      //     }
      //     chrome.tabs.sendMessage(tabs[0].id, message);
      //   })
      // } else if (newValue == 7) {
      //   chrome.tabs.query({ active: true, currentWindow: true }, function (tabs) {
      //     let message = {
      //       type: "UpdateRecommendContent",
      //       content: recommend["r7"]
      //     }
      //     chrome.tabs.sendMessage(tabs[0].id, message);
      //   })
      // }
    } else if (key === "recommends") {
      recommends = newValue;
    } else if (key === "username") {
      username = newValue;
    } else if (key === "preferTopics") {
      if (! newValue instanceof Array) {
        continue;
      }
      preferTopics.length = newValue.length;
      for (let i = 0; i < newValue.length; i++) {
        preferTopics[i] = newValue[i];
      }
    } else if (key === "preferTopicVector") {
      preferTopicVector = newValue;
    }
  }
});
