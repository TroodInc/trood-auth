FROM python:3.8-alpine

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
&&  apk add --no-cache gcc musl-dev && apk add --no-cache rust cargo \
&&  apk add --no-cache --virtual .build-deps postgresql-dev gcc python3-dev musl-dev libffi-dev git \
&&  pip install --upgrade --force-reinstall --no-cache-dir -r $APPDIR/requirements.txt \
&&  apk del --no-cache .build-deps \
&&  apk --no-cache add libpq

RUN echo $TAG > ${APPDIR}/VERSION

EXPOSE 8000

CMD /usr/local/bin/gunicorn -w 4 -b 0.0.0.0:8000 --reload --access-logfile - t_auth.wsgi:application
