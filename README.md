# mblibs

Fast tools for programming

installation
```bash
$ pip install mblibs
```

Usage for settings
```python
# Using settings
from mblibs.fast import FastSettings

settings = FastSettings("/path/to/yaml_or_json")
value = settings.get("/path/to/key", "default_value")
integer = settings.getInt("/path/to/keyInt", 12)

# => 18/07/2018
date = settings.getWithDateFormat("/path/to/current_date", "{dd}/{mm}/{yyyy}")

# => 19/07/2018
date = settings.getWithDateFormat("/path/to/tomorrow_date"
                "{tomorrow_dd}/{tomorrow_mm}/{tomorrow_yyyy}")

# => 17/07/2018
date = settings.getWithDateFormat("/path/to/yesterday_date", 
                "{yesterday_dd}/{yesterday_mm}/{yesterday_yyyy}")

# sample
{'data': [{'ident': 'name1', 'rows': [{'key': 1}, {'key': 2}]},
          {'ident': 'name2', 'rows': [{'key': 3}, {'key': 4}]}]}
settings.get("/data[1]/rows[0]/key") => 3
settings.get("/data[0]/rows") => [{'key': 1}, {'key': 2}]
```

Usage for email
```python
# Using email object
from mblibs.fast import FastEmail

# email body
body = """
<p>Lorem <em><strong>ipsum</strong></em> dolor !</p>

<p>Ceci est un message de test de l&#39;application</p>

<img class="picture" src="cid:graphic1" alt="Graphique en pi&egrave;ce jointe" />

<p>Merci pour le graphique&nbsp;<br />
Mick</p>

<img class="picture" src="cid:graphic2" alt="Graphique en pi&egrave;ce jointe" />
"""

# init email object
mailer = FastEmail()
mailer.mail_from = settings.get("/smtp/mail_from")
mailer.mail_subject = "A subject for the mail."
mailer.mail_text = 'Merci de lire le message depuis un lecteur acceptant le HTML.'
mailer.mail_html = body
mailer.smtp_host = "localhost"
mailer.smtp_port = 25
mailer.smtp_tls = False
mailer.smtp_login = ""
mailer.smtp_password = ""

# send email
To = ["mail1@mail.mx", "mail2@mail.mx"]
Cc = ["mail3@mail.mx"]
Bcc = ["mail4@mail.mx", "mail5@mail.mx"]

filename = "./ridev.png"
ret = mailer.send_mail(to=To, cc=Cc, bcc=Bcc, attachfiles=[filename],
                       embeddedimages_tag="graphic",
                       embeddedimages=["./python.png", filename])
```
