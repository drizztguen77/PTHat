# PTHat

Pulse Train HAT Python API. This is a Python API to control the PTHAT from CNC Design Limited

## Installation

Make sure pip, wheel, setuptools and virtualenv are all installed.
```
python -m pip install --upgrade pip wheel setuptools virtualenv
```

To install the dependencies
```
pip install -r requirements.txt
```

## Build

To build the project files:
```
python setup.py sdist bdist_wheel
```

## TestPyPI

To upload the project the first time until a token is obtained. This will prompt for username and password.
```
twine upload --repository-url https://test.pypi.org/legacy/ dist/*
```

To upload the project to TestPyPI:
```
twine upload -r testpypi dist/*
```

To install this package from TestPyPI:
```
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple pthat
```

To view the project on TestPyPI:
https://test.pypi.org/project/pthat/

#### Token
Token to upload this project to TestPyPI:
```
Username: __token__
Password: <token password>
```
#### Keyring
To install the tokens to a local keyring do the following. Each command will prompt for the password. Just copy and paste the token.
```
keyring set https://upload.pypi.org/legacy/ __token__
keyring set https://test.pypi.org/legacy/ __token__
```


## Pypi

To upload the project the first time until a token is obtained. This will prompt for username and password.
```
twine upload dist/*
```

To upload the project to pypi:
```
twine upload -r pypi dist/*
```

To install this package from pypi:
```
pip install pthat
```

## Version

When the version is changed, there are currently four places the version number
must be changed
- pthat.py - _version variable
- setup.py - version parameter
- CHANGELOG.md
- docs/conf.py - version and release variables


## TODO

- Example for changing direction after n number of revolutions
- Example of reading pulse count and printing number of revolutions
- Async sending and reading the serial device
- Complete response parsing method
