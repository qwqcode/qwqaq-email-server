# qwqaq-email-server

✉ Http 异步邮箱服务器

```bash
pip install flask-mail
cp conf.example.json conf.json
python qwqaq-email-server.py
```

GET 请求：`/?password=[密码]&mail_title=[标题]&mail_content=[正文]&mail_recipient=[接收者邮箱]`