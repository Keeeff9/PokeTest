import logging
import math
from datetime import timedelta

from app.clients.pokeapi_client import PokeAPIUnavailableError
from app.models.pokemon import utc_now
from app.validators import normalize_identifier

logger = logging.getLogger(__name__)

SPRITE_URL = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{id}.png"
)


class PageOutOfRangeError(Exception):
    """La pagina solicitada excede el total de paginas disponibles."""


class PokemonService:
    def __init__(
        self,
        client,
        repository,
        per_page=20,
        cache_ttl_seconds=7 * 24 * 3600,
        clock=utc_now,
    ):
        self.client = client
        self.repository = repository
        self.per_page = per_page
        self.cache_ttl = timedelta(seconds=cache_ttl_seconds)
        self.clock = clock

    def get_page(self, page):
        if page < 1:
            raise ValueError("El numero de pagina debe ser mayor o igual a 1.")

        offset = (page - 1) * self.per_page
        data = self.client.list_pokemon(limit=self.per_page, offset=offset)

        total_pages = max(1, math.ceil(data["count"] / self.per_page))
        if page > total_pages:
            raise PageOutOfRangeError(f"La pagina {page} no existe.")

        pokemon = [
            {
                "id": item["id"],
                "name": item["name"],
                "sprite": SPRITE_URL.format(id=item["id"]),
            }
            for item in data["results"]
        ]

        return {
            "pokemon": pokemon,
            "page": page,
            "total_pages": total_pages,
            "count": data["count"],
            "has_prev": page > 1,
            "has_next": page < total_pages,
        }

    def get_detail(self, name_or_id):
        identifier = normalize_identifier(name_or_id)
        cached = self.repository.get(identifier)

        if cached is not None and not self._is_stale(cached):
            logger.info("cache hit: %s", identifier)
            return cached.to_dict()

        logger.info("cache miss: %s", identifier)
        try:
            data = self.client.get_pokemon(identifier)
        except PokeAPIUnavailableError:
            if cached is not None:
                logger.warning("PokeAPI no disponible; se sirve dato vencido: %s", identifier)
                return cached.to_dict()
            raise

        self.repository.save(data)
        return data

    def _is_stale(self, record):
        return self.clock() - record.fetched_at > self.cache_ttl