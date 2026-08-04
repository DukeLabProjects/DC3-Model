from dc3 import classify_dc3, decode_dc3, encode_dc3


label = classify_dc3(
    thermal_sensation=0,
    thermal_preference="no_change",
    thermal_acceptability=1,
)

code = encode_dc3(label)
description = decode_dc3(code)

print(label)
print(code)
print(description)

