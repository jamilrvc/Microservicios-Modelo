#!/bin/bash

# Esperar hasta que RabbitMQ esté listo
until nc -z rabbit 5672; do
  echo "Esperando a que RabbitMQ esté disponible..."
  sleep 2
done

echo "RabbitMQ está disponible, iniciando la aplicación..."

# Iniciar la aplicación (puedes ajustar el comando según tu configuración)
exec gunicorn -b 0.0.0.0:80 app:app

