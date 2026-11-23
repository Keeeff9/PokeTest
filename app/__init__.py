import logging
from flask import Flask, render_template
from app.extensions import db
from app.models.pokemon import PokemonCache  
from app.repositories.pokemon_repository import PokemonRepository
from app.clients.pokeapi_client import (
    PokeAPIClient,
    PokeAPIError,
    PokeAPIUnavailableError,
    PokemonNotFoundError,
)
from app.config import Config
from app.services.pokemon_service import PokemonService


def create_app(config_class=Config):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    client = PokeAPIClient(
        app.config["POKEAPI_BASE_URL"],
        app.config["REQUEST_TIMEOUT"],
    )
    app.extensions["pokemon_service"] = PokemonService(
        client,
        PokemonRepository(),
        per_page=app.config["PER_PAGE"],
        cache_ttl_seconds=app.config["CACHE_TTL_SECONDS"],
    )

    from app.routes.pokemon import bp as pokemon_bp

    app.register_blueprint(pokemon_bp)

    @app.route("/health")
    def health():
        return {"status": "ok"}, 200

    _register_error_handlers(app)
    return app


def _error_page(code, title, message):
    return render_template("error.html", code=code, title=title, message=message), code


def _register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(_):
        return _error_page(400, "Solicitud invalida", "Los parametros enviados no son validos.")

    @app.errorhandler(404)
    def not_found(_):
        return _error_page(404, "No encontrado", "El recurso solicitado no existe.")

    @app.errorhandler(PokemonNotFoundError)
    def pokemon_not_found(_):
        return _error_page(404, "Pokemon no encontrado", "No existe un Pokemon con ese nombre o numero.")

    @app.errorhandler(PokeAPIUnavailableError)
    def api_unavailable(_):
        return _error_page(503, "Servicio no disponible", "No se pudo contactar con PokeAPI. Intenta nuevamente en unos minutos.")

    @app.errorhandler(PokeAPIError)
    def api_error(_):
        return _error_page(502, "Error del proveedor", "PokeAPI devolvio una respuesta inesperada.")