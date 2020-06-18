#!/bin/bash

# frontend port
FEND_PORT=20013

# compressor port
COMPRESS_PORT=20016

# expiry age of secure links in minutes
SECURE_EXPIRY=20

# ~~ please don't ~~~
LOG_PATH='/var/log/law'
NGINX_PORT=20010
PID_LIST_PATH='/tmp/law.pid'
ROOT_DIR='/law'
# ~~~ ~~~ ~~~ ~~~ ~~~

# kill previous processes
if [ -f "${PID_LIST_PATH}" ]; then
  while IFS="" read -r p || [ -n "$p" ]
    do
      kill "${p}"
    done < "${PID_LIST_PATH}"
  rm "${PID_LIST_PATH}"
fi

# load env variables
export LAW_COMPRESS_PORT="${COMPRESS_PORT}"
export LAW_LINK_AGE="${SECURE_EXPIRY}"
export LAW_NGINX_PORT="${NGINX_PORT}"
export LAW_ROOT_DIR="${ROOT_DIR}"

# make path to logging texts
mkdir -p "${LOG_PATH}"

# run frontend (server 1)
export FLASK_APP="./fend/app.py"
nohup flask run -h 0.0.0.0 -p ${FEND_PORT} > "${LOG_PATH}/fend.log" 2>&1 &
echo "${!}" >> "${PID_LIST_PATH}"

# run compressor (server 3)
export FLASK_APP="./compressor/app.py"
nohup flask run -p ${COMPRESS_PORT} > "${LOG_PATH}/compressor.log" 2>&1 &
echo "${!}" >> "${PID_LIST_PATH}"

# run consumer (server 2)
nohup python3 -c "from loader.consumer import start_consume; start_consume()" > "${LOG_PATH}/downloader.log" 2>&1 &
echo "${!}" >> "${PID_LIST_PATH}"

# run clock (server 5)
nohup python3 -c "from timer.timekeeper import play_time; play_time()" > "${LOG_PATH}/timer.log" 2>&1  &
echo "${!}" >> "${PID_LIST_PATH}"

# run nginx (server 4)
nginx -s quit
nginx -c /etc/nginx/nginx.conf
cp nginx.conf /etc/nginx/nginx.conf
nginx -s reload
