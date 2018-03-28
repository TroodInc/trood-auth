FROM python:3-alpine

ENV APPDIR=/home/t_auth
ENV PYTHONPATH=$PYTHONPATH:$APPDIR

RUN apk update && \
    apk add gcc g++ make libffi-dev openssl-dev && \ 
    mkdir -p $APPDIR
WORKDIR $APPDIR

COPY ./requirements.txt $APPDIR/requirements.txt
RUN pip install -r $APPDIR/requirements.txt
RUN rm $APPDIR/requirements.txt

ADD ./ $APPDIR/

EXPOSE 8000

CMD ["/usr/local/bin/gunicorn", "-b", "0.0.0.0:8000", "t_auth.wsgi:application"]