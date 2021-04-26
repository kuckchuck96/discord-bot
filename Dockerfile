FROM python:3.9.4-alpine
LABEL maintainer="LASN Devs"

RUN apk update && apk upgrade
RUN apk add --no-cache git make build-base linux-headers
RUN apk add --no-cache libressl-dev musl-dev libffi-dev
RUN apk add --no-cache ffmpeg
# RUN apk add --no-cache ffmpeg=4.4-r0

WORKDIR /lasnbot
ADD . /lasnbot
RUN pip3 install --no-cache-dir -r requirements.txt
RUN apk del libressl-dev musl-dev libffi-dev

CMD [ "python3", "main.py" ]