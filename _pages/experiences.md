---
layout: page
permalink: /experiences/
title: 学术经历
description: Work, education, and research funding.
nav: true
nav_order: 3
---

{% assign work_items = site.data.experiences.work %}
{% assign education_items = site.data.experiences.education %}
{% assign funding_items = site.data.experiences.funding %}

<div class="experience-page">
  {% if work_items.size > 0 %}
  <section class="experience-section" aria-labelledby="experience-work-title">
    <h2 class="experience-section-title" id="experience-work-title">Work</h2>
    <div class="experience-list">
      {% for item in work_items %}
        <article class="experience-entry">
          <div class="experience-logo">
            {% if item.logo %}
              {% assign logo_src = item.logo %}
              {% unless logo_src contains "://" %}
                {% assign logo_src = logo_src | relative_url %}
              {% endunless %}
              <img src="{{ logo_src | escape }}" alt="{{ item.institution | escape }} logo" loading="lazy">
            {% else %}
              <i class="fa-solid fa-building-columns" aria-hidden="true"></i>
            {% endif %}
          </div>
          <div class="experience-content">
            <div class="experience-header">
              <h3>{{ item.institution | escape }}</h3>
              {% if item.dates %}<span class="experience-date">{{ item.dates | escape }}</span>{% endif %}
            </div>
            {% if item.role %}<p class="experience-role">{{ item.role | escape }}</p>{% endif %}
            {% if item.location %}<p class="experience-location">{{ item.location | escape }}</p>{% endif %}
            {% if item.detail or item.links.size > 0 %}
              <p class="experience-detail">
                {{ item.detail | escape }}
                {% for link in item.links %}
                  <a href="{{ link.url | escape }}" {% if link.url contains "://" %}target="_blank" rel="noopener noreferrer"{% endif %}>{{ link.label | escape }}</a>{% unless forloop.last %}, {% endunless %}
                {% endfor %}
              </p>
            {% endif %}
          </div>
        </article>
      {% else %}
        <p class="experience-empty">工作经历信息待补充。</p>
      {% endfor %}
    </div>
  </section>
  {% endif %}

  <section class="experience-section" aria-labelledby="experience-education-title">
    <h2 class="experience-section-title" id="experience-education-title">Education</h2>
    <div class="experience-list">
      {% for item in education_items %}
        <article class="experience-entry">
          <div class="experience-logo">
            {% if item.logo %}
              {% assign logo_src = item.logo %}
              {% unless logo_src contains "://" %}
                {% assign logo_src = logo_src | relative_url %}
              {% endunless %}
              <img src="{{ logo_src | escape }}" alt="{{ item.institution | escape }} logo" loading="lazy">
            {% else %}
              <i class="fa-solid fa-graduation-cap" aria-hidden="true"></i>
            {% endif %}
          </div>
          <div class="experience-content">
            <div class="experience-header">
              <h3>{{ item.institution | escape }}</h3>
              {% if item.dates %}<span class="experience-date">{{ item.dates | escape }}</span>{% endif %}
            </div>
            {% if item.role %}<p class="experience-role">{{ item.role | escape }}</p>{% endif %}
            {% if item.location %}<p class="experience-location">{{ item.location | escape }}</p>{% endif %}
            {% if item.detail or item.links.size > 0 %}
              <p class="experience-detail">
                {{ item.detail | escape }}
                {% for link in item.links %}
                  <a href="{{ link.url | escape }}" {% if link.url contains "://" %}target="_blank" rel="noopener noreferrer"{% endif %}>{{ link.label | escape }}</a>{% unless forloop.last %}, {% endunless %}
                {% endfor %}
              </p>
            {% endif %}
            {% if item.degrees.size > 0 %}
              <div class="experience-degrees">
                {% for degree in item.degrees %}
                  <div class="experience-degree">
                    <div class="experience-degree-header">
                      <h4>{{ degree.name | escape }}</h4>
                      {% if degree.dates %}<span class="experience-date">{{ degree.dates | escape }}</span>{% endif %}
                    </div>
                    {% if degree.detail or degree.links.size > 0 %}
                      <p class="experience-detail">
                        {{ degree.detail | escape }}
                        {% for link in degree.links %}
                          <a href="{{ link.url | escape }}" {% if link.url contains "://" %}target="_blank" rel="noopener noreferrer"{% endif %}>{{ link.label | escape }}</a>{% unless forloop.last %}, {% endunless %}
                        {% endfor %}
                      </p>
                    {% endif %}
                  </div>
                {% endfor %}
              </div>
            {% endif %}
          </div>
        </article>
      {% else %}
        <p class="experience-empty">教育经历信息待补充。</p>
      {% endfor %}
    </div>
  </section>

{% if funding_items.size > 0 %}
    <section class="experience-section experience-funding-section" aria-labelledby="experience-funding-title">
      <h2 class="experience-section-title" id="experience-funding-title">Research Funding</h2>
      <div class="experience-list">
        {% for grant in funding_items %}
          <article class="experience-funding-entry">
            <div class="experience-header">
              <h3>{{ grant.title | escape }}</h3>
              {% if grant.dates %}<span class="experience-date">{{ grant.dates | escape }}</span>{% endif %}
            </div>
            {% if grant.agency %}
              <p class="experience-detail">
                {% if grant.agency_url %}
                  <a href="{{ grant.agency_url | escape }}" {% if grant.agency_url contains "://" %}target="_blank" rel="noopener noreferrer"{% endif %}>{{ grant.agency | escape }}</a>
                {% else %}
                  {{ grant.agency | escape }}
                {% endif %}
              </p>
            {% endif %}
            {% if grant.role %}<p class="experience-role">{{ grant.role | escape }}</p>{% endif %}
          </article>
        {% endfor %}
      </div>
    </section>
{% endif %}
</div>
