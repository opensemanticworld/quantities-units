# quantities-units

Project to fetch quantities and units from ontologies to provide a applied data source to OSW.

Table of Contents

- [quantities-units](#cookiecutterproject_name)
  - [Prerequisites](#prerequisites)
  - [Usage](#usage)
    - [Windows](#windows)
      - [Using Poetry](#using-poetry)
      - [Using Pip](#using-pip)
    - [Ubuntu](#ubuntu)
      - [Makefile for Poetry](#makefile-for-poetry)

## Prerequisites

- Package Manager:
  - [poetry](https://python-poetry.org/docs/#installation) (Recommended)
    - Why? [See here!](https://mathdatasimplified.com/poetry-a-better-way-to-manage-python-dependencies/)
    - TLDR:
      - Automatically:
        - creates a project specific virtual environment and installs dependencies,
        - manages all project dependencies in a `pyproject.toml` file,
        - manages exact package versions in a `poetry.lock` file.
      - Can be used to immediately resolve dependency conflicts.
      - Provides consistent dependency management across all environments for deployments and CI/CD.
  - [pip](https://pip.pypa.io/en/stable/installing/)
    - All virtual environments with its dependencies must be installed and managed manually.
    - Requires a `requirements.txt` file to manage dependencies.
    - Project dependencies are not locked to specific versions.
    - Dependency conflict resolving is way more difficult and possibly produces overhead.
    - Does not provide a way to manage virtual environments.
    - Dependencies in `pyproject.toml`, which is essential for the `Docker-Wrapper-Repository`, must be manually created or by using third-party tools like [pip-tools](https://hynek.me/til/pip-tools-and-pyproject-toml/).

## Usage

Change into the project directory first using a terminal. Then, follow the instructions below.

### Windows

#### Using Poetry

Poetry must be installed first. See this article to configure [PyCharm with Poetry](https://towardsdatascience.com/configure-a-poetry-environment-that-runs-in-pycharm-eba47420f0b6).

To create a project specific virtual environment (Python version of your project musst be installed on your machine, consider to use [Pyenv Windows](https://github.com/pyenv-win/pyenv-win) to install reqired Python versions first), run:

```bash
poetry shell
```

To initialize the project as a Git repository, run:
  
```bash
git init
```

To install dependencies, run:
  
```bash
poetry install
```

Add a new dependency to the project:

```bash
poetry add <package-name>
```

Remove a dependency from the project:

```bash
poetry remove <package-name>
```

Test python code in tests directory:

```bash
pytest
```

#### Using Pip

All virtual environments with its dependencies must be installed and managed manually.

### Ubuntu

Commands listed for Windows can be used on Ubuntu as well. Makefile commands are also available. It is recommended to install virtual environements for different Python versions first, e.g., using [Pyenv](https://github.com/pyenv/pyenv).

#### Makefile for Poetry

Create project specific virtuall environment, initialize the project as Git repository and install dependencies and activate the virtual environment:

```bash
make setup
```

Activate the project specific virtual environment (if not already activated):

```bash
make activate
```

Test python code:

```bash
make test
```

Create documentation:

```bash
make docs_save
```

View documentation:

```bash
make docs_serve
```

Clean up compiled files and remove the virtual environment:
  
```bash
make clean
```
