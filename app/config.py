class Config:
    POKEAPI_BASE_URL = "https://pokeapi.co/api/v2"
    REQUEST_TIMEOUT = 5 
    PER_PAGE = 20
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///pokedex.db"  # se crea en instance/
    CACHE_TTL_SECONDS = 7 * 24 * 3600