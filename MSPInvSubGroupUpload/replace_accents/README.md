# Clean dem' accents

https://www.accentletters.com/accent-o.html


```python
import re
def f_remove_accents(old):
    """
    https://stackoverflow.com/a/69099798
    https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-normalize-in-a-python-unicode-string
    Removes common accent characters
    Uses: regex.
    """
    new = re.sub(r'[àáâãäå]', 'a', old)
    new = re.sub(r'[ÀÁÂÃ]', 'A', new)
    new = re.sub(r'[èéêë]', 'e', new)
    new = re.sub(r'[ËÉÈÊ]', 'E', new)
    new = re.sub(r'[ìíîï]', 'i', new)
    new = re.sub(r'[ÏÍÌÎ]', 'I', new)
    new = re.sub(r'[òóôõö]', 'o', new)
    new = re.sub(r'[ÖÔÓÒ]', 'O', new)
    new = re.sub(r'[ùúûü]', 'u', new)
    new = re.sub(r'[ÛÚÙÜ]', 'U', new)
    new = re.sub(r'[ñńņň]', 'n', new)
    new = re.sub(r'[ÑŃŅŇ]', 'N', new)
    return new
```

Still having issues... �
