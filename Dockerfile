FROM python:3.10

LABEL org.opencontainers.image.authors="Temuri Takalandze <me@abgeo.dev>"

WORKDIR /var/app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

CMD ["python", "main.py"]
