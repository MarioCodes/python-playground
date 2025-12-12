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

// if problems on init
poetry config virtualenvs.use-poetry-python true
~~~

add dependencies
~~~ bash
poetry add {package_name}
~~~

create virtual env for the project
~~~ bash
// you need to have a README.md on the project's root
poetry install
~~~

enter into virtual env
~~~ bash
poetry env activate

// activate or create new virtualenv for current project
poetry env use {other_env}
~~~

see active env
~~~ bash
poetry env info
~~~

build project
~~~ bash
poetry build
~~~

install and run a project through poetry
~~~ bash
// this works through pyproject.toml's conf
poetry install
~~~

there you need something like this, where this 'hello' is the one you use to run the project
~~~ toml
[tool.poetry.scripts]
hello = "PromptEngineering:main"
~~~

execute
~~~ bash
poetry run hello
~~~

## Prompt engineering
Ensure you have `OPENAI_API_KEY` as environment variable and billing enabled for that key. You'll need an account.