from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required

from db import db
from models import ToDoModel
from schemas import PlainToDoSchema, ToDoUpdateSchema
from sqlalchemy.exc import SQLAlchemyError

blp = Blueprint("ToDos", "todos", description="Endpoints sui To-Do")


@blp.route("/todo/")
class ToDoList(MethodView):

    @blp.response(200, PlainToDoSchema(many=True))
    def get(self):  # GET method: return tutti i To-Do
        return ToDoModel.query.all()

    @blp.response(201, description="Inserimento di un todo nel DB", example={"message": "Todo inserted"})
    @blp.arguments(PlainToDoSchema)
    def post(self, todo_receive):  # POST method: salvataggio nel DB
        todo = ToDoModel(**todo_receive)
        try:
            db.session.add(todo)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="Internal server error")
        return {"message": "Todo inserted"}, 201


@blp.route("/todo/<int:todo_id>/")
class ToDo(MethodView):

    @blp.response(200, PlainToDoSchema, description="Restituisce il To-Do richiesto dall'utente")
    def get(self, todo_id):
        todo = ToDoModel.query.get_or_404(todo_id)
        return todo

    @blp.response(200, description="Effettua un'ipotetica modifica di un To-Do selezionato. PATCH method!",
                  example={"todo_text": "prova modifica", "fatto": True})
    @blp.arguments(ToDoUpdateSchema)
    def patch(self, todo_receive_updated, todo_id):  # PATCH method, aggiorno
        todo: ToDoModel = ToDoModel.query.get_or_404(todo_id)  # ricerco

        # verifico e modifico
        if "todo_text" in todo_receive_updated:
            todo.todo_text = todo_receive_updated["todo_text"]
        if "fatto_text" in todo_receive_updated:
            todo.fatto = todo_receive_updated["fatto"]

        # Salvo modifiche
        db.session.add(todo)
        db.session.commit()
        return {"message": "ToDo Updated."}

    @blp.response(200, description="Elimina un To-Do")
    @blp.alt_response(404, description="To-Do non trovato")
    def delete(self, todo_id):
        todo: ToDoModel = ToDoModel.query.get_or_404(todo_id)  # ricerco
        # cancello
        db.session.delete(todo)
        db.session.commit()
        return {"message": "ToDo deleted."}
