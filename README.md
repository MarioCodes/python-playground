# python-playground
install pip tools
~~~ bash
py -m pip install pip-tools
~~~

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

## Prompt engineering
Ensure you have `OPENAI_API_KEY` as environment variable and billing enabled for that key.