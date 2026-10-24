---
layout: page
title: Tiện ích Magento
permalink: /vi/extensions/
lang: vi
---

Tất cả tiện ích dưới đây đều miễn phí và mã nguồn mở. Nội dung chi tiết từng tiện ích hiện chỉ có bằng tiếng Anh.

<div class="card-grid">
  {% assign exts = site.extensions | sort: "order" %}
  {% for ext in exts %}
  <a class="ext-card" href="{{ ext.url | relative_url }}">
    <div class="ext-card-top">
      <span class="ext-card-badge">Mã nguồn mở</span>
    </div>
    <div class="ext-card-body">
      <p class="ext-card-category">{{ ext.category }}</p>
      <h3 class="ext-card-name">{{ ext.title }}</h3>
      <p class="ext-card-summary">{{ ext.summary }}</p>
    </div>
  </a>
  {% endfor %}
</div>
