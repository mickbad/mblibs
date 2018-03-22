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
```
