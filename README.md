# devops.notes

Минималистичный личный сайт на **Python + Flask** для практики DevOps.

## Разделы

- **Главная**
- **Дневник** — заметки в Markdown (`app/posts/`)
- **Резюме**
- **Достижения**

Дизайн: чистый, без градиентов.

## Быстрый старт

### Локально (без Docker)

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python wsgi.py
# → http://127.0.0.1:8000
```

### Через Docker

```bash
docker compose up --build
# → http://localhost:8000
```

## Структура

```
.
├── app/
│   ├── __init__.py          # create_app()
│   ├── routes.py            # роуты + чтение Markdown-постов
│   ├── posts/               # дневник (*.md)
│   ├── templates/           # Jinja2
│   └── static/css/          # стили
├── wsgi.py                  # точка входа
├── requirements.txt
├── Dockerfile               # multi-stage
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## Как добавлять записи в дневник

1. Создай файл `app/posts/YYYY-MM-DD-slug.md`
2. Первая строка — заголовок (`# Заголовок`)
3. Опционально вторая строка: `Tags: docker, k8s, python`
4. Дальше обычный Markdown

Пример:

```markdown
# Моя новая заметка
Tags: kubernetes, practice

Текст заметки...
```

После сохранения запись появится в дневнике автоматически.

## Деплой

### Docker на VPS

```bash
docker build -t personal-site .
docker run -d --name site -p 80:8000 --restart unless-stopped personal-site
```

Или через `docker compose`.

### GitHub Actions

Workflow `ci.yml` при пуше:
- ставит зависимости
- проверяет, что приложение импортируется
- собирает Docker-образ

Дальше можно добавить деплой (ssh + docker, или Registry + pull на сервере).

## Что можно улучшить

- [ ] Деплой через GitHub Actions на VPS (ssh-action)
- [ ] Nginx как reverse-proxy + HTTPS
- [ ] Healthcheck endpoint
- [ ] Prometheus metrics
- [ ] Terraform / Ansible для инфраструктуры
- [ ] Перейти на Markdown + SSG (если захочется статику)

---

Сделано для практики. Не сиди без дела.
