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

### Linting

Main considerations:
- 120 chars per line (setup your editor for that)
- FSDL chose google style over pep8 (we can change it if we want to)

Adopted linting strategy from FSDL Course adding isort and autoflake for dealing with imports.

If you want to run linting before commit, stage files and then run:
```sh
./project_tasks/lint.sh
```

NOTE: If at some point some of the linting errors slows down our goal (e.g. typing with mypy or docstring) we 
can decide to relax the rules.

### Local Inference App Launch

We use streamlit so...

```sh
streamlit run src/semantic_search_qa/ui/01_main.py
```

Then check it out here: [http://localhost:8501/](http://localhost:8501/)