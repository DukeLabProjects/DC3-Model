from dc3 import decode_dc3, encode_dc3


def test_all_non_z_labels_encode_and_decode():
    expected_code = 1
    for letter in ["A", "B", "C", "D", "E", "F", "G"]:
        for label in [f"{letter}-", letter, f"{letter}+"]:
            assert encode_dc3(label) == expected_code
            assert decode_dc3(expected_code)["label"] == label
            expected_code += 1


def test_z_label_encode_and_decode():
    assert encode_dc3("Z") == 22
    assert decode_dc3(22)["label"] == "Z"

