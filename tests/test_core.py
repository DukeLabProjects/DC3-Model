import pytest

from dc3 import (
    DC3InputError,
    classify_dc3,
    dc3_codebook,
    decode_dc3,
    describe_dc3,
    encode_dc3,
    observed_comfort,
    thermal_sensation_label,
)


@pytest.mark.parametrize(
    ("sensation", "label"),
    [
        (-3, "A"),
        (-2, "B"),
        (-1, "C"),
        (0, "D"),
        (1, "E"),
        (2, "F"),
        (3, "G"),
    ],
)
def test_thermal_sensation_label(sensation, label):
    assert thermal_sensation_label(sensation) == label


def test_observed_comfort_rule():
    assert observed_comfort("no_change", 1) is True
    assert observed_comfort("no change", "acceptable") is True
    assert observed_comfort("cooler", 1) is False
    assert observed_comfort("warmer", 1) is False
    assert observed_comfort("no_change", 0) is False


@pytest.mark.parametrize(
    ("sensation", "preference", "acceptability", "expected"),
    [
        (-3, "no_change", 1, "A"),
        (-2, "no_change", 1, "B"),
        (-1, "no_change", 1, "C"),
        (0, "no_change", 1, "D"),
        (1, "no_change", 1, "E"),
        (2, "no_change", 1, "F"),
        (3, "no_change", 1, "G"),
        (1, "cooler", 1, "E-"),
        (-1, "warmer", 1, "C+"),
        (0, "no_change", 0, "Z"),
    ],
)
def test_classify_dc3(sensation, preference, acceptability, expected):
    assert classify_dc3(sensation, preference, acceptability) == expected


def test_classify_dc3_accepts_common_text_variants():
    assert classify_dc3("slightly warm", "prefer cooler", "acceptable") == "E-"
    assert classify_dc3("neutral", "same", "yes") == "D"
    assert classify_dc3("cold", "want warmer", "no") == "A+"


def test_describe_dc3():
    description = describe_dc3("D")
    assert description["code"] == 11
    assert description["thermal_sensation"] == 0
    assert description["observed_comfort"] is True
    assert description["recommended_direction"] == "maintain"


def test_describe_z_class():
    description = describe_dc3("Z")
    assert description["code"] == 22
    assert description["observed_comfort"] is False
    assert description["is_z_class"] is True
    assert description["recommended_direction"] == "review_response"


def test_invalid_inputs_raise_clear_errors():
    with pytest.raises(DC3InputError):
        classify_dc3(4, "no_change", 1)
    with pytest.raises(DC3InputError):
        classify_dc3(0, "unknown", 1)
    with pytest.raises(DC3InputError):
        classify_dc3(0, "no_change", "maybe")


def test_decode_rejects_invalid_codes():
    with pytest.raises(DC3InputError):
        decode_dc3(0)
    with pytest.raises(DC3InputError):
        decode_dc3(23)
    with pytest.raises(DC3InputError):
        encode_dc3("Q")


def test_dc3_codebook_outputs_labels_and_numeric_equivalence():
    codebook = dc3_codebook()
    assert len(codebook) == 22
    lookup = {row["dc3_label"]: row["dc3_code"] for row in codebook}
    assert lookup["A-"] == 1
    assert lookup["D"] == 11
    assert lookup["G+"] == 21
    assert lookup["Z"] == 22
