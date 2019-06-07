FROM ubuntu:bionic

RUN apt-get update
RUN apt-get install -y python3 \
    python3-pip \
    build-essential \
    libssl-dev \
    libffi-dev \
    dnsutils

# Resolves pg_config executable not found
RUN apt-get install -y libpq-dev

RUN apt-get clean

RUN pip3 install Flask
RUN pip3 install Flask-Table
RUN pip3 install Flask-Bootstrap
RUN pip3 install Flask-WTF
RUN pip3 install psycopg2-binary
RUN pip3 install psycopg2
RUN pip3 install pytest

CMD /bin/bash;
