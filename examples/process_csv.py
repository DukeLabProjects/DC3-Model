import pandas as pd

from dc3 import process_dataframe, summarise_dc3


df = pd.DataFrame(
    {
        "TS": [0, "slightly warm", 3],
        "Pref": ["no change", "prefer cooler", "no_change"],
        "Accept": ["acceptable", 1, 0],
    }
)

processed = process_dataframe(
    df,
    columns={
        "thermal_sensation": "TS",
        "thermal_preference": "Pref",
        "thermal_acceptability": "Accept",
    },
)

print(processed)
print(summarise_dc3(processed))

