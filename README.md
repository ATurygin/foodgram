# Проекn Foodgram

### Описание проекта
Это дипломный проект курса Яндекс-практикума по бэкенд-разработке на Python.
Проект представляет из себя сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов. Зарегистрированным пользователям также доступен сервис «Список покупок». Он позволяет создавать список продуктов, которые нужно купить для приготовления выбранных блюд.

### Запуск проекта
Для локального запуска проекта подготовьте .env-файл с переменными окружения (пример файла есть в корневой директории проекта).
Выполните docker compose up в корневой директории. Проект будет доступен по адресу http://localhost:8000.
После старта нужно применить миграции и собрать файлы статики:
```
docker compose exec backend python3 manage.py migrate
docker compose exec backend python3 manage.py collectstatic
docker compose exec backend cp -r static/. /staticfiles/static/
```

В "прод" окружении проект доступен по адресу https://foodgram.aturygin-petprojects.ru/

### Технологии
Frontend-часть проекта - это SPA на JavaScript. Backend-часть - это python-приложение, реализующее REST API для взаимодействия с Frontend'ом.
В проекте использованы:
+ **Python 3**
+ **Django**
+ **Django REST Framework**
+ **Docker**
+ **nginx**

### Авторы
Александр Турыгин
whothehellcares@yandex.ru
