import logging
import sys
from flask import Flask, request, Blueprint, render_template, abort
from pythonjsonlogger import jsonlogger
from app.posts_manager import get_posts, get_post_by_slug

# 1. Фильтр для сквозного Request-ID
class RequestIDFilter(logging.Filter):
    def filter(self, record):
        try:
            record.request_id = request.headers.get("X-Request-ID", "internal")
        except RuntimeError:
            record.request_id = "startup"
        return True

# 2. Настройка JSON-логирования
def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(request_id)s %(message)s"
    )
    
    handler.setFormatter(formatter)
    handler.addFilter(RequestIDFilter())
    logger.handlers = [handler]

# 3. Объявление блюпринта и маршрутов
main = Blueprint("main", __name__)

@main.route("/")
def index():
    recent_posts = get_posts()[:3]
    return render_template("index.html", recent_posts=recent_posts)

@main.route("/diary")
def diary():
    posts = get_posts()
    return render_template("diary.html", posts=posts)

@main.route("/diary/<slug>")
def post(slug):
    post_item = get_post_by_slug(slug)
    if not post_item:
        abort(404)
    return render_template("post.html", post=post_item)

@main.route("/resume")
def resume():
    return render_template("resume.html")

@main.route("/achievements")
def achievements():
    return render_template("achievements.html")

@main.route("/health")
def health():
    return {"status": "ok"}, 200

# 4. Фабрика приложения
def create_app():
    setup_logging()
    app = Flask(__name__)
    
    # Вот строчка, которой не хватало:
    app.register_blueprint(main)
    
    return app