#!/bin/bash

set -e

# Переключение на ветку develop
git checkout develop
git pull origin develop

# Копирование .env.prod в .env
cp .env.prod .env

# Остановка старых контейнеров
docker compose -f docker-compose.prod.yml down

# Сборка и запуск
docker compose -f docker-compose.prod.yml up --build -d

# Ожидание запуска
sleep 5

# Миграции и статика (уже в command, но для верности)
docker compose -f docker-compose.prod.yml exec -T app python manage.py migrate --noinput
docker compose -f docker-compose.prod.yml exec -T app python manage.py collectstatic --noinput

