FROM python:3.11.4-alpine
LABEL maintainer="adamchuk.oksana01.08@gmail.com"

ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
