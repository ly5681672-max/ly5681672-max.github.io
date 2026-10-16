---
layout: about
title: 首页
permalink: /
subtitle: 催化科学 · 第一性原理计算 · 微观动力学 · 人工智能

profile:
  align: right
  image: yaqian-li-portrait.jpg
  image_circular: true
  more_info: >
    <p>中国石油大学（华东） · 化学工程学院博士研究生</p>
selected_papers: false
social: true

announcements:
  enabled: false

latest_posts:
  enabled: false
---

我是**李亚倩（Yaqian Li）**，中国石油大学（华东）化学工程学院博士研究生，研究兴趣包括**人工智能辅助催化剂筛选、第一性原理计算、异相催化反应机制及微观动力学**。

研究重点是建立从催化活性位电子结构、反应能量到动力学性能的关联，并探索机器学习与机理计算相结合的催化剂设计方法。

[ORCID](https://orcid.org/0009-0004-7005-8512) · [Google Scholar](https://scholar.google.com/citations?user=ReMQrbIAAAAJ&hl=zh-CN) · [Web of Science](https://www.webofscience.com/wos/author/rid/GVT-4395-2022) · [ResearchGate](https://www.researchgate.net/profile/Yaqian-Li-10)

[全部论文成果](/publications/) · [CatMAP 科研代码](https://github.com/ly5681672-max/catmap)

## 近期动态

{% assign home_updates = site.news | concat: site.posts | sort: "date" | reverse %}
<div class="academic-latest-posts">
{% for item in home_updates limit:5 %}
  <div class="academic-latest-post">
    <time datetime="{{ item.date | date: '%Y-%m-%d' }}">{{ item.date | date: '%Y.%m.%d' }}</time>
    <a href="{{ item.url | relative_url }}">{{ item.title | escape }}</a>
  </div>
{% else %}
  <p>暂无公开的科研动态。</p>
{% endfor %}
</div>

[查看全部科研动态 →](/news/)

## 代表性成果

现收录 **{{ site.data.publication_stats.journal_count }} 篇独立期刊论文**，新成果经 DOI、作者和出版信息核验后自动更新。详见[全部论文成果](/publications/)。

<div class="publications">
{% bibliography --group_by none --query @*[selected=true]* %}
</div>

[查看全部论文成果 →](/publications/)

## 研究方向

**异相催化机理与 DFT · CatMAP 微观动力学 · 机器学习催化描述符。** 相关内容分别见[科研项目](/projects/)、[CatMAP 中文教程](/catmap/)及[文献笔记](/literature/)。
