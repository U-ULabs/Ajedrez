from flask import request
from flask_restful import Resource
from marshmallow import ValidationError

from extensions import db
from models import Jugador
from schemas import jugador_schema, jugadores_schema
from . import api

class Jugadoresq(Resource):
    # GET /api/empleados
    def get(self):
        jugadores = Empleado.query.order_by(Empleado.idEmpleado.asc()).all()
        return empleados_schema.dump(jugadores), 200

    # POST /api/empleados
    def post(self):
        data = request.get_json()
        if not data:
            return {"message": "Cuerpo JSON requerido."}, 400
        try:
            empleado = empleado_schema.load(data)
        except ValidationError as err:
            return {"errors": err.messages}, 422

        db.session.add(empleado)
        db.session.commit()
        return empleado_schema.dump(empleado), 201


class EmpleadoDetail(Resource):
    # GET /api/empleados/<id>
    def get(self, id):
        empleado = Empleado.query.get_or_404(id)
        return empleado_schema.dump(empleado), 200

    # PUT /api/empleados/<id>
    def put(self, id):
        empleado = Empleado.query.get_or_404(id)
        data = request.get_json()
        if not data:
            return {"message": "Cuerpo JSON requerido."}, 400
        try:
            empleado = empleado_schema.load(data, instance=empleado, partial=False)
        except ValidationError as err:
            return {"errors": err.messages}, 422

        db.session.commit()
        return empleado_schema.dump(empleado), 200

    # DELETE /api/empleados/<id>
    def delete(self, id):
        empleado = Empleado.query.get_or_404(id)
        db.session.delete(empleado)
        db.session.commit()
        return {"message": "Empleado eliminado"}, 200


# Registro de rutas en el Api del blueprint
api.add_resource(Empleados, "/empleados", endpoint="empleados")
api.add_resource(EmpleadoDetail, "/empleados/<int:id>", endpoint="empleado_detail")
