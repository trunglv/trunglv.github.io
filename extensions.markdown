---
layout: page
title: Magento Extensions
permalink: /extensions/
---

All extensions below are free and open-source.

<div class="card-grid">
  {% assign exts = site.extensions | sort: "order" %}
  {% for ext in exts %}
  <a class="ext-card" href="{{ ext.url | relative_url }}">
    <div class="ext-card-top">
      <span class="ext-card-badge">Open Source</span>
    </div>
    <div class="ext-card-body">
      <p class="ext-card-category">{{ ext.category }}</p>
      <h3 class="ext-card-name">{{ ext.title }}</h3>
      <p class="ext-card-summary">{{ ext.summary }}</p>
    </div>
  </a>
  {% endfor %}
</div>
