{% extends "mail_templated/base.tpl" %}

{% block subject %}
فعالسازی حساب کاربری
{% endblock %}


{% block html %}
<p>کاربر گرامی،</p>
<p>برای فعالسازی حساب کاربری خود روی لینک زیر کلیک کنید:</p>
<p>
    <a href="http://127.0.0.1:8000/accounts/api/v1/activation/confirm/{{ token }}">فعالسازی حساب کاربری</a>
</p>
<p>با احترام،</p>
<p>تیم پشتیبانی</p>
{% endblock %}