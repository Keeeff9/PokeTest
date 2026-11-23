import math

SPRITE_URL = (
    "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/{id}.png"
)


class PageOutOfRangeError(Exception):
    """La pagina solicitada excede el total de paginas disponibles."""


class PokemonService:
    def __init__(self, client, per_page=20):
        self.client = client
        self.per_page = per_page

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
        return self.client.get_pokemon(name_or_id)