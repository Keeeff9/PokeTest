from flask import Blueprint, abort, current_app, redirect, render_template, request, url_for

from app.services.pokemon_service import PageOutOfRangeError

bp = Blueprint("pokemon", __name__)


def _service():
    return current_app.extensions["pokemon_service"]

def _parse_page(raw):
    if not (raw.isascii() and raw.isdecimal() and len(raw) <= 7):
        raise ValueError("Parametro page invalido.")
    return int(raw)


@bp.route("/")
def index():
    try:
        page = _parse_page(request.args.get("page", "1"))
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