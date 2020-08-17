FROM python:3.7

RUN apt-get update && apt-get install -y \
    cmake \
    git \
    gcc \
    g++ \
    libgoogle-perftools-dev

COPY ./src /opt/fast_align/src
COPY ./cmake /opt/fast_align/cmake
COPY ./CMakeLists.txt /opt/fast_align/CMakeLists.txt

RUN cd /opt/fast_align \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make

ENV PATH="/opt/fast_align/build:${PATH}"
