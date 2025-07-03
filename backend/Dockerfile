FROM python:3.10-slim-bullseye

# Setting a working directory inside the container!
WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

# Add pip cache purge before installation and ensure --no-cache-dir
RUN pip cache purge && \
    pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]