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
        <p class="talks-empty">会议海报将在这里展示。</p>
      {% endfor %}
    </div>
  </section>
</div>
