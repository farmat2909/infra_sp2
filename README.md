# api_yamdb

*Групповой проект студентов Яндекс.Практикум по курсу **"API: интерфейс взаимодействия программ"***

Проект YaMDb собирает отзывы (Review) пользователей на произведения (Titles). Произведения делятся на категории: «Книги», «Фильмы», «Музыка». Список категорий (Category) может быть расширен администратором (например, можно добавить категорию «Изобразительное искусство» или «Ювелирка»).

**Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.**

В каждой категории есть произведения: книги, фильмы или музыка.

Произведению может быть присвоен жанр (Genre) из списка предустановленных (например, «Сказка», «Рок» или «Артхаус»). Новые жанры может создавать только администратор.

Благодарные или возмущённые пользователи оставляют к произведениям текстовые отзывы (Review) и ставят произведению оценку в диапазоне от одного до десяти (целое число); из пользовательских оценок формируется усреднённая оценка произведения — рейтинг (целое число). На одно произведение пользователь может оставить только один отзыв.

___

## Запуск:
1. Клонируйте репозиторий на локальную машину.

    ``git@github.com:farmat2909/infra_sp2.git``

2. Необходимо создать в папке /infra файл .env и заполнить переменными окружения.
    ``DB_ENGINE=django.db.backends.postgresql # указываем, что работаем c postgresql``
    ``DB_NAME=postgres # имя базы данных``
    ``POSTGRES_USER=postgres # логин для подключения к базе данных``
    ``POSTGRES_PASSWORD=postgres # пароль для подключения к БД (установите свой)``
    ``DB_HOST=db # название сервиса (контейнера)``
    ``DB_PORT=5432 # порт для подключения к БД``
    ``SECRET_KEY=ваш секретный ключ``

3. Находясь в папке /infra запустите сборку образа Docker.

    ``docker-compose up -d``

4. Выполните миграции.

    ``docker-compose exec web python manage.py migrate``

5. Создайте суперпользователя.

    ``docker-compose exec web python manage.py createsuperuser``

6. Выполните команду collectstatic.

    ``docker-compose exec web python manage.py collectstatic --no-input``

7. Команда позволяет наполнить базу данных тестовыми данными:

    ``docker-compose exec web python manage.py import_test_data``

8. Документация проекта.

    **[REDOC](http://localhost/redoc/)**

---
## Над проектом работали:
**[Вагнер Александр](https://github.com/KorsakovPV)** - управление пользователями: система регистрации и аутентификации, права доступа, работа с токеном, система подтверждения через e-mail.

**[Сущева Екатерина](https://github.com/MelatoZa)** - категории, жанры и произведения: модели, представления и эндпойнты для них.

**[Стельмахов Дмитрий](https://github.com/farmat2909)** - отзывы и комментарии: модели и представления, эндпойнты, права доступа для запросов. Рейтинги произведений.