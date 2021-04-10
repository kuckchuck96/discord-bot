FROM python:3.9-alpine
LABEL maintainer="LASN Devs"

RUN apk update && apk upgrade
RUN apk add --no-cache git make build-base linux-headers

WORKDIR /lasnbot
ADD . /lasnbot
RUN pip3 install --no-cache-dir -r requirements.txt

CMD [ "python3", "main.py" ]