[TOC]



# Introduction

This document is a brief of the [offical flaskr tutorial](http://flask.pocoo.org/docs/1.0/tutorial).

# Setup

## Create Project Directory

    mkdir flask-tutorial
    cd flask-tutorial

## Setup A Virtual Environment

Use a virtual environment to manage the dependencies for your project, both in development and in production.

Virtual environments are independent groups of Python libraries, one for each project. Packages installed for one project will not affect other projects or the operating system’s packages.

Python 3 comes bundled with the [venv](https://docs.python.org/3/library/venv.html#module-venv) module to create virtual environments. We'll use it to create a virtual environment for our project.

Create virtual environment for your project in `venv` directory: 

    python -m venv venv

Activate the virtual environment:

    . venv/bin/activate

Activate for Windows:

    venv\Scripts\activate

Upgrade python package tools(optional):

    python -m pip install --upgrade pip setuptools wheel

Install Flask and its dependencies:

    pip install flask

Recommandation dependencies(optional):

- [Blinker](https://pythonhosted.org/blinker/) provides support for [Signals](http://flask.pocoo.org/docs/1.0/signals/#signals).
- [SimpleJSON](https://simplejson.readthedocs.io/) is a fast JSON implementation that is compatible with Python’s `json` module. It is preferred for JSON operations if it is installed.
- [python-dotenv](https://github.com/theskumar/python-dotenv#readme) enables support for [Environment Variables From dotenv](http://flask.pocoo.org/docs/1.0/cli/#dotenv) when running `flask` commands.
- [Watchdog](https://pythonhosted.org/watchdog/) provides a faster, more efficient reloader for the development server.

## Project Layout

The offical flaskr tutorial project directory structure:

    /home/user/Projects/flask-tutorial
    ├── flaskr/
    │   ├── __init__.py
    │   ├── db.py
    │   ├── schema.sql
    │   ├── auth.py
    │   ├── blog.py
    │   ├── templates/
    │   │   ├── base.html
    │   │   ├── auth/
    │   │   │   ├── login.html
    │   │   │   └── register.html
    │   │   └── blog/
    │   │       ├── create.html
    │   │       ├── index.html
    │   │       └── update.html
    │   └── static/
    │       └── style.css
    ├── tests/
    │   ├── conftest.py
    │   ├── data.sql
    │   ├── test_factory.py
    │   ├── test_db.py
    │   ├── test_auth.py
    │   └── test_blog.py
    ├── venv/
    ├── setup.py
    └── MANIFEST.in

- `flaskr/`, a Python package containing your application code and files.
- `tests/`, a directory containing test modules.
- `venv/`, a Python virtual environment where Flask and other dependencies are installed.
- Installation files telling Python how to install your project.
- Version control config, such as [git](https://git-scm.com/). You should make a habit of using some type of version control for all your projects, no matter the size.
- Any other project files you might add in the future.

## Version Control Ignore

For example, with git:

.gitignore

```
venv/

*.pyc
__pycache__/

instance/

.pytest_cache/
.coverage
htmlcov/

dist/
build/
*.egg-info/
```

# Develop

## Concepts

### View

A view function is the code you write to respond to requests to your application. Flask uses patterns to match the incoming request URL to the view that should handle it. The view returns data that Flask turns into an outgoing response. 

### Blueprint

A [`Blueprint`](http://flask.pocoo.org/docs/1.0/api/#flask.Blueprint) is a way to organize a group of related views and other code. Rather than registering views and other code directly with an application, they are registered with a blueprint. Then the blueprint is registered with the application when it is available in the factory function, e.g., `app.register_blueprint(your_blueprint)`.

### Endpoint

URL is the HTTP access interface.

A view is to handle the corresponding HTTP request for a URL.

Endpoint is a string reference to the view in application.

The [`url_for()`](http://flask.pocoo.org/docs/1.0/api/#flask.url_for) function generates the URL to a view based on a name and arguments. The name associated with a view is also called the *endpoint*, and by default it’s the same as the name of the view function.

For example, the `hello()` view that was added to the app factory earlier in the tutorial has the name `'hello'` and can be linked to with `url_for('hello')`. If it took an argument, which you’ll see later, it would be linked to using `url_for('hello',who='World')`.

When using a blueprint, the name of the blueprint is prepended to the name of the function, so the endpoint for the `login`function you wrote above is `'auth.login'` because you added it to the `'auth'` blueprint.

### Template

Flask uses the [Jinja](http://jinja.pocoo.org/docs/templates/) template library to render templates.

### Static

Flask automatically adds a `static` view that takes a path relative to the `flaskr/static` directory and serves it. For example:

```
{{ url_for('static', filename='style.css') }}
```

## Application Factory and Instance

The most straightforward way to create a Flask application is to create a global [`Flask`](http://flask.pocoo.org/docs/1.0/api/#flask.Flask) instance directly at the top of your code. While this is simple and useful in some cases, it can cause some tricky issues as the project grows.

Instead of creating a [`Flask`](http://flask.pocoo.org/docs/1.0/api/#flask.Flask) instance globally, you will create it inside a function. This function is known as the *application factory*. Any configuration, registration, and other setup the application needs will happen inside the function, then the application will be returned.

Create the `flaskr` directory and add the `__init__.py` file. And create application factory in it. 

[Application Factory example](http://flask.pocoo.org/docs/1.0/tutorial/factory/#the-application-factory):

```
import os

from flask import Flask


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app
```

## Application Configuration

Configure application in the factory function for different mode

* test mode

  The `test_config` dict argument for the factory function.

* development mode

      app.config.from_mapping(
      	SECRET_KEY='dev',
          DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
      )

* production mode

  Load the config file from instance folder: `app.config.from_pyfile('config.py', silent=True)`.

Note: Production and test configurations wil override the development.

## Running In Development

Run your application in the development mode. Development mode shows an interactive debugger whenever a page raises an exception, and restarts the server whenever you make changes to the code.

For Linux and Mac:

```
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run

```

For Windows cmd, use `set` instead of `export`:

```
set FLASK_APP=flaskr
set FLASK_ENV=development
flask run

```

For Windows PowerShell, use `$env:` instead of `export`:

```
$env:FLASK_APP = "flaskr"
$env:FLASK_ENV = "development"
flask run
```

## Make the Project Installable

Making your project installable means that you can build a *distribution* file and install that in another environment, just like you installed Flask in your project’s environment.

### Describe Project

The `setup.py` file describes your project and the files that belong to it.

setup.py

```
from setuptools import find_packages, setup

setup(
    name='flaskr',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ],
)
```

To include other files, such as the static and templates directories,`include_package_data` is set. Python needs another file named `MANIFEST.in` to tell what this other data is.

MANIFEST.in

```
include flaskr/schema.sql
graft flaskr/static
graft flaskr/templates
global-exclude *.pyc
```

### Install Project

Use `pip` to install your project in the virtual environment.

```
pip install -e .

```

This tells pip to find `setup.py` in the current directory and install it in *editable* or *development* mode. Editable mode means that as you make changes to your local code, you’ll only need to re-install if you change the metadata about the project, such as its dependencies.

Benefits:

* Test tools can isolate your test environment from your development environment.
* You can manage your project’s dependencies just like other packages do. `pip install` will automatically install dependencies.
* You can import the project package from any python module.

## Command Line Interface

The `flask` command is implemented using [Click](http://click.pocoo.org/).

This example adds the command `create_user` that takes the argument `name`.

```
import click
from flask import Flask

app = Flask(__name__)

@app.cli.command()
@click.argument('name')
def create_user(name):
    pass
```

```
flask create_user admin
```

This example adds the same command, but as `user create`, a command in a group. This is useful if you want to organize multiple related commands.

```
import click
from flask import Flask
from flask.cli import AppGroup

app = Flask(__name__)
user_cli = AppGroup('user')

@user_cli.command('create')
@click.argument('name')
def create_user(name):
    pass

app.cli.add_command(user_cli)
```

```
flask user create demo
```

## Test

Flask provides a test client that simulates requests to the application and returns the response data.

You’ll use [pytest](https://pytest.readthedocs.io/) and [coverage](https://coverage.readthedocs.io/) to test and measure your code. Install them both:

```
pip install pytest coverage
```

### Unittest

Use [pytest](https://docs.pytest.org/en/latest/contents.html) framework to run test.

Run test cases: `pytest`

Or Run if you have configure have `setup.py` and `setup.cfg`: `python setup.py test`

Run test cases with verbose ouput: `pytest -v`

Run test cases in a directory: `pytest tests`

Run test cases in a module: `pytest tests/test_auth.py`

Run a test case: `pytest tests/test_auth.py::test_register`

### Test Coverage

You should test as much of your code as possible. Code in functions only runs when the function is called, and code in branches, such as if blocks, only runs when the condition is met. You want to make sure that each function is tested with data that covers each branch.

The closer you get to 100% coverage, the more comfortable you can be that making a change won’t unexpectedly change other behavior. However, 100% coverage doesn’t guarantee that your application doesn’t have bugs. In particular, it doesn’t test how the user interacts with the application in the browser. Despite this, test coverage is an important tool to use during development.

Some extra configuration, which is not required but makes running tests with `coverage` less verbose, can be added to the project’s`setup.cfg` file. Put the following into `setup.cfg` file:

```
[tool:pytest]
testpaths = tests

[coverage:run]
branch = True
source =
    flaskr
```

To measure the code coverage of your tests, use the `coverage` command to run pytest instead of running it directly.

```
coverage run -m pytest
```

View coverage report in command line: 

```
coverage report
```

Convert report file into HTML file(see directory `htmlcov`): 

```
coverage html
```

# Deploy

## Build

When you want to deploy your application elsewhere, you build a distribution file. The current standard for Python distribution is the wheel format, with the `.whl` extension. Make sure the wheel library is installed first:

```
pip install wheel
```

Running `setup.py` with Python gives you a command line tool to issue build-related commands. The `bdist_wheel` command will build a wheel distribution file.

```
python setup.py bdist_wheel
```

You can find the file in `dist/yourpackagename-1.0.0-py3-none-any.whl`. The file name is the name of the project, the version, and some tags about the file can install.

## Install

Copy this file to another machine, set up a new virtualenv with [venv](http://flask.pocoo.org/docs/1.0/installation/#install-create-env), then install the file with pip(not in editable mode).

```
pip install yourpackagename-1.0.0-py3-none-any.whl
```

Pip will install your project along with its dependencies.

## Init DB

Since this is a different machine, you need to run init-db again to create the database in the instance folder.

```
export FLASK_APP=yourpackagename
flask init-db
```

When Flask detects that it’s installed (not in editable mode), it uses a different directory for the instance folder. You can find it at `venv/var/yourpackagename-instance` instead.

## Production config

Create the `config.py` file in the instance folder, which the application factory will read from if it exists.

You muest set a Secret Key first.

Generate a random key: `python -c 'import os; print(os.urandom(16))'`

Copy the generated value into it the config file:

```
SECRET_KEY = b'_5#y2L"F4Q8z\n\xec]/'
```

## Runing in Production

When running publicly rather than in development, you should not use the built-in development server (`flask run`). The development server is provided by Werkzeug for convenience, but is not designed to be particularly efficient, stable, or secure.

Instead, use a production WSGI server. For example, to use [Waitress](https://docs.pylonsproject.org/projects/waitress/), first install it in the virtual environment:

```
pip install waitress
```

You need to tell Waitress about your application, but it doesn’t use `FLASK_APP` like flask run does. You need to tell it to import and call the application factory to get an application object.

```
waitress-serve --call 'flaskr:create_app'
```

Or you can choose another [deploy options](http://flask.pocoo.org/docs/1.0/deploying/).

# More

Check out the [Quickstart](http://flask.pocoo.org/docs/1.0/quickstart/#quickstart) for an overview of what Flask can do, then dive into the docs to keep learning. Flask uses [Jinja](https://palletsprojects.com/p/jinja/), [Click](https://palletsprojects.com/p/click/), [Werkzeug](https://palletsprojects.com/p/werkzeug/), and [ItsDangerous](https://palletsprojects.com/p/itsdangerous/) behind the scenes, and they all have their own documentation too. You’ll also be interested in [Extensions](http://flask.pocoo.org/docs/1.0/extensions/#extensions) which make tasks like working with the database or validating form data easier and more powerful.