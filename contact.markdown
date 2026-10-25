---
layout: page
title: Contact
permalink: /contact/
---

Tell me a little about your project and I'll get back to you, usually within one or two working days.

<form id="contact-form" class="contact-form">
  <label>Name
    <input type="text" name="name" required>
  </label>
  <label>Company <span class="contact-optional">(optional)</span>
    <input type="text" name="company">
  </label>
  <label>Email
    <input type="email" name="email" required>
  </label>
  <label>What do you need?
    <textarea name="message" rows="6" required placeholder="A short description of your business, the system you have in mind, and any deadline."></textarea>
  </label>
  <button type="submit" class="contact-submit">Send message</button>
  <p class="contact-note">This opens your email app with the message ready to send to {{ site.email }}.</p>
</form>

<p class="contact-direct">Or email me directly at <a href="mailto:{{ site.email }}">{{ site.email }}</a>.</p>

<script>
document.getElementById('contact-form').addEventListener('submit', function (e) {
  e.preventDefault();
  var f = this;
  var subject = encodeURIComponent('[Betagento] Project inquiry from ' + f.name.value);
  var body = encodeURIComponent(
    'Name: ' + f.name.value + '\n' +
    'Company: ' + f.company.value + '\n' +
    'Email: ' + f.email.value + '\n\n' +
    f.message.value
  );
  window.location.href = 'mailto:{{ site.email }}?subject=' + subject + '&body=' + body;
});
</script>
