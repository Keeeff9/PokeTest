from flask import Blueprint, abort, current_app, redirect, render_template, request, url_for

from app.services.pokemon_service import PageOutOfRangeError

bp = Blueprint("pokemon", __name__)


def _service():
    return current_app.extensions["pokemon_service"]


@bp.route("/")
def index():
    page = request.args.get("page", default=1, type=int)
    try:
        data = _service().get_page(page)
    except ValueError:
        abort(400)
    except PageOutOfRangeError:
        abort(404)
    return render_template("index.html", **data)


@bp.route("/search")
def search():
    term = request.args.get("q", "").strip().lower()
    if not term:
        return redirect(url_for("pokemon.index"))
    return redirect(url_for("pokemon.detail", name_or_id=term))


@bp.route("/pokemon/<name_or_id>")
def detail(name_or_id):
    try:
        pokemon = _service().get_detail(name_or_id)
    except ValueError:
        abort(400)
    return render_template("detail.html", pokemon=pokemon)