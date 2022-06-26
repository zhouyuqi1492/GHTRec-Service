const SERVER_IP = "162.105.16.46:3001"
const DEBUG = true

chrome.storage.local.get(["username"], (result) => {
  if (DEBUG) console.log("[PopupPage] Init username: ", result);
  if (result.username != "") {
    changeUserLogin(result.username);
  }
});

chrome.storage.local.get(["preferTopics"], (result) => {
  if (DEBUG) console.log("[PopupPage] Init preferTopics", result.preferTopics);
  changePreferTopics(result.preferTopics);
});

chrome.storage.local.get(["daysetting"], (result) => {
  if (DEBUG) console.log("[PopupPage] Init daysetting", result.daysetting);
  if (result.daysetting == 1) {
    daysettingButton1Listener();
  } else if (result.daysetting == 3) {
    daysettingButton2Listener();
  } else if (result.daysetting == 7) {
    daysettingButton3Listener();
  }
});

// 监听本地存储发生改变
chrome.storage.onChanged.addListener(function (changes, namespace) {
  for (let [key, { oldValue, newValue }] of Object.entries(changes)) {
    console.log(`[Popup] Value of ${key} changed from ${oldValue} to ${newValue}`);
    if (key === "username") {
      changeUserLogin(newValue);
    } else if (key === "preferTopics") {
      changePreferTopics(newValue);
    }
  }
});

// 天数设置监听
document.querySelector("body > div > div:nth-child(3) > div.btn-group > button").addEventListener("click", daysettingButton1Listener);
document.querySelector("body > div > div:nth-child(3) > div.btn-group > button:nth-child(2)").addEventListener("click", daysettingButton2Listener);
document.querySelector("body > div > div:nth-child(3) > div.btn-group > button:nth-child(3)").addEventListener("click", daysettingButton3Listener);

// 生成偏好按钮监听
document.querySelector("body > div > div:nth-child(2) > div:nth-child(2) > button").addEventListener("click", async () => {
  let username = await readLocalStorage("username")
  let url = "http://" + SERVER_IP + "/generate_topic_preference?username=" + username
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
    throw new Error("Request to", url, "failed")
  })
  .then((result) => {
    if (!result.success) {
      return;
    }
    if (DEBUG) console.log("[PopupPage] Get response: ", JSON.stringify(result));
    chrome.storage.local.set({ preferTopics: result.preferTopics });
    chrome.storage.local.set({ preferTopicVector: result.preferTopicVector });
  })
  .catch((error) => {
    console.log(error);
  })
})

// 生成（刷新）推荐按钮监听
// document.querySelector("body > div > div:nth-child(4) > button")
document.querySelector("body > div > div:nth-child(4) > button").addEventListener("click", async () => {
  let preferTopicVector = await readLocalStorage("preferTopicVector");
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
    throw new Error("Request to", url, failed);
  })
  .then((result) => {
    if (DEBUG) console.log("[PopupPage] Get response: ", JSON.stringify(result));
    if (!result.success) {
      return;
    }
    chrome.storage.local.set({ recommend: result });
  })
  .catch((error) => {
    console.log(error);
  })
})

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

function changeUserLogin(username) {
  document.querySelector("body > div > div:nth-child(1) > div.user-login").innerHTML = "已登录账号";
  document.querySelector("body > div > div:nth-child(1) > div:nth-child(2)").innerHTML = username;
}

function changePreferTopics(preferTopics) {
  console.log("[changePreferTopics] called!");
  topicElements = document.getElementsByTagName("span");
  for (let i = 0; i < preferTopics.length; i++) {
    topicElements[i].innerHTML = preferTopics[i];
  }
  for (let i = preferTopics.length; i < 5; i++) {
    topicElements[i] = "...";
  }
}

function daysettingButton1Listener() {
  document.querySelector("body > div > div:nth-child(3) > div.btn-group > button:nth-child(2)").className = "btn button-default"
  document.querySelector("body > div > div:nth-child(3) > div.btn-group > button:nth-child(3)").className = "btn button-default"
  document.querySelector("body > div > div:nth-child(3) > div.btn-group > button").className = "btn button-default selected"
  chrome.storage.local.set({ daysetting: 1 });
}

function daysettingButton2Listener() {
  document.querySelector("body > div > div:nth-child(3) > div.btn-group > button").className = "btn button-default"
  document.querySelector("body > div > div:nth-child(3) > div.btn-group > button:nth-child(3)").className = "btn button-default"
  document.querySelector("body > div > div:nth-child(3) > div.btn-group > button:nth-child(2)").className = "btn button-default selected"
  chrome.storage.local.set({ daysetting: 3 });
}

function daysettingButton3Listener() {
  document.querySelector("body > div > div:nth-child(3) > div.btn-group > button:nth-child(2)").className = "btn button-default"
  document.querySelector("body > div > div:nth-child(3) > div.btn-group > button").className = "btn button-default"
  document.querySelector("body > div > div:nth-child(3) > div.btn-group > button:nth-child(3)").className = "btn button-default selected"
  chrome.storage.local.set({ daysetting: 7 });
}

