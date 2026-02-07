from extensions import ma, db
from marshmallow import fields, validate
from models import Jugador

class JugadorSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Jugador
        load_instance = True
        sqla_session = db.session

    idJugador = ma.auto_field(dump_only=True)
    nombre = ma.auto_field(required=True, validate=validate.Length(min=1, max=100))
    edad = fields.Float(required=True, validate=validate.Range(min=0))
    puntos = fields.Float(required=True, validate=validate.Range(min=0))

jugador_schema = JugadorSchema()
jugadores_schema = JugadorSchema(many=True)
