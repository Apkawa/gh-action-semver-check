#!/usr/bin/env -S python3 -B

import re
import sys
import os
from typing import Dict, List, TextIO, Optional, Union
import json

from poetry.core.constraints.version import Version

__version__ = "0.0.0"


def parse_argv(argv: List[str]) -> Dict:
    """
    >>> parse_argv(['a=1', 'b=foobar', 'c="   fooo bar   "'])
    {'a': 1, 'b': 'foobar', 'c': '   fooo bar   '}
    >>> parse_argv(['a  =  1', 'b  =  foobar', "c =   'baz'"])
    {'a': 1, 'b': 'foobar', 'c': 'baz'}
    >>> parse_argv(['a  =  true', 'b  =  null', "c =   'null'", 'd='])
    {'a': True, 'b': None, 'c': 'null', 'd': ''}

    :param argv:
    :return:
    """
    parsed = {}
    for p in argv:
        k, v = p.split("=")
        k = k.strip()
        try:
            parsed[k] = json.loads(v)
        except json.JSONDecodeError:
            parsed[k] = v.strip().strip("'")
    return parsed


def parse_version(version_string: Optional[str], prefix: Optional[str] = None) -> Dict:
    """
    >>> parse_version("1.2", 'v')
    {'is_valid': False}
    >>> parse_version("sdfsf")
    {'is_valid': False}
    >>> parse_version('v0.2.3', 'v')
    {'is_valid': True, 'is_stable': True, 'is_unstable': False, 'is_prerelease': False, \
'is_devrelease': False, 'is_postrelease': False, 'full': '0.2.3', \
'full_with_prefix': 'v0.2.3', 'epoch': 0, 'major': 0, 'minor': 2, 'patch': 3, \
'major_with_prefix': 'v0'}
    >>> parse_version('v1.2.3a4', 'v')
    {'is_valid': True, 'is_stable': False, 'is_unstable': True, 'is_prerelease': True, \
'is_devrelease': False, 'is_postrelease': False, 'full': '1.2.3a4', \
'full_with_prefix': 'v1.2.3a4', 'epoch': 0, 'major': 1, 'minor': 2, 'patch': 3, \
'major_with_prefix': 'v1', 'prerelease': 'a4', \
'prerelease_phase': 'a', 'prerelease_number': 4}

    >>> parse_version('v1.2.3a4+foo123.bar456', 'v')
    {'is_valid': True, 'is_stable': False, 'is_unstable': True, 'is_prerelease': True, \
'is_devrelease': False, 'is_postrelease': False, 'full': '1.2.3a4+foo123.bar456', \
'full_with_prefix': 'v1.2.3a4+foo123.bar456', 'epoch': 0, 'major': 1, 'minor': 2, \
'patch': 3, 'major_with_prefix': 'v1', 'prerelease': 'a4', 'prerelease_phase': 'a', \
'prerelease_number': 4, 'local': 'foo123.bar456'}

    :param version_string:
    :param prefix:
    :return:
    """
    result: Dict[str, Union[bool, str, int]] = dict(is_valid=False)

    if not version_string:
        return result
    if prefix is None:
        prefix = "v" if version_string.startswith("v") else ""
    if not version_string.startswith(prefix):
        return result
    prefix_len = len(prefix)
    version_string = version_string[prefix_len:]
    try:
        parsed = Version.parse(version_string)
    except ValueError:
        return result
    result["is_valid"] = True
    for f in [
        "is_stable",
        "is_unstable",
        "is_prerelease",
        "is_devrelease",
        "is_postrelease",
    ]:
        result[f] = getattr(parsed, f)()
    result["full"] = parsed.text
    result["full_with_prefix"] = f"{prefix}{version_string}"
    for p in ["epoch", "major", "minor", "patch"]:
        result[p] = getattr(parsed, p)
    result["major_with_prefix"] = f"{prefix}{parsed.major}"
    if parsed.is_prerelease() and parsed.pre:
        result["prerelease"] = parsed.pre.to_string()
        result["prerelease_phase"] = parsed.pre.phase
        result["prerelease_number"] = parsed.pre.number

    if parsed.is_devrelease() and parsed.dev:
        result["dev"] = parsed.dev.number
    if parsed.is_postrelease() and parsed.post:
        result["post"] = parsed.post.number

    if parsed.local:
        if isinstance(parsed.local, (list, tuple)):
            result["local"] = ".".join([str(v) for v in parsed.local])
        else:
            result["local"] = parsed.local
    return result


REF_REGEXP = re.compile("^refs/tags/(.*)$")


def get_version_tag_from_github_env(
    raw: Optional[str] = None, prefix: Optional[str] = None
) -> Optional[str]:
    """
    >>> get_version_tag_from_github_env()
    >>> get_version_tag_from_github_env('refs/tags/v1.2.3')
    'v1.2.3'
    >>> get_version_tag_from_github_env('foobar/v1.2.3', 'foobar/')
    'v1.2.3'
    >>> os.environ['GITHUB_REF'] = 'refs/tags/v1.2.3'
    >>> get_version_tag_from_github_env()
    'v1.2.3'
    >>> os.environ['GITHUB_REF'] = 'refs/branch/master'
    >>> get_version_tag_from_github_env()

    :return:
    """
    if prefix is None:
        prefix = "refs/tags/"
    if raw is None:
        raw = os.environ.get("GITHUB_REF") or ""
    if raw.startswith(prefix):
        prefix_len = len(prefix)
        return raw[prefix_len:]
    return None


def write_output(output: Dict, _file: TextIO) -> None:
    """
    >>> write_output(dict(foo='bar', a=1), sys.stdout)
    foo="bar"
    a=1

    :param output:
    :param _file:
    :return:
    """
    for k, v in output.items():
        if isinstance(v, bool):
            v = json.dumps(v)
        else:
            v = str(v)
        if "\n" in v:
            print(f"{k}<<EOF", file=_file)
            print(v, file=_file)
            print("EOF", file=_file)
        else:
            print(f"{k}={v}", file=_file)


def main() -> None:
    args = parse_argv(sys.argv[1:])
    version_raw = args.get("raw") or None
    prefix = args.get("prefix")
    version_prefix = args.get("verson_prefix")
    version = get_version_tag_from_github_env(raw=version_raw, prefix=prefix)

    output = parse_version(version, prefix=version_prefix)

    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a", encoding="utf8") as f:
            write_output(output, f)
    else:
        write_output(output, sys.stdout)


if __name__ == "__main__":
    # Rename these variables to something meaningful
    main()
