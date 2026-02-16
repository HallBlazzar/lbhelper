FROM debian:13.2

ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && \
    apt-get install -qq  \
        python3.13 \
        git \
        dpkg-dev \
        live-build \
        curl \
        locales

# set locale for lb and package installation
RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh

ENTRYPOINT ["sleep", "infinity"]
