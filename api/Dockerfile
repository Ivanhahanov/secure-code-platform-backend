FROM python:3.8-alpine
MAINTAINER Ivan Hahanov 'hahanov.i@explabs.ru'
RUN pip install fastapi uvicorn pytest redis
RUN pip install docker
RUN apk add --update docker openrc
RUN rc-update add docker boot
EXPOSE 80
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /api
CMD ["uvicorn", "api.app.server:app", "--host", "0.0.0.0", "--port", "80", "--reload"]