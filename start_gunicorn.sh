#!/bin/bash
set -e
LOGFILE=/trood/trood-core-python/logs/auth.log
LOGDIR=$(dirname $LOGFILE)
NUM_WORKERS=2

# PID file
PIDFILE="$HOME/tmp/trood_auth.pid"

# check if gunicorn for this site is already running
if [ -e "${PIDFILE}" ] && (ps -u $USER -f | grep "[ ]$(cat ${PIDFILE})[ ]"); then
  echo "Already running."
  exit 99
fi

# user/group to run as
USER=www-data
GROUP=www-data

# activate virtualenv and test log directory
source /.envs/t_auth/bin/activate
test -d $LOGDIR || mkdir -p $LOGDIR
cd /trood/trood-core-python/t_auth/

export PATH=$PATH:/trood/trood-core-python/t_auth/
export PYTHONPATH=$PYTHONPATH:/trood/trood-core-python/t_auth/
#exec python

# run gunicorn
exec /.envs/t_auth/bin/gunicorn -b 0.0.0.0:8001 -w $NUM_WORKERS --user=$USER --group=$GROUP --max-requests=200 --log-level=debug --log-file=$LOGFILE 2>>$LOGFILE t_auth.wsgi:application
