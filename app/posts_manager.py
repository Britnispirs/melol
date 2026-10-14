from pathlib import Path
import re
from datetime import datetime
import markdown

POSTS_DIR = Path(__file__).parent / "posts"

RU_MONTHS = [
    "января", "февраля", "марта", "апреля", "мая", "июня",
    "июля", "августа", "сентября", "октября", "ноября", "декабря"
]


def slugify(text: str) -> str:
    """Транслитерация и очистка заголовка для создания красивого slug."""
    translit_table = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    }
    text = (text or "").lower().strip()
    result = []
    for char in text:
        if char in translit_table:
            result.append(translit_table[char])
        elif char.isalnum() or char in ('-', '_'):
            result.append(char)
        elif char.isspace():
            result.append('-')

    slug = ''.join(result)
    slug = re.sub(r'[-\s]+', '-', slug).strip('-_')
    return slug or "post"


def format_date_human(date_str: str) -> str:
    """Форматирует дату YYYY-MM-DD в красивую русскую строку."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return f"{dt.day} {RU_MONTHS[dt.month - 1]} {dt.year}"
    except Exception:
        return date_str


def render_markdown(text: str) -> str:
    """Рендерит markdown текст с расширениями."""
    return markdown.markdown(text or "", extensions=["fenced_code", "tables", "codehilite"]) if "codehilite" in markdown.markdown.__module__ else markdown.markdown(text or "", extensions=["fenced_code", "tables"])


def parse_post_file(md_file: Path) -> dict | None:
    """Парсит markdown файл поста."""
    name = md_file.stem
    parts = name.split("-", 3)
    if len(parts) < 4:
        return None

    date_str = f"{parts[0]}-{parts[1]}-{parts[2]}"
    slug = parts[3]

    content = md_file.read_text(encoding="utf-8")
    lines = content.strip().split("\n")
    title = lines[0].lstrip("# ").strip() if lines else slug
    body = "\n".join(lines[1:]).strip()

    tags = []
    tags_raw = ""
    if body.startswith("Tags:"):
        tag_line, body = body.split("\n", 1)
        tags_raw = tag_line.replace("Tags:", "").strip()
        tags = [t.strip() for t in tags_raw.split(",") if t.strip()]
        body = body.strip()

    plain = body[:220].rsplit(" ", 1)[0] + "…" if len(body) > 220 else body

    return {
        "date": date_str,
        "date_human": format_date_human(date_str),
        "slug": slug,
        "filename": md_file.name,
        "title": title,
        "tags": tags,
        "tags_raw": tags_raw,
        "summary": plain,
        "body_raw": body,
        "body_html": markdown.markdown(body, extensions=["fenced_code", "tables"]),
    }


def get_posts() -> list[dict]:
    """Возвращает все посты, отсортированные по убыванию даты."""
    posts = []
    if not POSTS_DIR.exists():
        return posts

    for md_file in sorted(POSTS_DIR.glob("*.md"), reverse=True):
        post_data = parse_post_file(md_file)
        if post_data:
            posts.append(post_data)

    return posts


def get_post_by_slug(slug: str) -> dict | None:
    """Находит пост по слагу."""
    posts = get_posts()
    return next((p for p in posts if p["slug"] == slug), None)


def find_post_file(slug: str) -> Path | None:
    """Находит физический файл поста по его слагу."""
    if not POSTS_DIR.exists():
        return None
    for md_file in POSTS_DIR.glob("*.md"):
        parts = md_file.stem.split("-", 3)
        if len(parts) >= 4 and parts[3] == slug:
            return md_file
    return None


def save_post(title: str, slug: str, date_str: str, tags: list[str] | str, body: str, old_slug: str | None = None) -> str:
    """Создает или обновляет markdown пост."""
    POSTS_DIR.mkdir(parents=True, exist_ok=True)

    clean_slug = slugify(slug or title)
    
    # Парсим теги
    if isinstance(tags, str):
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    else:
        tag_list = [str(t).strip() for t in tags if str(t).strip()]

    tag_line = f"Tags: {', '.join(tag_list)}\n\n" if tag_list else "\n"
    content = f"# {title.strip()}\n{tag_line}{body.strip()}\n"

    new_filename = f"{date_str}-{clean_slug}.md"
    new_path = POSTS_DIR / new_filename

    if old_slug:
        old_file = find_post_file(old_slug)
        if old_file and old_file.resolve() != new_path.resolve() and old_file.exists():
            old_file.unlink()

    new_path.write_text(content, encoding="utf-8")
    return clean_slug


def delete_post(slug: str) -> bool:
    """Удаляет markdown пост."""
    file_path = find_post_file(slug)
    if file_path and file_path.exists():
        file_path.unlink()
        return True
    return False
