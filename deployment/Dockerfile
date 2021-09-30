FROM python:3.7-alpine

ENV APPDIR=/home/src
ENV PYTHONPATH=$PYTHONPATH:$APPDIR

WORKDIR $APPDIR

COPY ./t_auth $APPDIR/t_auth
COPY ./manage.py $APPDIR/
COPY ./requirements.txt $APPDIR/
COPY ./pytest.ini $APPDIR/
COPY ./docs/_static/swagger.yml $APPDIR/static/
COPY ./VERSION $APPDIR/

RUN apk update \
&&  apk add --no-cache gcc musl-dev && apk add --no-cache rust cargo && apk add --no-cache g++ make \
&&  apk add --no-cache --virtual .build-deps postgresql-dev gcc python3-dev musl-dev libffi-dev git file make \
&&  pip install --upgrade --force-reinstall --no-cache-dir -r $APPDIR/requirements.txt \
&&  pip install --upgrade pip setuptools \
&&  apk del --no-cache .build-deps \
&&  apk --no-cache add libpq

RUN echo $TAG > ${APPDIR}/VERSION

EXPOSE 8000

CMD /usr/local/bin/gunicorn -w 8 -b 0.0.0.0:8000 --worker-class gevent --timeout 60 --reload --access-logfile - t_auth.wsgi:application
