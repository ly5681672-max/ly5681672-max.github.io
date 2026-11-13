---
layout: page
title: 领域专家与知识图谱
permalink: /domain-experts/
description: AI 与催化知识学习、烯烃环氧化领域专家的研究图谱与论文追踪
nav: true
nav_order: 5
---

<link rel="stylesheet" href="{{ '/assets/css/domain-experts.css' | relative_url }}">

<p>将领域专家、研究方法、论文证据连接起来，重点关注 <strong>AI 结合知识学习</strong> 和 <strong>烯烃环氧化</strong>。图中专家—主题关联是依据官方简介<strong>人工整理</strong>的研究兴趣，不代表合作关系或已证明的因果关系。点选专家可查看简介、来源、对应主题与近期论文。</p>

<div class="domain-controls" aria-label="筛选研究方向">
  <button class="domain-active" data-domain-filter="all" aria-pressed="true">全部</button>
  <button data-domain-filter="ai" aria-pressed="false">AI 结合知识学习</button>
  <button data-domain-filter="epox" aria-pressed="false">烯烃环氧化</button>
</div>

<p class="domain-help">手机端可以左右滑动图谱。点击节点查看详情；实线代表经人工整理的“专家—研究兴趣”关联；启用论文同步后，虚线代表经过作者身份匹配的“专家—论文”关系，不代表两位专家共同发表论文。</p>
<div class="domain-graph-scroll"><svg id="domain-experts-graph" viewBox="0 0 900 720" role="img" aria-label="领域专家—研究主题知识图谱" xmlns="http://www.w3.org/2000/svg"></svg></div>
<div id="domain-expert-detail" class="domain-detail" aria-live="polite">点击图中的专家或下方姓名，查看官方介绍与研究关注点。</div>

## 专家与官方介绍

<div class="domain-experts-list">
{% for person in site.data.domain_experts %}
  <article class="domain-expert-card" data-person-group="{{ person.group }}">
    <h3><button data-person-id="{{ person.id }}" class="domain-person-button">{{ person.name | escape }}</button></h3>
    <p><small>{{ person.institution | escape }}</small></p>
    <p>{{ person.intro | escape }}</p>
    <p class="domain-tags">{% for topic in person.topics %}<span>{{ topic | escape }}</span>{% endfor %}</p>
    <p><a href="{{ person.official_url }}" target="_blank" rel="noopener noreferrer">官方主页 ↗</a>{% if person.orcid %} · <a href="https://orcid.org/{{ person.orcid }}" target="_blank" rel="noopener noreferrer">ORCID ↗</a>{% endif %}</p>
  </article>
{% endfor %}
</div>

## 每位专家的最新研究与个人时间轴

<p>优先显示化工、催化与材料领域精选期刊论文。<strong>“优先期刊”仅表示本站人工维护的期刊名单，并不等于自动核实 SCI 收录、JCR 分区或论文科学结论。</strong>每条节点按实际发表日期排列，保留期刊、DOI、作者关联及研究主题；关键发现须阅读全文并人工核验后才可标注。</p>

{% assign update = site.data.domain_expert_updates %}
{% for person in site.data.domain_experts %}
<section class="domain-person-timeline" data-person-group="{{ person.group }}" id="timeline-{{ person.id }}">
  <h3>{{ person.name | escape }} · 研究时间轴</h3>
  <p class="domain-help">{{ person.institution | escape }} · <a href="{{ person.official_url }}" target="_blank" rel="noopener noreferrer">研究组官网</a></p>
  {% assign found_count = 0 %}
  {% for paper in update.papers %}
    {% if paper.author_names contains person.name %}
      {% assign found_count = found_count | plus: 1 %}
      <article class="domain-timeline-event">
        <time>{{ paper.publication_date | escape }}</time>
        <div class="domain-timeline-content">
          <div class="domain-paper-meta">{% if paper.priority_journal %}<strong>优先期刊</strong> · {% endif %}{{ paper.journal | escape }} · {{ paper.publication_type | escape }}</div>
          <h4><a href="{{ paper.doi_url }}" target="_blank" rel="noopener noreferrer">{{ paper.title | escape }}</a></h4>
          <p><strong>研究线索（非已证实发现）：</strong>{{ paper.match_tags | join: '、' | escape }}</p>
          <p class="domain-help">关键发现：待核验论文正文。<a href="{{ paper.source_url }}" target="_blank" rel="noopener noreferrer">书目证据</a> · <a href="{{ paper.doi_url }}" target="_blank" rel="noopener noreferrer">DOI</a></p>
        </div>
      </article>
    {% endif %}
  {% endfor %}
  {% if found_count == 0 %}
    <p class="domain-help">当前检索窗口暂无已核验身份且符合主题条件的论文；不代表该专家未发表论文。{% unless update.generated_at %}自动检索尚未成功执行。{% endunless %}</p>
  {% endif %}
</section>
{% endfor %}

## 研究方向演进：关键证据时间轴

<p>下列为<strong>人工精选且有原始来源的代表性节点</strong>，不代表完整文献计量结论，也不能据此推定作者之间存在师承或合作关系。</p>
<div class="domain-milestones">
{% for item in site.data.domain_expert_milestones %}
  <article class="domain-milestone" data-milestone-group="{{ item.group }}">
    <div><b>{{ item.year | escape }}</b> · {{ item.type | escape }}</div>
    <h3><a href="{{ item.url }}" target="_blank" rel="noopener noreferrer">{{ item.title | escape }}</a></h3>
    <p>{{ item.evidence | escape }}</p><p><small>{{ item.authors | escape }}</small></p>
  </article>
{% endfor %}
</div>

## 与研究方向相关的最新论文

{% assign update = site.data.domain_expert_updates %}
{% if update.generated_at %}<p>上次有效检索（UTC）：<time>{{ update.generated_at }}</time>；检索窗口 {{ update.window_days }} 天。按发表日期排序；入选表示<strong>规则相关性</strong>，不代表已完成全文核验。</p>{% else %}<p><strong>尚未建立可验证的在线检索结果。</strong>本页面初始仅包含人工整理的专家资料；首次有效同步后展示带 DOI 的真实文献。</p>{% endif %}
{% if update.papers and update.papers.size > 0 %}
<div class="domain-papers">
{% for paper in update.papers limit:60 %}
  <article class="domain-paper" data-paper-group="{{ paper.group }}">
    <div class="domain-paper-meta">{{ paper.publication_date | escape }} · {{ paper.journal | escape }} · {% if paper.priority_journal %}优先期刊 · {% endif %}{{ paper.relevance | escape }}相关 · {{ paper.group_label | escape }}</div>
    <h3><a href="{{ paper.doi_url }}" target="_blank" rel="noopener noreferrer">{{ paper.title | escape }}</a></h3>
    <p>已匹配专家：{{ paper.author_names | join: ', ' | escape }}</p>
    <p>匹配主题：{{ paper.match_tags | join: '、' | escape }} · <a href="{{ paper.source_url }}" target="_blank" rel="noopener noreferrer">OpenAlex 原始记录</a></p>
  </article>
{% endfor %}
</div>
{% endif %}
<p class="domain-help">数据规则：仅纳入具备 DOI、作者身份匹配且主题相关的文献；原始来源保留 DOI、OpenAlex 记录和发表日期。没有 ORCID 的专家暂不自动归属新论文，以免同名误判。页面不自动生成未核验的研究结论。</p>

<script id="domain-experts-data" type="application/json">{{ site.data.domain_experts | jsonify | replace: '</', '<\/' }}</script>
<script id="domain-expert-papers-data" type="application/json">{{ site.data.domain_expert_updates | jsonify | replace: '</', '<\/' }}</script>
<script src="{{ '/assets/js/domain-experts.js' | relative_url }}" defer></script>
