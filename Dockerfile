FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    mininet \
    openvswitch-switch \
    iproute2 \
    iputils-ping \
    python3 \
    python3-matplotlib \
    python3-pip \
    sudo \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
