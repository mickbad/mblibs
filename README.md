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
date = settings("/path/to/current_date", "{dd}/{mm}/{yyyy}")

# => 19/07/2018
date = settings("/path/to/tomorrow_date"
                "{tomorrow_dd}/{tomorrow_mm}/{tomorrow_yyyy}")

# => 17/07/2018
date = settings("/path/to/yesterday_date", 
                "{yesterday_dd}/{yesterday_mm}/{yesterday_yyyy}")

```
