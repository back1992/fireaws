FROM python:3.5
MAINTAINER George Cushen

ADD ./.deploy/sources.list /etc/apt/sources.list

# Install Mezzanine dependencies.
RUN sed "s/^deb\ /deb-src /g" /etc/apt/sources.list >> /etc/apt/sources.list && \
    DEBIAN_FRONTEND=noninteractive apt-get clean && apt-get update && \
    apt-get install -y \
        libjpeg-dev openssh-server &&\
    apt-get build-dep -y \
        python-imaging

ENV DOCKERIZE_VERSION v0.2.0
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

RUN mkdir ~/.pip
ADD .deploy/pip.conf /root/.pip/
ADD .deploy/.pydistutils.cfg /root/

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
RUN pip freeze --local | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U
RUN pip install django-celery
RUN pip install gunicorn
ADD . /code/

# Add start script
ADD ./start.sh /
