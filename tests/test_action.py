import os
import sys
import tempfile
from unittest.mock import patch

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
