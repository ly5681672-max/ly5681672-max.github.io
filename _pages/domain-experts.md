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

## 每位专家的关键科研里程碑

<p>本时间轴只展示<strong>具有可追溯文献依据、明确归属专家的代表性成果</strong>，不按发表时间机械收录全部新论文。里程碑需回答“提出了什么方法或发现、解决什么问题、学术意义是什么”。<strong>PROVISIONAL</strong> 表示仅完成书目关联与初步整理，CONFIRMED_ABSTRACT 表示出版商原始摘要与作者身份已核验，但并非全文独立复核；CONFIRMED_BIBLIOGRAPHY 仅表示书目信息已核验；PROVISIONAL 仍待核验。无合格节点的专家保留待核验状态，不使用普通新论文充数。</p>

{% assign milestones = site.data.domain_expert_milestones %}
{% for person in site.data.domain_experts %}
<section class="domain-person-timeline" data-person-group="{{ person.group }}" id="timeline-{{ person.id }}">
  <h3>{{ person.name | escape }} · 关键科研里程碑</h3>
  <p class="domain-help">{{ person.institution | escape }} · <a href="{{ person.official_url }}" target="_blank" rel="noopener noreferrer">研究组官网</a></p>
  {% assign milestone_count = 0 %}
  {% for item in milestones %}
    {% if item.expert_ids contains person.id %}
      {% assign milestone_count = milestone_count | plus: 1 %}
      <article class="domain-timeline-event">
        <time datetime="{{ item.year | escape }}">{{ item.year | escape }}</time>
        <div class="domain-timeline-content">
          <div class="domain-paper-meta">{{ item.type | escape }} · {{ item.review_status | escape }}</div>
          <h4><a href="{{ item.url }}" target="_blank" rel="noopener noreferrer">{{ item.title | escape }}</a></h4>
          <p><strong>研究贡献线索：</strong>{{ item.evidence | escape }}</p>
          <p class="domain-help"><strong>作者：</strong>{{ item.authors | escape }}</p>
          <p class="domain-help">{{ item.review_note | escape }}{% if item.publisher_source %} · <a href="{{ item.publisher_source }}" target="_blank" rel="noopener noreferrer">出版商证据</a>{% endif %} · <a href="{{ item.url }}" target="_blank" rel="noopener noreferrer">原始来源 ↗</a></p>
        </div>
      </article>
    {% endif %}
  {% endfor %}
  {% if milestone_count == 0 %}
    <p class="domain-help domain-milestone-pending">尚未完成该专家历史代表性成果的原文核验，暂不将近期论文自动认定为里程碑。下方“最新论文”仍持续自动更新。</p>
  {% endif %}
</section>
{% endfor %}

## 历史代表性成果候选（自动筛选，待科学审核）

<p>该列表用于辅助补全每位专家的科研里程碑：按作者身份、历史引用表现及研究主题生成候选，<strong>不代表已经核实“首次发现”或科学突破</strong>。只有人工核验论文原文后，才能进入上方正式里程碑时间轴。</p>
{% assign candidate_data = site.data.domain_expert_milestone_candidates %}
{% if candidate_data.generated_at %}
<p class="domain-help">候选数据更新时间（UTC）：{{ candidate_data.generated_at | escape }}；来源：OpenAlex。引用次数为动态书目指标，不作为独立的科学贡献结论。</p>
{% endif %}
{% for person in site.data.domain_experts %}
  {% assign candidate_count = 0 %}
  {% for item in candidate_data.candidates %}
    {% if item.expert_id == person.id %}
      {% assign candidate_count = candidate_count | plus: 1 %}
      {% if candidate_count == 1 %}<h3 data-person-group="{{ person.group }}">{{ person.name | escape }} · 候选研究</h3>{% endif %}
      <article class="domain-paper" data-paper-group="{{ person.group }}">
        <p class="domain-paper-meta">{{ item.year | escape }} · {{ item.journal | escape }} · 引用记录 {{ item.cited_by_count | escape }} · PROVISIONAL</p>
        <h4><a href="{{ item.doi_url }}" target="_blank" rel="noopener noreferrer">{{ item.title | escape }}</a></h4>
        <p>主题线索：{{ item.relevance_tags | join: '、' | escape }}</p>
        <p class="domain-help">科学发现尚未核验 · <a href="{{ item.source_url }}" target="_blank" rel="noopener noreferrer">OpenAlex 书目</a> · <a href="{{ item.doi_url }}" target="_blank" rel="noopener noreferrer">DOI</a></p>
      </article>
    {% endif %}
  {% endfor %}
{% endfor %}

## 研究领域背景与历史节点

<p>以下是研究领域背景材料，<strong>不自动归属于某位专家</strong>；其历史意义仍需结合原始文献进一步核验。</p>
<div class="domain-milestones">
{% for item in milestones %}
  {% if item.expert_ids.size == 0 %}
    <article class="domain-milestone" data-milestone-group="{{ item.group }}">
      <div><b>{{ item.year | escape }}</b> · {{ item.type | escape }} · {{ item.review_status | escape }}</div>
      <h3><a href="{{ item.url }}" target="_blank" rel="noopener noreferrer">{{ item.title | escape }}</a></h3>
      <p>{{ item.evidence | escape }}</p>
    </article>
  {% endif %}
{% endfor %}
</div>

## 最新SCI相关论文（自动检索，非里程碑）

{% assign update = site.data.domain_expert_updates %}
{% if update.generated_at %}<p>上次有效检索（UTC）：<time>{{ update.generated_at }}</time>；检索窗口 {{ update.window_days }} 天。按发表日期排序；“SCI相关”仅表示学科相关，未自动核验Web of Science收录；入选表示<strong>规则相关性</strong>，不代表已完成全文核验。</p>{% else %}<p><strong>尚未建立可验证的在线检索结果。</strong>本页面初始仅包含人工整理的专家资料；首次有效同步后展示带 DOI 的真实文献。</p>{% endif %}
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
