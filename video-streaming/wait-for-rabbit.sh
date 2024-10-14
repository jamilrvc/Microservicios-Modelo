#!/bin/sh

set -e

HOST="$1"
shift
CMD="$@"

until nc -z "$HOST" 5672; do
  >&2 echo "RabbitMQ is unavailable - sleeping"
  sleep 1
done

>&2 echo "RabbitMQ is up - executing command"
exec $CMD


