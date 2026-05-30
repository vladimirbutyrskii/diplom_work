Доска объявлений (Diplom)
Backend-часть сайта объявлений на Django Rest Framework.

Постановка задачи
Разработать backend-часть для сайта объявлений со следующим функционалом:

Регистрация и аутентификация пользователей (JWT)

Распределение ролей: пользователь (user) и администратор (admin)

Сброс пароля через электронную почту

CRUD для объявлений (пользователи управляют своими, админ — всеми)

Отзывы под объявлениями (пользователи управляют своими, админ — всеми)

Поиск объявлений по названию

Пагинация (не более 4 объявлений на странице)

Автогенерируемая OpenAPI-документация (Swagger)

Контейнеризация (Docker, Docker Compose)

Тестирование (pytest, покрытие > 75%)

Технологический стек
Технология	Назначение
Python 3.12	Язык программирования
Django 5.1	Веб-фреймворк
Django Rest Framework 3.15	REST API
PostgreSQL 16	База данных
Simple JWT	JWT-аутентификация
django-filter	Фильтрация и поиск
drf-yasg	Swagger-документация
django-cors-headers	CORS-заголовки
pytest	Тестирование
Docker / Docker Compose	Контейнеризация
Gunicorn	WSGI-сервер для production
Права доступа
Действие	Аноним	Пользователь	Администратор
Просмотр списка объявлений	✅	✅	✅
Просмотр одного объявления	✅	✅	✅
Поиск объявлений	✅	✅	✅
Создание объявления	❌	✅	✅
Редактирование своего объявления	❌	✅	✅
Удаление своего объявления	❌	✅	✅
Редактирование чужого объявления	❌	❌	✅
Удаление чужого объявления	❌	❌	✅
Просмотр отзывов	❌	✅	✅
Создание отзыва	❌	✅	✅
Редактирование своего отзыва	❌	✅	✅
Удаление своего отзыва	❌	✅	✅
Редактирование чужого отзыва	❌	❌	✅
Удаление чужого отзыва	❌	❌	✅
Структура проекта
text
diplom/
├── .gitignore                  # Исключения для Git
├── .dockerignore               # Исключения для Docker
├── .env.example                # Пример переменных окружения
├── README.md                   # Документация
├── requirements.txt            # Python-зависимости
├── Dockerfile                  # Сборка Docker-образа
├── docker-compose.yml          # Оркестрация контейнеров
├── pytest.ini                  # Конфигурация pytest
├── conftest.py                 # Фикстуры для тестов
├── manage.py                   # Утилита управления Django
│
├── config/                     # Django-проект
│   ├── __init__.py
│   ├── settings.py             # Настройки проекта
│   ├── urls.py                 # Корневой роутинг
│   ├── wsgi.py                 # WSGI-конфигурация
│   └── asgi.py                 # ASGI-конфигурация
│
├── users/                      # Приложение «Пользователи»
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py               # Модель User
│   ├── serializers.py          # Сериализаторы
│   ├── views.py                # ViewSet'ы
│   ├── urls.py                 # Роутинг
│   ├── permissions.py          # Права доступа
│   ├── admin.py                # Админ-панель
│   └── tests/
│       ├── __init__.py
│       └── test_users.py       # Тесты пользователей
│
└── ads/                        # Приложение «Объявления и отзывы»
    ├── __init__.py
    ├── apps.py
    ├── models.py               # Модели Ad и Comment
    ├── serializers.py          # Сериализаторы
    ├── views.py                # ViewSet'ы
    ├── filters.py              # Фильтры django-filter
    ├── urls.py                 # Роутинг
    ├── permissions.py          # Права доступа
    ├── admin.py                # Админ-панель
    └── tests/
        ├── __init__.py
        └── test_ads.py         # Тесты объявлений и отзывов
API: эндпоинты
Аутентификация и пользователи
Метод	URL	Описание	Авторизация
POST	/api/register/	Регистрация нового пользователя	❌
POST	/api/token/	Получение JWT-токена (email + password)	❌
POST	/api/token/refresh/	Обновление access-токена	❌
GET	/api/users/me/	Профиль текущего пользователя	✅ Bearer
PATCH	/api/users/me/	Частичное обновление своего профиля	✅ Bearer
GET	/api/users/{id}/	Просмотр профиля по ID	✅ Bearer
PATCH	/api/users/{id}/	Обновление профиля по ID	✅ Bearer (админ)
DELETE	/api/users/{id}/	Удаление профиля	✅ Bearer (админ)
POST	/api/users/reset_password/	Запрос на сброс пароля	❌
POST	/api/users/reset_password_confirm/	Подтверждение сброса пароля	❌
Объявления
Метод	URL	Описание	Авторизация
GET	/api/ads/	Список объявлений (пагинация: 4 на стр.)	❌
GET	/api/ads/?search=текст	Поиск по названию	❌
GET	/api/ads/?title=текст	Фильтрация по названию	❌
GET	/api/ads/?page=2	Пагинация	❌
POST	/api/ads/	Создать объявление	✅ Bearer
GET	/api/ads/{id}/	Детальный просмотр (с отзывами)	❌
PATCH	/api/ads/{id}/	Редактировать объявление	✅ Bearer (автор/админ)
DELETE	/api/ads/{id}/	Удалить объявление	✅ Bearer (автор/админ)
Отзывы
Метод	URL	Описание	Авторизация
GET	/api/ads/{ad_pk}/comments/	Список отзывов	✅ Bearer
POST	/api/ads/{ad_pk}/comments/	Создать отзыв	✅ Bearer
GET	/api/ads/{ad_pk}/comments/{id}/	Просмотр отзыва	✅ Bearer
PATCH	/api/ads/{ad_pk}/comments/{id}/	Редактировать отзыв	✅ Bearer (автор/админ)
DELETE	/api/ads/{ad_pk}/comments/{id}/	Удалить отзыв	✅ Bearer (автор/админ)
Документация
Метод	URL	Описание
GET	/api/docs/	Swagger UI
GET	/admin/	Админ-панель Django
Быстрый старт (локальная разработка)
Требования
Python 3.12+

PostgreSQL 16

Git

1. Клонирование репозитория
bash
git clone <url-репозитория>
cd diplom
2. Виртуальное окружение
bash
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
3. Установка зависимостей
bash
pip install -r requirements.txt
4. Переменные окружения
Создайте файл .env на основе .env.example:

bash
cp .env.example .env
Отредактируйте .env, указав свои настройки подключения к PostgreSQL.

5. Миграции
bash
python manage.py makemigrations
python manage.py migrate
6. Создание суперпользователя
bash
python manage.py createsuperuser
7. Запуск сервера разработки
bash
python manage.py runserver
Приложение доступно: http://127.0.0.1:8000

Swagger-документация: http://127.0.0.1:8000/api/docs/

Запуск через Docker Compose
bash
# Запуск контейнеров
docker compose up --build -d

# Миграции
docker compose exec app python manage.py migrate

# Суперпользователь
docker compose exec app python manage.py createsuperuser

# Остановка
docker compose down
Тестирование
bash
# Запуск всех тестов
pytest

# Запуск с отчётом о покрытии
pytest --cov=. --cov-report=term-missing

# Минимальное покрытие: 75%
Переменные окружения
Переменная	Описание	По умолчанию
SECRET_KEY	Секретный ключ Django	—
DEBUG	Режим отладки	False
ALLOWED_HOSTS	Разрешённые хосты (через запятую)	localhost,127.0.0.1
DB_NAME	Имя базы данных	diplom
DB_USER	Пользователь БД	postgres
DB_PASSWORD	Пароль БД	—
DB_HOST	Хост БД	localhost
DB_PORT	Порт БД	5432
EMAIL_BACKEND	Бэкенд отправки почты	django.core.mail.backends.console.EmailBackend
EMAIL_HOST	SMTP-сервер	smtp.gmail.com
EMAIL_PORT	Порт SMTP	587
EMAIL_USE_TLS	Использовать TLS	True
EMAIL_HOST_USER	Логин почты	—
EMAIL_HOST_PASSWORD	Пароль приложения	—
CORS_ALLOWED_ORIGINS	Доверенные домены (через запятую)	http://localhost:3000
Деплой на Yandex Cloud
Подготовка сервера (однократно)
bash
# Подключение к серверу
ssh ubuntu@<публичный-IP>

# Установка Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker

# Клонирование проекта
git clone <url-репозитория> diplom
cd diplom
Создание .env на сервере
bash
nano .env
Заполнить реальными данными. Обязательно:

DEBUG=False

SECRET_KEY — длинная случайная строка

DB_PASSWORD — сложный пароль

ALLOWED_HOSTS — IP-адрес сервера

Первый запуск
bash
docker compose up --build -d
docker compose exec app python manage.py migrate
docker compose exec app python manage.py collectstatic --noinput
docker compose exec app python manage.py createsuperuser
Обновление (последующие деплои)
bash
cd diplom
git pull
docker compose down
docker compose up --build -d
docker compose exec app python manage.py migrate --noinput
docker compose exec app python manage.py collectstatic --noinput
CI/CD через GitHub Actions
При пуше в ветку develop автоматически запускается деплой на сервер. Workflow: .github/workflows/deploy.yml

Необходимые Secrets:

SSH_USER — логин на сервере

SSH_PRIVATE_KEY — приватный SSH-ключ