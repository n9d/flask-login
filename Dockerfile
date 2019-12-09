FROM python:3.7.4
USER root

RUN apt-get update
RUN apt-get -y install locales && \
    localedef -f UTF-8 -i ja_JP ja_JP.UTF-8

ENV LANG ja_JP.UTF-8
ENV LANGUAGE ja_JP:ja
ENV LC_ALL ja_JP.UTF-8
ENV TZ JST-9
ENV TERM xterm

EXPOSE 5000

ADD . /root
RUN pip install \
	flask \
	gunicorn

#RUN pip install Flask-BasicAuth

WORKDIR /root/app

EXPOSE 5000/tcp
ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0:5000 --workers=3 --access_logfile=- --log-file=- --log-level=info"

ENTRYPOINT ["gunicorn","app:app"]
