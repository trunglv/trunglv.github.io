---
layout: page
title: Liên hệ
permalink: /vi/contact/
lang: vi
---

Hãy cho tôi biết đôi chút về dự án của bạn, tôi sẽ phản hồi trong vòng một đến hai ngày làm việc.

<form id="contact-form" class="contact-form">
  <label>Họ và tên
    <input type="text" name="name" required>
  </label>
  <label>Công ty <span class="contact-optional">(không bắt buộc)</span>
    <input type="text" name="company">
  </label>
  <label>Email
    <input type="email" name="email" required>
  </label>
  <label>Bạn cần gì?
    <textarea name="message" rows="6" required placeholder="Mô tả ngắn gọn về doanh nghiệp, hệ thống bạn đang hình dung và thời hạn (nếu có)."></textarea>
  </label>
  <button type="submit" class="contact-submit">Gửi tin nhắn</button>
  <p class="contact-note">Thao tác này sẽ mở ứng dụng email với nội dung đã soạn sẵn, gửi tới {{ site.email }}.</p>
</form>

<p class="contact-direct">Hoặc gửi email trực tiếp tới <a href="mailto:{{ site.email }}">{{ site.email }}</a>.</p>

<script>
document.getElementById('contact-form').addEventListener('submit', function (e) {
  e.preventDefault();
  var f = this;
  var subject = encodeURIComponent('[Betagento] Yêu cầu dự án từ ' + f.name.value);
  var body = encodeURIComponent(
    'Họ và tên: ' + f.name.value + '\n' +
    'Công ty: ' + f.company.value + '\n' +
    'Email: ' + f.email.value + '\n\n' +
    f.message.value
  );
  window.location.href = 'mailto:{{ site.email }}?subject=' + subject + '&body=' + body;
});
</script>
