
## Run tests
```bash
pip install -r requirements.txt
pytest # run tests
tox # run test matrix
```

## Run tests with pyenv with specific python and pypy

```shell
pyenv install 3.10-dev pypy3.7-7.3.5
pyenv local 3.10-dev pypy3.7-7.3.5
pip install -r requirements.txt
tox -e py310,pypy3
```

## Type checks

```shell
tox -e type
```

## Lint code

```shell
tox -e qa
```


## Before commit

Install git hook

```shell
pip install -r requirements-dev.txt

pre-commit install --hook-type pre-commit --hook-type commit-msg --hook-type pre-push
```

For pycharm needs install `tox` to global

## Bump version
Use [commitzen](https://commitizen-tools.github.io/commitizen/bump/)

### Release
```shell
cz bump --check-consistency --no-verify
```

### Prelease

```shell
cz bump --check-consistency --no-verify --prerelease alpha
```

## Update changelog

```shell
cz changelog
```
