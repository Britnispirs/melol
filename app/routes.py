from flask import Blueprint, render_template, abort
from app.posts_manager import get_posts, get_post_by_slug

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