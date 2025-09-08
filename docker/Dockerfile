FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install -U pip && pip install .[dev]
COPY src ./src
COPY Makefile README.md .
ENTRYPOINT ["expab"]