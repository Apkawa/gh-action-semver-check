import os
import sys
import tempfile
from unittest.mock import patch

import entrypoint


def test_main():
    os.environ["GITHUB_REF"] = "refs/tags/v1.2.3a1"
    tf = tempfile.NamedTemporaryFile("r")
    os.environ["GITHUB_OUTPUT"] = tf.name
    with patch.object(sys, "argv", ["foo.py", "prefix=v"]) as p:
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
