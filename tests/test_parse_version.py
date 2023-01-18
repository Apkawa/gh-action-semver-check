import pytest

from entrypoint import parse_version


@pytest.mark.parametrize(
    "version",
    [
        "v1.0.0",
        "v2.3.4",
        "99.999.9999",
        "99.999.9999+0354f3a",
        "v2.3.4.5",
        "99.999.9999.99999",
    ],
)
def test_valid(version):
    parsed = parse_version(version_string=version)
    assert parsed["is_valid"]


@pytest.mark.parametrize(
    "version",
    [
        "99.999.9999-SNAPSHOT",
        "99.999.9999-SNAPSHOT+0354f3a",
    ],
)
def test_invalid(version):
    parsed = parse_version(version_string=version)
    assert not parsed["is_valid"]


@pytest.mark.parametrize(
    "version",
    [
        "v0.1.0",
        "v1.0.0",
        "v2.3.4",
        "99.999.9999",
        "99.999.9999+0354f3a",
        "v2.3.4-post1",
        "v2.3.4post",
    ],
)
def test_is_stable(version):
    parsed = parse_version(version_string=version)
    assert parsed["is_stable"]


@pytest.mark.parametrize(
    "version",
    [
        "v2.3.4a1",
        "v1.0.0-alpha",
        "v2.3.4-beta5",
        "v2.3.4-dev1",
    ],
)
def test_is_unstable(version):
    parsed = parse_version(version_string=version)
    assert parsed["is_unstable"]


@pytest.mark.parametrize(
    "version,expected",
    [
        ["v2.3.4a1", "a1"],
        ["v1.0.0-alpha", "a0"],
        ["v2.3.4-beta5", "b5"],
    ],
)
def test_prerelease(version, expected):
    parsed = parse_version(version_string=version)
    assert parsed["is_unstable"]
    assert parsed["is_prerelease"]
    assert parsed["prerelease"] == expected


@pytest.mark.parametrize(
    "version,expected",
    [
        [
            "v2.3.4",
            dict(
                epoch=0,
                full="2.3.4",
                full_with_prefix="v2.3.4",
                is_devrelease=False,
                is_postrelease=False,
                is_prerelease=False,
                is_stable=True,
                is_unstable=False,
                is_valid=True,
                major=2,
                major_with_prefix="v2",
                minor=3,
                patch=4,
            ),
        ],
        [
            "v1.0.0-alpha",
            dict(
                epoch=0,
                full="1.0.0-alpha",
                full_with_prefix="v1.0.0-alpha",
                is_devrelease=False,
                is_postrelease=False,
                is_prerelease=True,
                is_stable=False,
                is_unstable=True,
                is_valid=True,
                major=1,
                major_with_prefix="v1",
                minor=0,
                patch=0,
                prerelease="a0",
                prerelease_number=0,
                prerelease_phase="a",
            ),
        ],
        [
            "6!2.3.4a1post2dev1+rev1234.123.123",
            dict(
                dev=1,
                epoch=6,
                full="6!2.3.4a1post2dev1+rev1234.123.123",
                full_with_prefix="6!2.3.4a1post2dev1+rev1234.123.123",
                is_devrelease=True,
                is_postrelease=True,
                is_prerelease=True,
                is_stable=False,
                is_unstable=True,
                is_valid=True,
                local="rev1234.123.123",
                major=2,
                major_with_prefix="2",
                minor=3,
                patch=4,
                post=2,
                prerelease="a1",
                prerelease_number=1,
                prerelease_phase="a",
            ),
        ],
    ],
)
def test_parsed(version, expected):
    parsed = parse_version(version_string=version)
    assert parsed == expected
