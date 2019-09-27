FROM python:3.6

ENV APPDIR=/home/src
ENV PYTHONPATH=$PYTHONPATH:$APPDIR

RUN apt-get update && \
    apt-get install gcc g++ make libffi-dev libssl-dev -y && mkdir -p $APPDIR

WORKDIR $APPDIR

COPY ./t_auth $APPDIR/t_auth
COPY ./manage.py $APPDIR/
COPY ./requirements.txt $APPDIR/
COPY ./pytest.ini $APPDIR/
COPY ./docs/_static/swagger.yml $APPDIR/static/

RUN pip install -r $APPDIR/requirements.txt

EXPOSE 8000

CMD /usr/local/bin/gunicorn -w 8 -b 0.0.0.0:8000 --reload --access-logfile - t_auth.wsgi:application