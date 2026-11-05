import os
import sys
import logging
from flask import Flask, Blueprint, render_template, request, abort
from pythonjsonlogger import jsonlogger
from app.posts_manager import get_posts, get_post_by_slug
from app.admin import admin as admin_blueprint

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

# 3. Основной блюпринт (main)
main = Blueprint("main", __name__)
logger = logging.getLogger(__name__)

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
    
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    @app.after_request
    def log_response(response):
        if request.path != "/health":
            logger.info(
                "Request handled",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                    "remote_addr": request.headers.get("X-Real-IP", request.remote_addr),
                }
            )
        return response

    # Регистрируем основной сайт и полноценную админку
    app.register_blueprint(main)
    app.register_blueprint(admin_blueprint)
    
    return app