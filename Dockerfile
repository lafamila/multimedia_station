FROM python:3.12.7-slim as builder

RUN mkdir /multimedia_station
COPY /src/. /multimedia_station
WORKDIR /multimedia_station
RUN apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
RUN set -x \
    && add-apt-repository ppa:mc3man/trusty-media \
    && apt-get update \
    && apt-get dist-upgrade \
    && apt-get install -y --no-install-recommends gcc libc-dev ffmpeg\
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
      && pip install --user -r requirements.txt

RUN apt-get purge -y --auto-remove gcc libc-dev

FROM python:3.12.7-slim

COPY --from=builder /multimedia_station /multimedia_station
COPY --from=builder /root/.local /root/.local

WORKDIR /multimedia_station

ENV PATH=/root/.local:$PATH

CMD ["python", "./__main__.py"]