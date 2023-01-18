[![ci](https://github.com/Apkawa/gh-action-semver-check/actions/workflows/ci.yml/badge.svg)](https://github.com/Apkawa/gh-action-semver-check/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)</br>

# gh-action-semver-check

Check semver by [PEP-0440](https://peps.python.org/pep-0440/#pre-release-separators)

# Usage

```yaml
on:
  push:
    tags:
      - 'v*'

jobs:
  test-tag:
    runs-on: ubuntu-latest

    steps:
      - uses: apkawa/gh-action-semver-check@master
        id: version

      - name: print output step
        run: |
          echo "Print version"
          echo "${{toJSON(steps.version.outputs)}}"

      - name: fail if not valid
        run: exit 1
        if: steps.version.outputs.is_valid != 'true'
  test-custom:
    runs-on: ubuntu-latest

    steps:
      - uses: apkawa/gh-action-semver-check@master
        id: version
        with:
          raw: "v1.2.3a1"
          prefix: ""

      - name: print output step
        run: |
          echo "Print version"
          echo "${{toJSON(steps.version.outputs)}}"

      - name: fail if not valid
        run: exit 1
        if: steps.version.outputs.is_valid != 'true'
```

### Inputs

| input            | required | description                                                                            |
|------------------|----------|----------------------------------------------------------------------------------------|
| `raw`            | no       | Version raw string. If not set - used `GITHUB_REF` env                                 |
| `prefix`         | no       | Prefix before version. `refs/tags/` by default                                         |
| `version_prefix` | no       | Version prefix in tag. `refs/tags/` is unnecessary. If not set - try detect "v" prefix |


### Output

| output              | description                                                                   |
|---------------------|-------------------------------------------------------------------------------|
| `is_valid`          | `true` if found valid version format in tag.                                  |
| `is_stable`         | `true` if found stable version in tag. (not have pre-release or dev metadata) |
| `is_unstable`       | `true` if found unstable version in tag. (have pre-release or dev metadata)   |
| `is_prerelease`     | `true` if found pre-release version in tag.                                   |
| `is_devrelease`     | `true` if found dev-release version in tag.                                   |
| `is_postrelease`    | `true` if found post-release version in tag.                                  |
| `full`              | Set full version as a string.                                                 |
| `full_with_prefix`  | Set full version as a string (include version_prefix).                        |
| `epoch`             | Set epoch version as a string.                                                |
| `major`             | Set major version as a string.                                                |
| `major_with_prefix` | Set major version as a string (include `version_prefix`).                     |
| `minor`             | Set minor version as a string.                                                |
| `patch`             | Set patch version as a string.                                                |
| `prerelease`        | Set pre-release version as a string. Example: a1, b2, rc3                     |
| `prerelease_phase`  | Set pre-release type as a string. Example: a, b, rc                           |
| `prerelease_number` | Set pre-release version number as a string. Example: 1                        |
| `dev`               | Set dev version as a string. Example: 1                                       |
| `post`              | Set post version as a string. Example: 1                                      |
| `local`             | Set local version.                                                            |

### Example

* `v0.1.2`
  ```
  {
    is_valid: true,
    is_stable: true,
    is_unstable: false,
    is_prerelease: false,
    is_devrelease: false,
    is_postrelease: false,
    full: 0.1.2,
    full_with_prefix: v0.1.2,
    epoch: 0,
    major: 0,
    minor: 1,
    patch: 2,
    major_with_prefix: v0,
  }
  ```
* `v1.2.3a1`
  ```
  {
    is_valid: true,
    is_stable: false,
    is_unstable: true,
    is_prerelease: true,
    is_devrelease: false,
    is_postrelease: false,
    full: 1.2.3a1,
    full_with_prefix: v1.2.3a1,
    epoch: 0,
    major: 1,
    minor: 2,
    patch: 3,
    major_with_prefix: v1,
    prerelease: a1,
    prerelease_phase: a,
    prerelease_number: 1
  }
  ```
* `6!2.3.4a1post2dev1+rev1234.123.123`
  ```
  {
    is_valid: true,
    is_stable: false,
    is_unstable: true,
    is_prerelease: true,
    is_devrelease: true,
    is_postrelease: true,
    full: 6!2.3.4a1post2dev1+rev1234.123.123,
    full_with_prefix: 6!2.3.4a1post2dev1+rev1234.123.123,
    epoch: 6,
    major: 2,
    minor: 3,
    patch: 4,
    major_with_prefix: v2,
    prerelease: a1,
    prerelease_phase: a,
    prerelease_number: 1,
    dev: 1,
    post: 2,
    local: rev1234.123.123
  }
  ```
