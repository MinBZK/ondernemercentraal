ARG BASE_IMAGE
FROM $BASE_IMAGE AS builder
ARG APP_VERSION

# Set it as an environment variable
ENV APP_VERSION=$APP_VERSION

# Install locales, required for generating dates in Dutch format
RUN echo "nl_NL.UTF-8 UTF-8" > /etc/locale.gen && \
    apt-get update && apt-get install -y locales && \
    locale-gen

# Copy the project files
COPY ./pyproject.toml ./uv.lock /backend/

WORKDIR /backend
RUN uv sync --frozen --no-install-project

COPY ./app /backend/app
COPY ./tests /backend/tests
COPY ./alembic /backend/alembic
COPY ./alembic.ini /backend/alembic.ini