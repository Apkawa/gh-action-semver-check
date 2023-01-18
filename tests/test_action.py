import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import yaml

import entrypoint


@patch.dict(os.environ, {"GITHUB_REF": "refs/tags/v1.2.3a1"})
def test_with_default():
    tf = tempfile.NamedTemporaryFile("r")
    os.environ["GITHUB_OUTPUT"] = tf.name
    with patch.object(sys, "argv", ["foo.py"]):
        entrypoint.main()

    tf.flush()
    expected = """
is_valid=true
is_stable=false
is_unstable=true
is_prerelease=true
is_devrelease=false
is_postrelease=false
full=1.2.3a1
full_with_prefix=v1.2.3a1
epoch=0
major=1
minor=2
patch=3
major_with_prefix=v1
prerelease=a1
prerelease_phase=a
prerelease_number=1
"""
    assert tf.read().strip() == expected.strip()


@patch.dict(os.environ, {"GITHUB_REF": "refs/tags/v1.2.3a1"})
def test_with_default_2():
    tf = tempfile.NamedTemporaryFile("r")
    os.environ["GITHUB_OUTPUT"] = tf.name
    with patch.object(
        sys, "argv", ["foo.py", "raw=null", "prefix=null", "version_prefix=null"]
    ):
        entrypoint.main()

    tf.flush()
    expected = """
is_valid=true
is_stable=false
is_unstable=true
is_prerelease=true
is_devrelease=false
is_postrelease=false
full=1.2.3a1
full_with_prefix=v1.2.3a1
epoch=0
major=1
minor=2
patch=3
major_with_prefix=v1
prerelease=a1
prerelease_phase=a
prerelease_number=1
"""
    assert tf.read().strip() == expected.strip()


@patch.dict(os.environ, {"GITHUB_REF": "refs/tags/v0.0.0"})
def test_manual_pass_raw():
    # This env must be ignored
    tf = tempfile.NamedTemporaryFile("r")
    os.environ["GITHUB_OUTPUT"] = tf.name
    with patch.object(
        sys,
        "argv",
        ["foo.py", 'raw="refs/tags/v1.2.3a1"', "prefix=null", "version_prefix=null"],
    ):
        entrypoint.main()

    tf.flush()
    expected = """
is_valid=true
is_stable=false
is_unstable=true
is_prerelease=true
is_devrelease=false
is_postrelease=false
full=1.2.3a1
full_with_prefix=v1.2.3a1
epoch=0
major=1
minor=2
patch=3
major_with_prefix=v1
prerelease=a1
prerelease_phase=a
prerelease_number=1
"""
    assert tf.read().strip() == expected.strip()


@patch.dict(os.environ, {"GITHUB_REF": "refs/tags/v0.0.0"})
def test_manual_pass_version():
    # This env must be ignored
    tf = tempfile.NamedTemporaryFile("r")
    os.environ["GITHUB_OUTPUT"] = tf.name
    with patch.object(
        sys,
        "argv",
        ["foo.py", 'raw="v1.2.3a1"', "prefix=", "version_prefix=null"],
    ):
        entrypoint.main()

    tf.flush()
    expected = """
is_valid=true
is_stable=false
is_unstable=true
is_prerelease=true
is_devrelease=false
is_postrelease=false
full=1.2.3a1
full_with_prefix=v1.2.3a1
epoch=0
major=1
minor=2
patch=3
major_with_prefix=v1
prerelease=a1
prerelease_phase=a
prerelease_number=1
"""
    assert tf.read().strip() == expected.strip()


def test_without_params():
    tf = tempfile.NamedTemporaryFile("r")
    os.environ["GITHUB_OUTPUT"] = tf.name
    with patch.object(
        sys, "argv", ["foo.py", "raw=null", "prefix=null", "version_prefix=null"]
    ):
        entrypoint.main()

    tf.flush()
    expected = """
is_valid=false
"""
    assert tf.read().strip() == expected.strip()


def test_action_spec():
    version_with_all_parts = "6!2.3.4a1post2dev1+rev1234.123.123"
    tf = tempfile.NamedTemporaryFile("r")
    os.environ["GITHUB_OUTPUT"] = tf.name
    with patch.object(
        sys,
        "argv",
        ["foo.py", f"raw={version_with_all_parts}", "prefix=", "version_prefix=null"],
    ):
        entrypoint.main()

    tf.flush()
    expected = (
        "is_valid=true\n"
        "is_stable=false\n"
        "is_unstable=true\n"
        "is_prerelease=true\n"
        "is_devrelease=true\n"
        "is_postrelease=true\n"
        "full=6!2.3.4a1post2dev1+rev1234.123.123\n"
        "full_with_prefix=6!2.3.4a1post2dev1+rev1234.123.123\n"
        "epoch=6\n"
        "major=2\n"
        "minor=3\n"
        "patch=4\n"
        "major_with_prefix=2\n"
        "prerelease=a1\n"
        "prerelease_phase=a\n"
        "prerelease_number=1\n"
        "dev=1\n"
        "post=2\n"
        "local=rev1234.123.123"
    )
    result = tf.read().strip()
    assert result == expected.strip()

    # Compare result with action spec
    action_file = (Path(__file__).parent.parent / "action.yml").absolute()
    with open(action_file, "r", encoding="utf8") as f:
        action_data = yaml.load(f, yaml.SafeLoader)
    outputs_names = set(action_data["outputs"].keys())
    result_keys = set([l.split("=")[0].strip() for l in result.splitlines()])

    assert outputs_names == result_keys
