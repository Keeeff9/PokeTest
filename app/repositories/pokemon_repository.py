import logging

from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models.pokemon import PokemonCache, utc_now

logger = logging.getLogger(__name__)

MAX_ID = 2**31 - 1 


class PokemonRepository:
    def get(self, identifier):
        try:
            if identifier.isdecimal():
                number = int(identifier)
                if number > MAX_ID:
                    return None
                return db.session.get(PokemonCache, number)
            stmt = db.select(PokemonCache).filter_by(name=identifier)
            return db.session.execute(stmt).scalar_one_or_none()
        except SQLAlchemyError:
            logger.warning("Fallo al leer la cache local.", exc_info=True)
            db.session.rollback()
            return None

    def save(self, data):
        try:
            db.session.merge(PokemonCache(**data, fetched_at=utc_now()))
            db.session.commit()
            return True
        except SQLAlchemyError:
            logger.warning("Fallo al escribir en la cache local.", exc_info=True)
            db.session.rollback()
            return False