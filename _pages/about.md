---
layout: about
title: 首页
permalink: /
subtitle: 催化科学 · 第一性原理计算 · 微观动力学 · 人工智能

profile: false
selected_papers: false
social: false

announcements:
  enabled: false

latest_posts:
  enabled: false
---

我是**李亚倩（Yaqian Li）**，中国石油大学（华东）化学工程学院博士研究生，研究兴趣包括**人工智能辅助催化剂筛选、第一性原理计算、异相催化反应机制及微观动力学**。

本站记录催化科学、计算化学与机器学习的研究工作、论文成果和可复现的学习笔记，重点关注从电子结构、反应能量到催化性能的关联。

[ResearchGate 学术主页](https://www.researchgate.net/profile/Yaqian-Li-10) · [论文成果](/publications/) · [CatMAP 科研代码](https://github.com/ly5681672-max/catmap)

## 最新学习笔记

<div class="academic-latest-posts">
{% for post in site.posts limit:5 %}
  <div class="academic-latest-post">
    <time datetime="{{ post.date | date: '%Y-%m-%d' }}">{{ post.date | date: '%Y.%m.%d' }}</time>
    <a href="{{ post.url | relative_url }}">{{ post.title | escape }}</a>
  </div>
{% endfor %}
</div>

## 研究方向

### 1. 催化反应机理与第一性原理计算

学习密度泛函理论（DFT）、吸附能、过渡态搜索、反应能垒及催化反应路径分析，理解催化剂结构与反应活性之间的关系。

### 2. CatMAP微观动力学

系统学习CatMAP开源框架，涵盖：

- 反应机理与基元反应
- 反应自由能与速率常数
- 表面覆盖度与稳态方程
- 转换频率（TOF）
- 速率控制度（DRC）
- 催化活性描述符与火山图

### 3. 人工智能辅助催化研究

关注机器学习、图神经网络（GNN）、SISSO描述符发现，以及数据驱动的催化剂筛选和反应性能预测。

## 代表性论文

ResearchGate 共收录 **25 条成果记录**，去重后为 **23 篇期刊论文**，另有 **2 条对应已发表论文的预印本版本**。详见[全部论文成果](/publications/)。

<div class="publications">
{% bibliography --group_by none --query @*[selected=true]* %}
</div>

[查看全部论文成果](/publications/)

## CatMAP中文学习教程

本系列从基础理论出发，逐步学习微观动力学建模方法。

课程将结合真实科研数据，记录公式推导、Python代码、模型运行和结果验证过程。

## 我的科研项目

**Ti–M异核催化位点上的1-己烯环氧化研究**

围绕过氧中间体OOH*的形成、氧转移、表面物种覆盖度和催化活性，探索异核金属位点对反应机理与动力学性能的影响。

相关代码：

[GitHub：CatMAP科研项目](https://github.com/ly5681672-max/catmap)

---

本站内容持续更新，主要用于个人科研学习与知识整理。
