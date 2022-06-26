const DEBUG = false;

function getUserInfo() {
  let metas = document.querySelectorAll("head > meta");
  let username = ""
  for (let meta of metas) {
    if (meta.name === "user-login") {
      username = meta.content;
      break;
    }
  }
  return username;
}

const getUsernameTimer = setInterval(() => {
  let username = getUserInfo();
  if (username !== "") {
    if (DEBUG) {
      console.log("[MainPage] Get username: ", username)
    }
    chrome.runtime.sendMessage({ type: "UpdateUserInfo", content: username });
    clearInterval(getUsernameTimer);
  }
}, 1000 * 1);