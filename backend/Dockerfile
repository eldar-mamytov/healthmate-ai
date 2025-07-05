FROM python:3.10-slim-bullseye

# Install build dependencies for packages like llama-cpp-python
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    curl && \
    rm -rf /var/lib/apt/lists/*

# Clear proxy environment variables to prevent issues with openai client
ENV HTTP_PROXY=""
ENV HTTPS_PROXY=""
ENV ALL_PROXY=""
ENV NO_PROXY=""

# Setting a working directory inside the container!
WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

# Add pip cache purge before installation and ensure --no-cache-dir
RUN pip cache purge && \
    pip uninstall -y httpx && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-level", "debug"]