---
layout: page
title: Finance
permalink: /finance/
---

<div class="archive">
  {% assign finance_posts = site.posts | where_exp: "post", "post.categories contains 'finance'" %}
  {% assign posts_by_year = finance_posts | group_by_exp: "post", "post.date | date: '%Y'" %}
  {% if posts_by_year.size == 0 %}
  <p>No posts yet.</p>
  {% endif %}
  {% for year in posts_by_year %}
  <section class="archive-year">
    <h2 class="archive-year-title">{{ year.name }}</h2>
    <ul class="post-list">
      {% for post in year.items %}
      <li class="post-list-item">
        <a href="{{ post.url | relative_url }}">
          <span class="post-list-title">{{ post.title }}</span>
          <time class="post-list-date" datetime="{{ post.date | date_to_xmlschema }}">
            {{ post.date | date: "%b %-d, %Y" }}
          </time>
        </a>
      </li>
      {% endfor %}
    </ul>
  </section>
  {% endfor %}
</div>
