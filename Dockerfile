FROM python:3.12.7-slim as builder

RUN mkdir /multimedia_station
COPY /src/. /multimedia_station
WORKDIR /multimedia_station

RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && pip install --upgrade pip \
    && pip install --user -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*


ENV PATH=/root/.local:$PATH

CMD ["python", "./__main__.py"]