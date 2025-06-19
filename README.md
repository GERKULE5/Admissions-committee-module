# Admissions-committee-module
# API для интерактивной доски приёмной комиссии

Этот микросервис парсит данные с сайта [nke.ru](http://www.nke.ru) и предоставляет их через защищённое FastAPI.

Подходит для интеграции с интерактивной доской, которая обновляется каждые 30 минут.

## Что предоставляет API

- Список специальностей:
  - id специальности
  - Название
  - Описание
  - Префикс(ИС, СА, ... , None)
  - Код специальности
  - Тип групп [
    Тип группы,
    Академическая база,
    Срок обучения,
    Свободные места,
    Минимальный средний балл
  ]

- Рейтинг специальностей:
  - Код специальности
  - Название
  - План по местам
  - Подано заявлений
  - Конкурс(чел. на место) 
- Информация об образовательном кредите

## Авторизация

Все маршруты защищены статическим Bearer-токеном.

## Как развернуть проект

### 1. Склонируйте репозиторий

```bash
git clone https://github.com/GERKULE5/Admissions-committee-module.git 
cd Admissions-committee-module
```
### 2. Создайте виртуальное окружение и активируйте его

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Подгрузите библиотеки

```bash
pip install -r requirements.txt
```

### 4. Запустите локальный сервер

C помошью uvicorn
```bash
uvicorn main:app --reload
```

или с помощью Docker соберите контейнер

```bash
docker build -t admissions-committee-module-api .
```
далее запустите контейнер с токеном

```bash
docker run -d -p 8000:80 -e TOKEN=вставьте токен admissions-committee-module-api
```

## Доступные маршруты

> GET /specialties/ - все специальности

> GET /specialties/{code} - по коду специальности

> GET /specialties/rating/ - рейтинг специальностей

> GET /educational_loan/ - информация о кредите
 
---

## Все маршруты поддерживают параметры запроса:
```
(Пример)

GET /specialties/?base=NOT_FULL&group_type=FREE
```

## Как завершить работу сервера?

```
docker stop admissions-committee-module-api
```

