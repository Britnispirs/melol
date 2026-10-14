from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort, jsonify
from functools import wraps
from datetime import datetime
import os
from app.posts_manager import (
    get_posts,
    get_post_by_slug,
    save_post,
    delete_post,
    render_markdown,
    slugify
)

admin = Blueprint("admin", __name__, url_prefix="/admin")

# Пароль администратора, по умолчанию Yanedaun2008 (можно переопределить через переменную окружения)
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Yanedaun2008")


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Требуется вход администратора.", "warning")
            return redirect(url_for("admin.login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@admin.route("/login", methods=["GET", "POST"])
def login():
    if session.get("is_admin"):
        return redirect(url_for("admin.index"))

    if request.method == "POST":
        password = request.form.get("password", "")
        if password == ADMIN_PASSWORD:
            session["is_admin"] = True
            session.permanent = True
            flash("Успешный вход в панель администратора!", "success")
            next_url = request.args.get("next")
            # Простая защита от open redirect
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            return redirect(url_for("admin.index"))
        else:
            flash("Неверный пароль администратора. Попробуйте еще раз.", "error")

    return render_template("admin/login.html")


@admin.route("/logout")
def logout():
    session.pop("is_admin", None)
    flash("Вы вышли из панели администратора.", "info")
    return redirect(url_for("main.index"))


@admin.route("/")
@admin_required
def index():
    posts = get_posts()
    all_tags = set()
    for p in posts:
        for t in p.get("tags", []):
            all_tags.add(t)

    return render_template(
        "admin/index.html",
        posts=posts,
        total_posts=len(posts),
        total_tags=len(all_tags),
        latest_date=posts[0]["date"] if posts else "—"
    )


@admin.route("/post/new", methods=["GET", "POST"])
@admin_required
def new_post():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        slug = request.form.get("slug", "").strip()
        date_str = request.form.get("date", "").strip() or datetime.now().strftime("%Y-%m-%d")
        tags = request.form.get("tags", "").strip()
        body = request.form.get("body", "").strip()

        if not title:
            flash("Заголовок поста обязателен.", "error")
            return render_template("admin/editor.html", post={
                "title": title, "slug": slug, "date": date_str, "tags_raw": tags, "body_raw": body
            }, is_new=True)

        if not body:
            flash("Текст поста не может быть пустым.", "error")
            return render_template("admin/editor.html", post={
                "title": title, "slug": slug, "date": date_str, "tags_raw": tags, "body_raw": body
            }, is_new=True)

        try:
            saved_slug = save_post(
                title=title,
                slug=slug,
                date_str=date_str,
                tags=tags,
                body=body
            )
            flash(f"Пост «{title}» успешно опубликован!", "success")
            return redirect(url_for("main.post", slug=saved_slug))
        except Exception as e:
            flash(f"Ошибка при сохранении поста: {str(e)}", "error")
            return render_template("admin/editor.html", post={
                "title": title, "slug": slug, "date": date_str, "tags_raw": tags, "body_raw": body
            }, is_new=True)

    # GET
    default_post = {
        "title": "",
        "slug": "",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "tags_raw": "",
        "body_raw": "## Что сделано\n\n- Первый пункт\n- Второй пункт\n\n```bash\n# Команда\n```\n\n## Выводы\n\n"
    }
    return render_template("admin/editor.html", post=default_post, is_new=True)


@admin.route("/post/edit/<slug>", methods=["GET", "POST"])
@admin_required
def edit_post(slug):
    post = get_post_by_slug(slug)
    if not post:
        flash("Пост не найден.", "error")
        return redirect(url_for("admin.index"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        new_slug = request.form.get("slug", "").strip() or slug
        date_str = request.form.get("date", "").strip() or post["date"]
        tags = request.form.get("tags", "").strip()
        body = request.form.get("body", "").strip()

        if not title:
            flash("Заголовок поста обязателен.", "error")
            return render_template("admin/editor.html", post={
                "title": title, "slug": new_slug, "date": date_str, "tags_raw": tags, "body_raw": body
            }, is_new=False, original_slug=slug)

        if not body:
            flash("Текст поста не может быть пустым.", "error")
            return render_template("admin/editor.html", post={
                "title": title, "slug": new_slug, "date": date_str, "tags_raw": tags, "body_raw": body
            }, is_new=False, original_slug=slug)

        try:
            saved_slug = save_post(
                title=title,
                slug=new_slug,
                date_str=date_str,
                tags=tags,
                body=body,
                old_slug=slug
            )
            flash(f"Пост «{title}» успешно обновлен!", "success")
            return redirect(url_for("main.post", slug=saved_slug))
        except Exception as e:
            flash(f"Ошибка при обновлении поста: {str(e)}", "error")
            return render_template("admin/editor.html", post={
                "title": title, "slug": new_slug, "date": date_str, "tags_raw": tags, "body_raw": body
            }, is_new=False, original_slug=slug)

    return render_template("admin/editor.html", post=post, is_new=False, original_slug=slug)


@admin.route("/post/delete/<slug>", methods=["POST"])
@admin_required
def delete_post_route(slug):
    post = get_post_by_slug(slug)
    title = post["title"] if post else slug
    success = delete_post(slug)
    if success:
        flash(f"Пост «{title}» успешно удален.", "success")
    else:
        flash("Не удалось найти или удалить указанный пост.", "error")
    return redirect(url_for("admin.index"))


@admin.route("/api/preview", methods=["POST"])
@admin_required
def api_preview():
    data = request.get_json(silent=True) or request.form
    text = data.get("markdown", "")
    html = render_markdown(text)
    return jsonify({"html": html})


@admin.route("/api/slugify", methods=["POST"])
@admin_required
def api_slugify():
    data = request.get_json(silent=True) or request.form
    title = data.get("title", "")
    return jsonify({"slug": slugify(title)})
