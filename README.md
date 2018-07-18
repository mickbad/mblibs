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
date = settings.get("/path/to/current_date", "{dd}/{mm}/{yyyy}")

# => 19/07/2018
date = settings.get("/path/to/tomorrow_date"
                "{tomorrow_dd}/{tomorrow_mm}/{tomorrow_yyyy}")

# => 17/07/2018
date = settings.get("/path/to/yesterday_date", 
                "{yesterday_dd}/{yesterday_mm}/{yesterday_yyyy}")

# sample
{'data': [{'ident': 'name1', 'rows': [{'key': 1}, {'key': 2}]},
          {'ident': 'name2', 'rows': [{'key': 3}, {'key': 4}]}]}
settings.get("/data[1]/rows[0]/key") => 3
settings.get("/data[0]/rows") => [{'key': 1}, {'key': 2}]

```
