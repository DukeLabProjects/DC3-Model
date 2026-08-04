# DC3 Model

DC3 Model is a Python implementation of the D-centred thermal comfort classification model. It provides:

- deterministic DC3 classification rules,
- robust single-record and dataframe processing,
- explicit validation and error reporting,
- optional machine learning utilities,
- Sphinx package documentation.

The package is currently in early development. The first implementation milestone focuses on the deterministic DC3 engine and reliable dataset handling.

## Quick Example

```python
from dc3 import classify_dc3, encode_dc3, decode_dc3

label = classify_dc3(
    thermal_sensation=0,
    thermal_preference="no_change",
    thermal_acceptability=1,
)

assert label == "D"
assert encode_dc3(label) == 11
assert decode_dc3(11)["label"] == "D"
```

## Local Development

```bash
python -m pip install -e .[test,docs]
pytest
sphinx-build -b html docs docs/_build/html
```

Install optional extras when needed:

```bash
python -m pip install -e .[ml,viz,docs,test]
```

The package documentation lives in `docs/`.

The Streamlit user-facing app now lives in the sibling `DC3-App` project so it
can be hosted, versioned, and cited separately from the reusable Python
package.
