from datetime import datetime, timezone

from app.extensions import db


def utc_now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class PokemonCache(db.Model):
    __tablename__ = "pokemon_cache"

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)  # id de PokeAPI
    name = db.Column(db.String(64), unique=True, nullable=False)
    height_m = db.Column(db.Float, nullable=False)
    weight_kg = db.Column(db.Float, nullable=False)
    types = db.Column(db.JSON, nullable=False)
    abilities = db.Column(db.JSON, nullable=False)
    stats = db.Column(db.JSON, nullable=False)
    sprite = db.Column(db.String(300), nullable=True)
    fetched_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "height_m": self.height_m,
            "weight_kg": self.weight_kg,
            "types": self.types,
            "abilities": self.abilities,
            "stats": self.stats,
            "sprite": self.sprite,
        }