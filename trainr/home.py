# trainr/home.py

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from trainr.auth import login_required
from trainr.db import get_db

bp = Blueprint('blog', __name__)


  # home page
@bp.route("/")
def index():
    db = get_db()
    posts = db.execute(
        'select post_id, title, body, created, author_id, username'
        ' From post p join user u on p.author_id = u.user_id'
        ' order by created desc'
    ).fetchall()
    return render_template('home/index.html', posts=posts)