FROM python:3.7

RUN apt-get update && apt-get install -y \
    cmake \
    git \
    gcc \
    g++ \
    libgoogle-perftools-dev

COPY ./* /opt/fast_align/

RUN cd /opt/fast_align \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make

ENV PATH="/opt/fast_align/build:${PATH}"
