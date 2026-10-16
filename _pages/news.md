---
layout: page
title: 近期动态
permalink: /news/
description: 已核验的论文发表、学术报告与科研进展
nav: true
nav_order: 5
---

{% assign academic_updates = site.news | sort: "date" | reverse %}

<div class="academic-news-list">
  {% for item in academic_updates %}
    <article class="academic-news-entry">
      <time datetime="{{ item.date | date: '%Y-%m-%d' }}">{{ item.date | date: "%Y.%m.%d" }}</time>
      <div class="academic-news-detail">
        <span class="academic-news-kind">学术动态</span>
        <a href="{{ item.url | relative_url }}">{{ item.title | escape }}</a>
      </div>
    </article>
  {% else %}
    <p>暂无已核验的学术动态。</p>
  {% endfor %}
</div>

科研计算与学习记录单独收录于[学习笔记](/blog/)，不与论文发表日期混淆。
