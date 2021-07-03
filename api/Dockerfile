FROM node:14.2-alpine3.11 AS frontend-builder
COPY ./secure-code-platform-frontend /frontend
WORKDIR /frontend
RUN npm ci && npm run generate

FROM python:3.8-alpine
MAINTAINER Ivan Hahanov 'hahanov.i@explabs.ru'
RUN pip install fastapi uvicorn pytest redis
RUN pip install docker
RUN apk add --update docker openrc
RUN rc-update add docker boot
RUN apk add --no-cache \
    build-base cairo-dev cairo cairo-tools linux-headers \
    # pillow dependencies
    jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev libffi-dev
EXPOSE 80
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install Pillow
RUN pip install "CairoSVG==2.1.3"
COPY . /api
COPY --from=frontend-builder /frontend/dist /frontend/dist
CMD ["uvicorn", "api.app.server:app", "--host", "0.0.0.0", "--port", "80", "--reload"]