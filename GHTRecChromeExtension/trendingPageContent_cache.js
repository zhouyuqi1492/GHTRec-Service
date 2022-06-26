const DEBUG = false;

let recs = [];
let personalized = false;

const focusedButtonColor = getComputedStyle(document.querySelector("a.js-selected-navigation-item.selected.subnav-item")).getPropertyValue('color')
const focusedButtonBackgroundColor = getComputedStyle(document.querySelector("a.js-selected-navigation-item.selected.subnav-item")).getPropertyValue('background-color')
const focusedButtonBorderColor = getComputedStyle(document.querySelector("a.js-selected-navigation-item.selected.subnav-item")).getPropertyValue('border-color')
const buttonColor = getComputedStyle(document.querySelector("a.js-selected-navigation-item.subnav-item:not(.selected)")).getPropertyValue('color')
const buttonBackgroundColor = getComputedStyle(document.querySelector("a.js-selected-navigation-item.subnav-item:not(.selected)")).getPropertyValue('background-color')
const buttonBorderColor = getComputedStyle(document.querySelector("a.js-selected-navigation-item.subnav-item:not(.selected)")).getPropertyValue('border-color')

// 接受来自插件的更新推荐内容请求
chrome.runtime.onMessage.addListener((request, sender) => {
    if (request.type === "UpdateRecommendContent") {
      if (DEBUG) {
        console.log("[trendingPageContent] receive message from extension: ", request);
      }
      recs = Array.from(request.content);
    }
  }
);

function createARow(row) {
  var article = document.createElement("article");
  article.class = "Box-row";
  article.style = "padding: 16px; margin-top: -1px; list-style-type:noneborder-top: 1px solid var(--color-border-secondary);"
  var h1 = document.createElement("h1");
  h1.class = "h3 lh-condensed" 
  h1.style = "font-weight: 600!important; font-size: 20px;";
  var sub_a = document.createElement("a");
  sub_a.href="/" + row['repo_owner'] +'/' +row['repo_name'];
  sub_a.style = 'color: var(--color-accent-fg); text-decoration: none; background-color: transparent';
  var svg = document.createElement("svg");
  svg.class = "octicon octicon-repo mr-1 color-fg-muted"
  svg.setAttribute("aria-hidden", "true");
  svg.setAttribute("height", 16);
  svg.setAttribute("viewBox", "0 0 16 16");
  svg.setAttribute("width", 16);
  svg.setAttribute("data-view-component", "true");
  var path = document.createElement("path")
  path.setAttribute("fill-rule", "evenodd");
  path.setAttribute("d", "M2 2.5A2.5 2.5 0 014.5 0h8.75a.75.75 0 01.75.75v12.5a.75.75 0 01-.75.75h-2.5a.75.75 0 110-1.5h1.75v-2h-8a1 1 0 00-.714 1.7.75.75 0 01-1.072 1.05A2.495 2.495 0 012 11.5v-9zm10.5-1V9h-8c-.356 0-.694.074-1 .208V2.5a1 1 0 011-1h8zM5 12.25v3.25a.25.25 0 00.4.2l1.45-1.087a.25.25 0 01.3 0L8.6 15.7a.25.25 0 00.4-.2v-3.25a.25.25 0 00-.25-.25h-3.5a.25.25 0 00-.25.25z");
  svg.appendChild(path);
  sub_a.appendChild(svg);
  var sub_span = document.createElement("span");
  sub_span.class = "text-normal";
  sub_span.style = "font-weight: 400!important;";
  sub_span.innerHTML = row['repo_owner'] +'/' +row['repo_name'];
  sub_a.appendChild(sub_span);
  h1.appendChild(sub_a);
  var p = document.createElement("p");
  p.class="col-9 color-text-secondary my-1 pr-4";
  p.innerHTML = row['repo_des'];
  article.appendChild(h1);
  article.appendChild(p); 
  return article;
}

function insertPersonalizedButton() {
  let subnav = document.getElementsByClassName('subnav')[0];
  let subnav_item = document.getElementsByClassName('subnav-item');
  let personalized_button = document.createElement("a");
  personalized_button.id = "buttonInserted"
  // personalized_button.href = "/trending/developers";
  personalized_button.class = "js-selected-navigation-item subnav-item"
  personalized_button.setAttribute("data-selected-links", "trending_developers /trending/developers")
  personalized_button.style = `position: relative; padding: 5px 16px; line-height: 20px; font-weight: 500; float: left; color: ${buttonColor}; border: 1px solid ${buttonBorderColor}; background_color: transparent; `
  personalized_button.innerHTML = "Personalized Repositories";
  personalized_button.href = "#"
  subnav.insertBefore(personalized_button, subnav_item[1]);
  personalized_button.addEventListener("click", addRecommendContent)
}

function addRecommendContent() {
  // 清除原来隔壁button的格式并设置自己的格式
  document.querySelector("a.js-selected-navigation-item.selected.subnav-item").style = `position: relative; float: left; padding: 5px 16px; font-weight: 500; line-height: 20px; color: ${buttonColor}; border: 1px solid ${buttonBorderColor}; background-color:${buttonBackgroundColor};`
  
  current_element = document.getElementById("buttonInserted");
  current_element.style.backgroundColor = focusedButtonBackgroundColor;
  current_element.style.color = focusedButtonColor;
  //  = `background-color: ; border-color: ${focusedButtonBorderColor}; color: ${focusedButtonColor}; z-index: 2; position: relative; padding: 5px 16px; line-height: 20px; font-weight: 500; float: left; border: 1px solid;` 
  
  // 清除原来BoxBody的内容
  var box = document.getElementsByClassName('Box-row')[0].parentElement;
  var childs = box.children;
  for(var i = childs.length - 1; i >= 0; i--) { 
    box.removeChild(childs[i]); 
  }

  // 清除侧边栏根据语言筛选等功能
  let box_header = document.querySelector("#js-pjax-container > div.position-relative.container-lg.p-responsive.pt-6 > div > div.Box-header.flex-items-center.flex-justify-between");
  box_header.removeChild(box_header.children[box_header.childElementCount - 1]);


  // 填充新的推荐内容
  for (let i = 0; i < recs.length; i++) {
    box.appendChild(createARow(recs[i]))
  }

  return false;
}

// 轮训页面是否被插入附加按钮
const timeId = setInterval(() => {
  if (document.getElementById("buttonInserted") == undefined) {
    console.log("Insert button");
    insertPersonalizedButton();
  }
}, 500);