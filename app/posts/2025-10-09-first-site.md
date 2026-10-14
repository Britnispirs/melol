# Запустил личный сайт как DevOps-проект
Tags: docker, flask, python, ci/cd

Решил не просто сидеть, а сделать что-то руками. Нужен был проект, который одновременно:

- даёт практику
- можно показывать
- легко поддерживать

Выбрал минималистичный личный сайт на **Python + Flask**. Посты пишу в Markdown — удобно и быстро.

## Что сделал

- Структура: главная, дневник, резюме, достижения
- Чистый CSS без градиентов и лишней анимации
- Markdown-посты в папке `app/posts/`
- Dockerfile (multi-stage) + Gunicorn
- docker-compose для локального запуска
- GitHub Actions для деплоя

## Заметки по Docker

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY . .
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "wsgi:app"]
```

## Что дальше

- Добавить больше записей в дневник
- Написать нормальное резюме
- Попробовать деплой на VPS
- Добавить мониторинг

Главное — не останавливаться и фиксировать прогресс.
