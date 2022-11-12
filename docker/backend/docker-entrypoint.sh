#!/bin/sh
set -e


if [ "$1" = "uvicorn" ]
then
    until mysqladmin ping -h db --silent; do
      echo 'waiting for mysqld to be connectable...'
      sleep 2
    done
    # alembic -c /app/backend/alembic.ini upgrade head
fi
exec "$@"