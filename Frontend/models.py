from extensions import db
from sqlalchemy import Numeric

class Jugador(db.Model):
    __tablename__ = "jugador"

    idJugador = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(100), nullable=False)
    edad = db.Column(Numeric(10, 2), nullable=False)
    puntos = db.Column(Numeric(10, 2), nullable=False)

    def __repr__(self) -> str:
        return f"<Jugador {self.idJugador} - {self.nombre}>"
