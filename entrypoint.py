#!/usr/bin/env -S python3 -B

import re
import sys
import os
from typing import Dict, List, TextIO, Optional
import json

import semver
from semver.exceptions import ParseVersionError


def parse_argv(argv: List[str]) -> Dict:
    """
    >>> parse_argv(['a=1', 'b=foobar', 'c="   fooo bar   "'])
    {'a': 1, 'b': 'foobar', 'c': '   fooo bar   '}
    >>> parse_argv(['a  =  1', 'b  =  foobar', "c =   'baz'"])
    {'a': 1, 'b': 'foobar', 'c': 'baz'}

    :param argv:
    :return:
    """
    parsed = {}
    for p in argv:
        k, v = p.split('=')
        k = k.strip()
        try:
            parsed[k] = json.loads(v)
        except json.JSONDecodeError:
            parsed[k] = v.strip().strip("'")
    return parsed


def parse_version(version_string: Optional[str], prefix: str = '') -> Dict:
    """
    >>> parse_version("1.2", 'v')
    {'is_valid': False}
    >>> parse_version('v0.2.3', 'v')
    {'is_valid': True, 'is_stable': False, 'is_prerelease': False, \
'full': '0.2.3', 'full_with_prefix': 'v0.2.3', 'major': 0, 'minor': 2, \
'patch': 3, 'rest': 0, 'major_with_prefix': 'v0'}
    >>> parse_version('v1.2.3', 'v')
    {'is_valid': True, 'is_stable': True, 'is_prerelease': False, \
'full': '1.2.3', 'full_with_prefix': 'v1.2.3', 'major': 1, 'minor': 2, \
'patch': 3, 'rest': 0, 'major_with_prefix': 'v1'}

    >>> parse_version('v1.2.3a4', 'v')
    {'is_valid': True, 'is_stable': False, 'is_prerelease': True, \
'full': '1.2.3a4', 'full_with_prefix': 'v1.2.3a4', 'major': 1, 'minor': 2, 'patch': 3, \
'rest': 0, 'major_with_prefix': 'v1', \
'prerelease': 'alpha4', 'prerelease_type': 'alpha', 'prerelease_number': 4}

    >>> parse_version('v1.2.3a4+foo123.bar456', 'v')
    {'is_valid': True, 'is_stable': False, 'is_prerelease': True, \
'full': '1.2.3a4+foo123.bar456', 'full_with_prefix': 'v1.2.3a4+foo123.bar456', \
'major': 1, 'minor': 2, 'patch': 3, \
'rest': 0, 'major_with_prefix': 'v1', \
'prerelease': 'alpha4', 'prerelease_type': 'alpha', 'prerelease_number': 4, \
'build': 'foo123.bar456'}

    :param version_string:
    :param prefix:
    :return:
    """
    result = dict(
        is_valid=False,
    )
    if not version_string or not version_string.startswith(prefix):
        return result
    version_string = version_string[len(prefix):]
    try:
        parsed = semver.Version.parse(version_string)
    except ParseVersionError:
        return result
    result['is_valid'] = True
    result['is_stable'] = not parsed.prerelease and parsed.major > 0
    result['is_prerelease'] = bool(parsed.prerelease)
    result['full'] = parsed.text
    result['full_with_prefix'] = f'{prefix}{version_string}'
    for p in ['major', 'minor', 'patch', 'rest']:
        result[p] = getattr(parsed, p)
    result['major_with_prefix'] = f'{prefix}{parsed.major}'
    if parsed.prerelease:
        prerelease = ''.join(map(str, parsed.prerelease))
        result['prerelease'] = ''.join(prerelease)
        result['prerelease_type'], result['prerelease_number'] = parsed.prerelease
    if parsed.build:
        result['build'] = '.'.join(parsed.build)
    return result


REF_REGEXP = re.compile('^refs/tags/(.*)$')


def get_version_tag_from_github_env() -> Optional[str]:
    """
    >>> get_version_tag_from_github_env()
    >>> os.environ['GITHUB_REF'] = 'refs/tags/v1.2.3'
    >>> get_version_tag_from_github_env()
    'v1.2.3'
    >>> os.environ['GITHUB_REF'] = 'refs/branch/master'
    >>> get_version_tag_from_github_env()

    :return:
    """
    ref = os.environ.get("GITHUB_REF") or ''
    m = REF_REGEXP.match(ref)
    if m:
        return m.groups()[0]
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
        if '\n' in v:
            print(f"{k}<<EOF", file=_file)
            print(v, file=_file)
            print(f"EOF", file=_file)
        else:
            print("{0}={1}".format(k, v), file=_file)


def main():
    args = parse_argv(sys.argv[1:])
    version = get_version_tag_from_github_env()

    output = parse_version(version, prefix=args.get('prefix') or '')

    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            write_output(output, f)
    else:
        write_output(output, sys.stdout)


if __name__ == "__main__":
    # Rename these variables to something meaningful
    main()
