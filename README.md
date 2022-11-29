## Readme
### **项目简介**
在软件开发中，软件开发人员经常需要相互合作，复用其它代码库中的代码。这种需 求推动了许多在线代码协作平台的出现，其中最著名的就是 GitHub，该平台上托管了超过 4000 万的开发人员和超过 1 亿个软件仓库。为了更好的依照软件开发者偏好进行软件仓库 的搜索，GitHub 提供了两个功能:
1.	GitHub Trending 页面，GitHub 列出了 Trending 页面上某个时间范围内项目体量和关注度增长最大的 25 个软件仓库，并每天更新。相关研究表明，如果一个软件仓库在趋势页面中出现，其项目的托管团队也会得到相 应的扩张。
2.	 Topic功能，它允许开发人员为自己的软件仓库分配主题标签。合适的主题 往往会帮助其它开发人员更容易找到和理解这个软件仓库。 
但即使 GitHub 推出了上述的两个功能，开发者仍然很难找到感兴趣的开源项目进行研究和贡献。 我们分析可能有两个主要原因:
1.	GitHub 提供的基于主题的搜索远非理想。
2.	GitHub 缺少针对软件开发者的个性化流行软件仓库推荐服务
基于以上背景和开发者遇到的难题，我们提出了一种面向软件开发者的个性化Trending软件仓库 推荐服务，并命名为“GHTRec”，用于向软件开发人员推荐个性化的 GitHub流行软件仓库。

### **技术方案**
<img width="333" alt="image" src="https://user-images.githubusercontent.com/21121412/204554304-ace98dc3-c465-449e-960d-17e5c15adfb7.png">
在这里，我们展示GHTRec服务的的架构。推荐服务由三部分组成，分别是：
1.  预测仓库主题：我们设计并训练了一个深度学习模型，为GitHub软件仓库预测Topic标签。需要预测的仓库包含GitHub的Trending仓库和软件开发者的历史提交仓库。
2. 生成用户的主题偏好：我们设计了一个根据软件开发者历史提交开源项目，计算用户主题向量的方法。
3. Trending软件仓库的重排序：我们提出了一种为开发人重排列 GitHub Trending软件仓库的方法。用户可以使用该服务提供的界面浏览个性化推荐的流行仓库。‘

### **工程实现**
前端以以 Chrome 插件形式呈现，主要负责与用户进行交互，展示功能，实现的主要语言是 JavaScript、HTML 和 CSS。

后端是一个 flask 项目，主要编程语言是 Python，除去相应前 端请求的服务器项目之外，后端还包含一个日更的GitHub Trending仓库收集模块，主要为获取 GitHub Trending 仓库， 按照时间存储在 mongodb 服务器中，此外还包含一个推荐模块，这个模块主要调用训练好 的项目主体预测模型，对爬取的 Trending 仓库以及用户自己 commit 的仓库进行技术主题 预测，由此得到仓库的偏重主题分布以及用户的偏好技术主题分布，基于两者的余弦相似 度给出最终推荐
![image](https://user-images.githubusercontent.com/21121412/204554531-a0ce0b7b-cc3c-4d59-ae8c-a191bc0f55fa.png)
