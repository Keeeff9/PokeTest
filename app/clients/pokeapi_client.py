import requests


class PokeAPIError(Exception):
    """Error base para cualquier fallo del cliente de PokeAPI."""


class PokemonNotFoundError(PokeAPIError):
    """El recurso solicitado no existe (HTTP 404)."""


class PokeAPIUnavailableError(PokeAPIError):
    """Fallo de red, timeout o error 5xx del proveedor externo."""


class PokeAPIClient:
    def __init__(self, base_url, timeout=5, session=None):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = session or requests.Session()

    # ---------- API pública ----------

    def get_pokemon(self, name_or_id):
        identifier = str(name_or_id).strip().lower()
        if not identifier:
            raise ValueError("El nombre o id del Pokemon no puede estar vacio.")

        data = self._get(f"pokemon/{identifier}")
        return self._parse_pokemon(data)

    def list_pokemon(self, limit=20, offset=0):
        if not 1 <= limit <= 100:
            raise ValueError("limit debe estar entre 1 y 100.")
        if offset < 0:
            raise ValueError("offset no puede ser negativo.")

        data = self._get("pokemon", params={"limit": limit, "offset": offset})
        return {
            "count": data["count"],
            "results": [
                {
                    "id": self._extract_id(item["url"]),
                    "name": item["name"],
                }
                for item in data["results"]
            ],
        }

    # ---------- Internos ----------

    def _get(self, path, params=None):
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
        except requests.Timeout as exc:
            raise PokeAPIUnavailableError("Timeout al consultar PokeAPI.") from exc
        except requests.RequestException as exc:
            raise PokeAPIUnavailableError(f"Error de red: {exc}") from exc

        if response.status_code == 404:
            raise PokemonNotFoundError(f"Recurso no encontrado: {path}")
        if response.status_code >= 500:
            raise PokeAPIUnavailableError(
                f"PokeAPI respondio con {response.status_code}."
            )
        if not response.ok:
            raise PokeAPIError(f"Respuesta inesperada: {response.status_code}.")

        try:
            return response.json()
        except ValueError as exc:
            raise PokeAPIError("La respuesta no es un JSON valido.") from exc

    @staticmethod
    def _extract_id(resource_url):
        # Ej: "https://pokeapi.co/api/v2/pokemon/25/" -> 25
        return int(resource_url.rstrip("/").split("/")[-1])

    @staticmethod
    def _parse_pokemon(data):
        return {
            "id": data["id"],
            "name": data["name"],
            "height_m": data["height"] / 10,
            "weight_kg": data["weight"] / 10,
            "types": [t["type"]["name"] for t in data["types"]],
            "abilities": [a["ability"]["name"] for a in data["abilities"]],
            "stats": {s["stat"]["name"]: s["base_stat"] for s in data["stats"]},
            "sprite": data["sprites"]["front_default"],
        }