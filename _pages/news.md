---
layout: page
title: 近期动态
permalink: /news/
description: 科研动态与学习笔记的公开更新记录
nav: true
nav_order: 5
---

{% assign academic_updates = site.news | concat: site.posts | sort: "date" | reverse %}

<div class="academic-news-list">
  {% for item in academic_updates %}
    <article class="academic-news-entry">
      <time datetime="{{ item.date | date: '%Y-%m-%d' }}">{{ item.date | date: "%Y.%m.%d" }}</time>
      <div class="academic-news-detail">
        {% if item.url contains "/blog/" %}
          <span class="academic-news-kind">研究笔记</span>
        {% else %}
          <span class="academic-news-kind">学术动态</span>
        {% endif %}
        <a href="{{ item.url | relative_url }}">{{ item.title | escape }}</a>
      </div>
    </article>
  {% else %}
    <p>暂无公开的科研动态。</p>
  {% endfor %}
</div>
