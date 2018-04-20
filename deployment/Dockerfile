FROM python:3

ENV APPDIR=/home/src
ENV PYTHONPATH=$PYTHONPATH:$APPDIR

RUN apt-get update && \
    apt-get install gcc g++ make libffi-dev libssl-dev -y && mkdir -p $APPDIR

ADD ./ $APPDIR/
RUN pip install -r $APPDIR/requirements.txt

EXPOSE 8000
CMD /usr/local/bin/gunicorn -b 0.0.0.0:8000 t_auth.wsgi:application