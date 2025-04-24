FROM python:3.10-slim

# Install system dependencies including netcat
RUN apt-get update && apt-get install -y \
    curl netcat-openbsd build-essential libglib2.0-0 libnss3 libgconf-2-4 \
    libx11-xcb1 libxcomposite1 libxcursor1 libxi6 libxtst6 \
    libxrandr2 libasound2 libpangocairo-1.0-0 libatk1.0-0 \
    libatk-bridge2.0-0 libcups2 && \
    rm -rf /var/lib/apt/lists/*

# Install Poetry
ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"
ENV POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-ansi

COPY . .

RUN chmod +x wait-for-it.sh

# Default entrypoint will be overridden per service
ENTRYPOINT ["bash", "wait-for-it.sh", "selenium-hub", "4444", "--"]
