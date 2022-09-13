# FSDL-2022-Semantic-Search-QA
Semantic Search and Question Answering project for Full Stack Deep Learning 2022

## Dev Instructions

### Install [Poetry](https://python-poetry.org/docs/)

e.g.:
```sh
curl -sSL https://install.python-poetry.org | python3 -
export PATH="${PATH}":"${HOME}"/.local/bin
```

Clone repo
```sh
git clone git@github.com:navant/FSDL-2022-Semantic-Search-QA.git
cd FSDL-2022-Semantic-Search-QA
```

### Install deps
```sh
poetry install
```

### VS Code Integration (Optional)
```sh
poetry shell  # This activates the virtual environment of the project making it available to VS Code
code .
```

Then, in VS Code, choose the interpreter and kernel from the virtual environment.