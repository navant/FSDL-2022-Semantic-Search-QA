FROM python:3.9-buster as base

EXPOSE 8501
EXPOSE 54321

# Create the working directory
#   set -x prints commands and set -e causes us to stop on errors
RUN set -ex && mkdir /repo
WORKDIR /repo


ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1

FROM base as builder

ENV PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VERSION=1.2.0

# Install Python dependencies

RUN pip install "poetry==$POETRY_VERSION"
RUN python -m venv /venv

COPY pyproject.toml poetry.lock ./
RUN . /venv/bin/activate && poetry install --no-dev --no-root

# Copy only the relevant directories
#   note that we use a .dockerignore file to avoid copying logs etc.
COPY . .
RUN . /venv/bin/activate && poetry build

RUN ls -la ../venv/bin
ENV PATH="${PATH}:../venv/bin"
RUN ls -la

# Use docker run -it --rm -p$PORT_STREAMLIT:8501 -p$PORT_JINA:54321 to run the web server and listen on host $PORT_X
#   add --help top see help for the Python script
ENTRYPOINT ["./entrypoint.sh"]
