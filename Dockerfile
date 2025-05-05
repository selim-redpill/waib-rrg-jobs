FROM python:3.13-alpine

ENV POETRY_VERSION=1.8.5

# Install only necessary Alpine packages (no libgl1!)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    && pip install --no-cache-dir poetry==$POETRY_VERSION

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-ansi --only main

COPY main.py models.py logger.py ./

CMD ["poetry", "run", "python", "main.py"]