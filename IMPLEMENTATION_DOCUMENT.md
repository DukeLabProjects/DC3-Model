# DC3 Model Implementation Document

## 1. Project Purpose

DC3 Model will provide a reusable Python implementation of the D-centred thermal comfort classification model. The project will support three audiences:

- Researchers who want to classify thermal comfort observations using the DC3 framework.
- Engineers and developers who want a stable Python API for batch processing and model integration.
- End users who want to upload sample data, map their own column names to DC3 concepts, process the data, and explore outputs through visualisations and filters.

The project will be organised so that the scientific model lives in a clean Python package, while documentation and the user-facing app consume that package rather than duplicating logic.

## 2. Core Model Summary

The implementation will preserve the rules described in the paper.

### 2.1 Observed Comfort

Observed Comfort, abbreviated as OC, is a binary operational metric.

A record is classified as comfortable only when:

```text
thermal_preference == "no_change"
thermal_acceptability == 1
```

All other combinations are classified as uncomfortable.

### 2.2 Thermal Sensation Letter Mapping

Thermal sensation values are mapped onto seven DC3 letter classes:

| Thermal Sensation | Label | Meaning |
| --- | --- | --- |
| -3 | A | cold |
| -2 | B | cool |
| -1 | C | slightly cool |
| 0 | D | neutral |
| 1 | E | slightly warm |
| 2 | F | warm |
| 3 | G | hot |

The DC3 scale is centred on `D`, corresponding to neutral thermal sensation.

### 2.3 Preference Suffixes

Preference and acceptability determine whether a label receives a suffix.

| Preference / Acceptability Condition | DC3 Form |
| --- | --- |
| no_change and acceptable | unsigned label, for example `D` |
| cooler preference and uncomfortable | minus suffix, for example `E-` |
| warmer preference and uncomfortable | plus suffix, for example `C+` |
| no_change and unacceptable | `Z` |

The `Z` class is a flag category for inconsistent, ambiguous, or semantically mixed responses. The package should preserve `Z` by default rather than silently reclassifying it.

### 2.4 Numeric Encoding

Each non-Z DC3 state can be represented by a numeric code:

```text
dc3_code = 3 * thermal_sensation_index + preference_group
```

where:

```text
thermal_sensation_index = 0..6
cooler preference = 1
no_change / comfortable = 2
warmer preference = 3
Z = 22
```

Examples:

| Label | Calculation | Code |
| --- | --- | --- |
| A- | 3 * 0 + 1 | 1 |
| D | 3 * 3 + 2 | 11 |
| G+ | 3 * 6 + 3 | 21 |
| Z | reserved | 22 |

## 3. Project Architecture

The project will use a `src/` layout.

```text
DC3-Model/
  pyproject.toml
  README.md
  LICENSE
  CHANGELOG.md
  IMPLEMENTATION_DOCUMENT.md
  src/
    dc3/
      __init__.py
      core.py
      schema.py
      preprocessing.py
      batch.py
      ml.py
      metrics.py
      viz.py
      exceptions.py
      datasets.py
      app/
        __init__.py
        streamlit_app.py
  docs/
    conf.py
    index.rst
    quickstart.rst
    model.rst
    data_mapping.rst
    api.rst
    examples.rst
    app.rst
  examples/
    classify_single_record.py
    process_csv.py
    train_random_forest.py
  tests/
    test_core.py
    test_encoding.py
    test_preprocessing.py
    test_batch.py
    test_ml.py
```

## 4. Python Package Responsibilities

### 4.1 `core.py`

Contains the deterministic DC3 model.

Primary responsibilities:

- Compute observed comfort.
- Convert thermal sensation values to letter labels.
- Classify a single observation into a DC3 label.
- Encode a DC3 label into a numeric code.
- Decode a numeric code back into model components.
- Provide helper descriptions for classes and intervention direction.

Expected public functions:

```python
observed_comfort(thermal_preference, thermal_acceptability) -> bool
thermal_sensation_label(thermal_sensation) -> str
classify_dc3(thermal_sensation, thermal_preference, thermal_acceptability) -> str
encode_dc3(label) -> int
decode_dc3(code) -> dict
describe_dc3(label) -> dict
```

### 4.2 `schema.py`

Defines accepted field names, categories, canonical values, and validation rules.

Responsibilities:

- Define valid thermal sensation values: `-3, -2, -1, 0, 1, 2, 3`.
- Define canonical thermal preference values: `cooler`, `no_change`, `warmer`.
- Define canonical thermal acceptability values: `0, 1`.
- Provide column mapping structures for batch processing and the app.
- Provide clear error messages for invalid inputs.

### 4.3 `preprocessing.py`

Normalises user data.

Responsibilities:

- Convert user-entered preference labels into canonical values.
- Handle common variants such as `no change`, `no-change`, `neutral`, `same`, `cooler`, `prefer cooler`, `warmer`, and `prefer warmer`.
- Convert acceptability values such as `acceptable`, `unacceptable`, `yes`, `no`, `true`, `false`, `1`, and `0`.
- Coerce thermal sensation values into integers when valid.
- Identify missing or invalid values without losing the original data.

### 4.4 `batch.py`

Provides dataframe-level processing.

Expected public functions:

```python
process_dataframe(df, columns, *, keep_invalid=True) -> pandas.DataFrame
validate_dataframe(df, columns) -> ValidationReport
summarise_dc3(df) -> pandas.DataFrame
```

Generated output columns should include:

```text
observed_comfort
dc3_label
dc3_code
thermal_sensation_label
preference_group
comfort_zone
recommended_direction
is_z_class
dc3_valid
dc3_error
```

### 4.5 `ml.py`

Contains optional machine learning utilities.

Responsibilities:

- Train Random Forest classifiers for OC, OTC, and DC3 targets.
- Reproduce the modelling scenarios from the paper where data permits.
- Provide cross-validation helpers.
- Compute permutation feature importance.
- Save and load trained models.

Potential public classes and functions:

```python
DC3RandomForestClassifier
train_random_forest(...)
cross_validate_model(...)
permutation_importance_report(...)
save_model(...)
load_model(...)
```

Important interpretation note:

When subjective inputs such as thermal sensation and thermal preference are used to predict DC3, the model is partly reconstructing deterministic labels. Documentation must be explicit about this so users do not misinterpret high accuracy as fully independent prediction from environmental data alone.

### 4.6 `metrics.py`

Provides evaluation utilities.

Responsibilities:

- Accuracy.
- Macro precision.
- Macro recall.
- Macro F1.
- Confusion matrices.
- Class distribution tables.
- Support per class.

### 4.7 `viz.py`

Provides reusable visualisation functions.

Initial visualisations:

- DC3 class frequency bar chart.
- DC3 7-by-3 matrix / triangle-style view.
- Temperature distribution by DC3 class.
- Relative humidity distribution by DC3 class.
- Air velocity distribution by DC3 class.
- City and season comfort signatures.
- Z-class inspection summaries.

The package should return figure objects rather than directly displaying plots where possible, so the same utilities can be used in notebooks, documentation, and the app.

### 4.8 `datasets.py`

Provides sample data helpers.

Responsibilities:

- Load bundled sample datasets.
- Provide synthetic demo data if no public sample data is bundled.
- Document expected schema.

## 5. Public API Design

The package should expose a small set of common functions from `dc3.__init__`.

Example single-record usage:

```python
from dc3 import classify_dc3, encode_dc3, decode_dc3, observed_comfort

oc = observed_comfort(
    thermal_preference="no_change",
    thermal_acceptability=1,
)

label = classify_dc3(
    thermal_sensation=0,
    thermal_preference="no_change",
    thermal_acceptability=1,
)

code = encode_dc3(label)
decoded = decode_dc3(code)
```

Example batch usage:

```python
from dc3 import process_dataframe

processed = process_dataframe(
    df,
    columns={
        "thermal_sensation": "Thermal sensation",
        "thermal_preference": "Thermal preference",
        "thermal_acceptability": "Thermal acceptability",
        "air_temperature": "Air temperature",
        "relative_humidity": "Relative humidity",
        "air_velocity": "Air velocity",
    },
)
```

## 6. User-Facing App

The first user-facing app should be built with Streamlit because it is fast to develop, Python-native, and suitable for research workflows.

### 6.1 App Workflow

1. Upload CSV or XLSX file.
2. Preview imported data.
3. Map user columns to DC3 fields.
4. Normalise values and validate records.
5. Process data through the DC3 package.
6. Display summary metrics.
7. Explore visualisations and filters.
8. Export processed data and reports.

### 6.2 Required Mapping Fields

Minimum required fields for deterministic DC3 classification:

```text
thermal_sensation
thermal_preference
thermal_acceptability
```

Optional analysis fields:

```text
air_temperature
relative_humidity
air_velocity
city
season
building_type
cooling_strategy
clo
met
pmv
thermal_comfort
```

### 6.3 App Views

Recommended first version views:

- Data import.
- Column mapping.
- Validation report.
- DC3 overview dashboard.
- Distribution explorer.
- Environmental variable explorer.
- Z-class review.
- Export.

### 6.4 App Filters

Recommended filters:

- DC3 class.
- Comfort / discomfort.
- Z-class only.
- City.
- Season.
- Building type.
- Cooling strategy.
- Temperature range.
- Humidity range.
- Air velocity range.

## 7. Sphinx Documentation

Sphinx documentation should be created early and maintained alongside the package.

### 7.1 Recommended Extensions

```text
sphinx.ext.autodoc
sphinx.ext.autosummary
sphinx.ext.napoleon
sphinx.ext.viewcode
myst_parser
sphinx_copybutton
```

Potential theme:

```text
furo
```

### 7.2 Documentation Pages

```text
index.rst
quickstart.rst
model.rst
data_mapping.rst
api.rst
examples.rst
app.rst
```

### 7.3 Documentation Principles

- Model equations and rules should be written manually in `model.rst`.
- Function and class references should be generated from docstrings.
- Examples should be executable where possible.
- The app guide should use the same terminology as the Python API.
- Any future correction to the model rules should update both tests and documentation.

## 8. Testing Strategy

Testing should begin with the deterministic rules.

### 8.1 Core Tests

Test cases should verify:

- Every thermal sensation value maps to the correct letter.
- All 21 DC3 non-Z labels can be encoded and decoded.
- `Z` maps to code `22`.
- Comfortable records produce unsigned labels.
- Cooler preference records produce `-` labels.
- Warmer preference records produce `+` labels.
- No-change plus unacceptable records produce `Z`.
- Invalid values raise clear exceptions.

### 8.2 Batch Tests

Test cases should verify:

- Dataframe processing preserves row order.
- Required columns are enforced.
- User column mappings work.
- Invalid rows can be retained with error metadata.
- Invalid rows can be dropped when requested.

### 8.3 ML Tests

Test cases should verify:

- Training runs on a small sample dataset.
- Cross-validation returns expected metric keys.
- Prediction output length matches input length.
- Model save and load works.

### 8.4 Documentation Tests

The documentation build should be checked with:

```bash
sphinx-build -b html docs docs/_build/html
```

## 9. Development Phases

### Phase 1: Project Scaffold

Deliverables:

- `pyproject.toml`
- package skeleton under `src/dc3`
- initial tests
- README
- basic Sphinx structure

### Phase 2: Deterministic DC3 Engine

Deliverables:

- observed comfort function
- single-record DC3 classifier
- encoder and decoder
- descriptive metadata
- full unit tests for all DC3 states

### Phase 3: Dataframe Processing

Deliverables:

- column mapping
- preprocessing
- validation report
- batch classification
- output summary tables

### Phase 4: Visualisation Utilities

Deliverables:

- class distribution chart
- DC3 matrix view
- environmental distribution plots
- Z-class summaries

### Phase 5: Machine Learning Utilities

Deliverables:

- Random Forest wrapper
- cross-validation helper
- metrics report
- feature importance helper
- model persistence

### Phase 6: Sphinx Documentation

Deliverables:

- quickstart
- model specification
- API docs
- examples
- app documentation
- local HTML build verification

### Phase 7: Streamlit App

Deliverables:

- upload workflow
- column mapping UI
- validation UI
- DC3 dashboard
- filters
- visualisations
- export processed CSV

### Phase 8: Packaging And Release Readiness

Deliverables:

- versioning
- package metadata
- changelog
- distribution build
- installation instructions
- optional publish workflow

## 10. Initial Dependency Plan

Core package dependencies:

```text
pandas
numpy
scikit-learn
joblib
```

Visualisation dependencies:

```text
matplotlib
seaborn
plotly
```

App dependencies:

```text
streamlit
openpyxl
```

Documentation dependencies:

```text
sphinx
furo
myst-parser
sphinx-copybutton
```

Testing dependencies:

```text
pytest
pytest-cov
```

## 11. Open Decisions

These should be confirmed before or during early implementation:

- Whether the package name should be imported as `dc3` or `dc3_project`.
- Whether `thermal_acceptability == 1` always means acceptable across all user datasets, or whether users should be allowed to configure this mapping.
- Whether Z-class reclassification should be implemented in version 1 or reserved for a later release.
- Whether the first app should be Streamlit only, or whether a later web app should be planned with FastAPI and React.
- Whether sample data can be bundled, or whether synthetic demo data should be used until data licensing is confirmed.
- Whether the project will eventually be published to PyPI.

## 12. Recommended Starting Point

The recommended next step is Phase 1 followed immediately by Phase 2.

The first working milestone should allow:

```python
from dc3 import classify_dc3, encode_dc3, decode_dc3, observed_comfort

label = classify_dc3(
    thermal_sensation=0,
    thermal_preference="no_change",
    thermal_acceptability=1,
)

assert label == "D"
assert encode_dc3(label) == 11
```

Once this is tested, dataframe processing, documentation, visualisation, machine learning, and the app can build on a stable foundation.
