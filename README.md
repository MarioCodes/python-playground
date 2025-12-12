# python-playground
## Environment
### Raw
Navigate to your project's folder
~~~ bash
// this creates a virtual environment named venv
py -m venv env

// activate the environment
.\venv\Scripts\activate.bat

// from inside the virtual env
pip install -r requirements.txt

// to exit venv
.\venv\Scripts\deactivate.bat
~~~

### Poetry
install pip tools
~~~ bash
py -m pip install pip-tools

// upgrade pip
pip install --upgrade pip
~~~

install pipx
~~~ bash
py -m pip install --user pipx

// adds executables to global path so you can call them without py -m ...
py -m pipx ensurepath
~~~

install poetry through pipx
~~~ bash
py -m pipx install poetry
~~~

## Poetry usage
Go to your project's folder and set up poetry
~~~ bash
// this creates a `.toml` file with configuration
poetry init
~~~

add dependencies later on
~~~ bash
poetry add {package_name}
~~~

## Prompt engineering
Ensure you have `OPENAI_API_KEY` as environment variable and billing enabled for that key. You'll need an account.