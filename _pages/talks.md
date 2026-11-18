---
layout: page
permalink: /talks/
title: 学术报告
description: Invited talks, conference presentations, and seminars.
nav: true
nav_order: 4
---

{% assign invited = site.talks | where: "category", "invited" | sort: "date" | reverse %}
{% assign conferences = site.talks | where: "category", "conference" %}
{% assign posters = site.talks | where: "category", "poster" %}
{% assign conference_items = conferences | sort: "date" | reverse %}
{% assign poster_items = posters | sort: "date" | reverse %}

<div class="talks-page">
  <section class="talks-section" aria-labelledby="talks-invited">
    <div class="talks-section-head">
      <h2 id="talks-invited">Invited Talks</h2>
      <span class="talks-section-count">{{ invited.size }} talks</span>
    </div>
    <div class="talks-invited-list">
      {% for talk in invited %}
        <article class="talks-invited-entry">
          <div class="talks-invited-symbol" aria-hidden="true">
            {% if talk.materials.size > 0 %}
              <i class="fa-solid fa-video"></i>
            {% else %}
              <i class="fa-solid fa-microphone"></i>
            {% endif %}
          </div>
          <div class="talks-entry-body">
            <div class="talks-entry-head">
              <h3>{{ talk.title | escape }}</h3>
              <span class="talks-entry-date">{{ talk.date | date: "%b. %Y" }}</span>
            </div>
            <p class="talks-venue">{{ talk.venue | escape }}</p>
            <p class="talks-place">{{ talk.location | escape }}</p>
            {% if talk.materials.size > 0 %}
              <div class="talks-materials">
                {% for material in talk.materials %}
                  {% assign material_href = material.url %}
                  {% unless material_href contains "://" %}
                    {% assign material_href = material_href | relative_url %}
                  {% endunless %}
                  <a class="talks-material-link" href="{{ material_href | escape }}" {% if material.url contains "://" %}target="_blank" rel="noopener noreferrer"{% endif %}>
                    {% if material.type == "video" %}
                      <i class="fa-solid fa-circle-play" aria-hidden="true"></i>
                    {% elsif material.type == "slides" %}
                      <i class="fa-solid fa-file-pdf" aria-hidden="true"></i>
                    {% else %}
                      <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i>
                    {% endif %}
                    {{ material.label | escape }} ↗
                  </a>
                {% endfor %}
              </div>
            {% endif %}
          </div>
        </article>
      {% else %}
        <p class="talks-empty">邀请报告将在这里展示。</p>
      {% endfor %}
    </div>
  </section>

  <section class="talks-section" aria-labelledby="talks-conferences">
    <div class="talks-section-head">
      <h2 id="talks-conferences">Conference Talks</h2>
      <span class="talks-section-count">{{ conference_items.size }} talks</span>
    </div>
    <div class="talks-conference-list">
      {% for talk in conference_items %}
        <article class="talks-conference">
          <div class="talks-conf-date">
            <span class="talks-conf-month">{{ talk.date | date: "%b" }}</span>
            <span class="talks-conf-year">{{ talk.date | date: "%Y" }}</span>
          </div>
          <div class="talks-entry-body">
            <p class="talks-type">
              {% if talk.category == "poster" %}
                <i class="fa-solid fa-file-lines" aria-hidden="true"></i> Poster
              {% else %}
                <i class="fa-solid fa-chalkboard" aria-hidden="true"></i> Conference talk
              {% endif %}
            </p>
            <div class="talks-entry-head">
              <h3>{{ talk.title | escape }}</h3>
            </div>
            <p class="talks-venue">{{ talk.venue | escape }}</p>
            <p class="talks-place">{{ talk.location | escape }}</p>
            {% if talk.materials.size > 0 %}
              <div class="talks-materials">
                {% for material in talk.materials %}
                  {% assign material_href = material.url %}
                  {% unless material_href contains "://" %}
                    {% assign material_href = material_href | relative_url %}
                  {% endunless %}
                  <a class="talks-material-link" href="{{ material_href | escape }}" {% if material.url contains "://" %}target="_blank" rel="noopener noreferrer"{% endif %}>
                    {% if material.type == "video" %}
                      <i class="fa-solid fa-circle-play" aria-hidden="true"></i>
                    {% elsif material.type == "slides" %}
                      <i class="fa-solid fa-file-pdf" aria-hidden="true"></i>
                    {% else %}
                      <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i>
                    {% endif %}
                    {{ material.label | escape }} ↗
                  </a>
                {% endfor %}
              </div>
            {% endif %}
          </div>
        </article>
      {% else %}
        <p class="talks-empty">会议报告将在这里展示。</p>
      {% endfor %}
    </div>
  </section>

  <section class="talks-section" aria-labelledby="talks-posters">
    <div class="talks-section-head">
      <h2 id="talks-posters">Conference Posters</h2>
      <span class="talks-section-count">{{ poster_items.size }} posters</span>
    </div>
    <div class="talks-conference-list">
      {% for talk in poster_items %}
        <article class="talks-conference">
          <div class="talks-conf-date">
            {% if talk.date_basis == "award_month" %}
              <span class="talks-conf-month">获奖</span>
              <span class="talks-conf-year">{{ talk.date | date: "%Y.%m" }}</span>
            {% elsif talk.date_basis == "upload" %}
              <span class="talks-conf-month">收录</span>
              <span class="talks-conf-year">{{ talk.date | date: "%Y.%m" }}</span>
            {% else %}
              <span class="talks-conf-month">{{ talk.date | date: "%b" }}</span>
              <span class="talks-conf-year">{{ talk.date | date: "%Y" }}</span>
            {% endif %}
          </div>
          <div class="talks-entry-body">
            <p class="talks-type">
              {% if talk.category == "poster" %}
                <i class="fa-solid fa-file-lines" aria-hidden="true"></i> Poster
              {% else %}
                <i class="fa-solid fa-chalkboard" aria-hidden="true"></i> Conference talk
              {% endif %}
            </p>
            <div class="talks-entry-head">
              <h3>{{ talk.title | escape }}</h3>
            </div>
            <p class="talks-venue">{{ talk.venue | escape }}</p>
            {% if talk.authors %}
              <p class="talks-place">作者：{{ talk.authors | escape }}</p>
            {% endif %}
            {% if talk.affiliation %}
              <p class="talks-place">单位：{{ talk.affiliation | escape }}</p>
            {% endif %}
            {% if talk.location %}
              <p class="talks-place">{{ talk.location | escape }}</p>
            {% endif %}
            {% if talk.date_basis == "upload" %}
              <p class="talks-place">日期说明：仅为资料上传日期，并非会议举办日期。</p>
            {% endif %}
            {% if talk.award_title %}
              <div class="talks-award">
                <div class="talks-award-details">
                  <p class="talks-award-name">
                    <i class="fa-solid fa-award" aria-hidden="true"></i>
                    <strong>{{ talk.award_title | escape }}</strong>
                    · {{ talk.award_issuer | escape }}
                  </p>
                  <p class="talks-award-meta">
                    获奖人：{{ talk.award_recipient | escape }} · 证书日期：{{ talk.award_date | escape }}
                  </p>
                  {% if talk.award_certificate_pdf %}
                    <div class="talks-materials">
                      <a class="talks-material-link" href="{{ talk.award_certificate_pdf | relative_url | escape }}" target="_blank" rel="noopener noreferrer">
                        <i class="fa-solid fa-file-pdf" aria-hidden="true"></i>
                        查看获奖证明（原始扫描 PDF） ↗
                      </a>
                    </div>
                  {% endif %}
                </div>
                {% if talk.award_certificate_image %}
                  <a class="talks-award-preview" href="{{ talk.award_certificate_pdf | relative_url | escape }}" target="_blank" rel="noopener noreferrer" aria-label="查看{{ talk.award_title | escape }}证书原始扫描件">
                    <img src="{{ talk.award_certificate_image | relative_url | escape }}" alt="{{ talk.award_title | escape }}证书（{{ talk.award_recipient | escape }}）" width="440" height="620" loading="lazy" decoding="async">
                  </a>
                {% endif %}
              </div>
            {% endif %}
            {% if talk.materials.size > 0 %}
              <div class="talks-materials">
                {% for material in talk.materials %}
                  {% assign material_href = material.url %}
                  {% unless material_href contains "://" %}
                    {% assign material_href = material_href | relative_url %}
                  {% endunless %}
                  <a class="talks-material-link" href="{{ material_href | escape }}" {% if material.url contains "://" %}target="_blank" rel="noopener noreferrer"{% endif %}>
                    {% if material.type == "video" %}
                      <i class="fa-solid fa-circle-play" aria-hidden="true"></i>
                    {% elsif material.type == "slides" %}
                      <i class="fa-solid fa-file-pdf" aria-hidden="true"></i>
                    {% else %}
                      <i class="fa-solid fa-arrow-up-right-from-square" aria-hidden="true"></i>
                    {% endif %}
                    {{ material.label | escape }} ↗
                  </a>
                {% endfor %}
              </div>
            {% endif %}
          </div>
        </article>
      {% else %}
        <p class="talks-empty">会议海报将在这里展示。</p>
      {% endfor %}
    </div>
  </section>
</div>
