#!/bin/bash
echo "Ejecutando migraciones de base de datos con Alembic..."

alembic upgrade head

if [ $? -ne 0 ]; then
  echo "Error en las migraciones. Abortando inicio del bot."
  exit 1
fi

echo "Migraciones completadas. Iniciando el bot..."

exec python main.py
