# trainr/home.py

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort

from trainr.auth import login_required
from trainr.db import get_db

bp = Blueprint("home", __name__)


# home page
@bp.route("/")
def index():
    db = get_db()
    posts = db.execute(
        "select post_id, title, body, created, author_id, username"
        " from post p join user u on p.author_id = u.user_id"
        " order by created desc"
    ).fetchall()
    return render_template("home/index.html", posts=posts)


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required"

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, author_id)" " VALUES (?, ?, ?)",
                (title, body, g.user["user_id"]),
            )
            db.commit()
            return redirect(url_for("home.index"))

    return render_template("home/create.html")


def get_post(id, check_author=True):
    post = get_db().execute(
        "select p.post_id, title, body, created, author_id, username"
        " from post p join user u on p.author_id = u.user_id"
        " where p.post_id = ?",
        (id,),
    ).fetchone()
    
    #p = post.fetchone()
    if post is None:
        abort(404, f"Post id {id} does not exist!!")
    
    if check_author and post['author_id'] != g.user['user_id']:
        abort(403)
    
    return post


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    post = get_post(id)
    print(post['post_id'])
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "update post set title = ?, body = ?" " where post_id = ?",
                (title, body, id),
            )
            db.commit()
            return redirect(url_for("home.index"))

    return render_template("home/update.html", post=post)


@bp.route("/<int:id>", methods=("GET",))
@login_required
def show_post(id):
    post = get_post(id, False)
    return render_template("home/post.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute("delete from post where post_id = ?", (id,))
    db.commit()
    return redirect(url_for("home.index"))
