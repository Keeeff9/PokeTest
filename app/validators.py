import re

_IDENTIFIER_RE = re.compile(r"[a-z0-9-]{1,64}")


def normalize_identifier(value):
    """Normaliza y valida un nombre o id de Pokemon (lista blanca ASCII)."""
    identifier = str(value).strip().lower()
    if not identifier:
        raise ValueError("El nombre o id del Pokemon no puede estar vacio.")
    if not _IDENTIFIER_RE.fullmatch(identifier):
        raise ValueError("El identificador contiene caracteres no permitidos.")
    return identifier