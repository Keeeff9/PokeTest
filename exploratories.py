from app.clients.pokeapi_client import (
    PokeAPIClient,
    PokeAPIUnavailableError,
    PokemonNotFoundError,
)
from app.config import Config


def make_client(base_url=None, timeout=None):
    return PokeAPIClient(
        base_url or Config.POKEAPI_BASE_URL,
        timeout or Config.REQUEST_TIMEOUT,
    )


def run_case(num, desc, func, expected_exc=None, check=None):
    """Ejecuta un caso y compara resultado esperado vs actual."""
    detail = ""
    try:
        result = func()
    except Exception as exc:
        actual = type(exc).__name__
        ok = expected_exc is not None and isinstance(exc, expected_exc)
        detail = str(exc)
    else:
        actual = "OK"
        ok = expected_exc is None and (check(result) if check else True)

    status = "PASS" if ok else "FAIL"
    expected = expected_exc.__name__ if expected_exc else "OK"
    print(f"{num:>2} | {status} | esperado={expected:<26} | actual={actual:<26} | {desc}")
    if detail:
        print(f"     detalle: {detail}")


def observe(label, func):
    """Para casos sin resultado esperado definido: solo registra lo que ocurre."""
    try:
        result = func()
        print(f"[OBS] {label} -> OK: {str(result)[:120]}")
    except Exception as exc:
        print(f"[OBS] {label} -> {type(exc).__name__}: {exc}")


client = make_client()
is_pikachu = lambda r: r["id"] == 25

print("=== Casos del Paso 5 ===")
run_case(1, 'get_pokemon("pikachu")', lambda: client.get_pokemon("pikachu"), check=is_pikachu)
run_case(2, "get_pokemon(25)", lambda: client.get_pokemon(25), check=is_pikachu)
run_case(3, 'get_pokemon("PIKACHU")', lambda: client.get_pokemon("PIKACHU"), check=is_pikachu)
run_case(4, 'get_pokemon("  pikachu  ")', lambda: client.get_pokemon("  pikachu  "), check=is_pikachu)
run_case(5, 'get_pokemon("")', lambda: client.get_pokemon(""), ValueError)
run_case(6, 'get_pokemon("   ")', lambda: client.get_pokemon("   "), ValueError)
run_case(7, 'get_pokemon("missingno")', lambda: client.get_pokemon("missingno"), PokemonNotFoundError)
run_case(8, "get_pokemon(0)", lambda: client.get_pokemon(0), PokemonNotFoundError)
run_case(9, "list_pokemon(limit=0)", lambda: client.list_pokemon(limit=0), ValueError)
run_case(10, "list_pokemon(limit=101)", lambda: client.list_pokemon(limit=101), ValueError)
run_case(11, "list_pokemon(offset=-1)", lambda: client.list_pokemon(offset=-1), ValueError)
run_case(
    12,
    "base_url invalida",
    lambda: make_client(base_url="https://noexiste.invalid").get_pokemon("pikachu"),
    PokeAPIUnavailableError,
)
run_case(
    13,
    "timeout=0.001",
    lambda: make_client(timeout=0.001).get_pokemon("pikachu"),
    PokeAPIUnavailableError,
)

print()
print("=== Observaciones (sin resultado esperado definido) ===")
observe('get_pokemon("pikachu/")', lambda: client.get_pokemon("pikachu/"))
observe('get_pokemon("../berry")', lambda: client.get_pokemon("../berry"))
observe("get_pokemon(1.5)", lambda: client.get_pokemon(1.5))
observe('get_pokemon("mr. mime")', lambda: client.get_pokemon("mr. mime"))
observe('get_pokemon("mr-mime")', lambda: client.get_pokemon("mr-mime"))