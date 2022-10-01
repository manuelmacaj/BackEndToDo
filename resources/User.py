from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

from db import db
from models import UserModel, ToDoModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from schemas import LoginUserSchema, PlainUserRegisterSchema, ToDoSchema

blp = Blueprint("User", "user", description="User management")


@blp.route("/sign-up/")
class UserRegister(MethodView):

    @blp.arguments(PlainUserRegisterSchema)
    def post(self, user_data):  # POST method: registrazione utente
        user = UserModel(**user_data)
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            abort(401, message="Email already exists. Please try again")
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the item")

        return {"message": "Registration completed successfully", "status": "created"}, 201


@blp.route("/sign-in/")
class UserLogin(MethodView):

    @blp.arguments(LoginUserSchema)
    @blp.response(200, description="Generate a JWT token for the logged user.")
    @blp.alt_response(401, description="Invalid credentials",
                      example={"message": "Invalid credentials. Please try again"})
    def post(self, user_login):  # POST method: login utente
        user: UserModel = UserModel.query.filter(
            UserModel.email == user_login["email"]
        ).first()

        if user and (user.password == user_login["password"]):
            access_token = create_access_token(identity=user.id)
            return {"access_token": access_token,
                    "id": user.id}, 200
        abort(401, message="Invalid credentials. Please try again")


@blp.route("/user/<int:user_id>/")
class User(MethodView):

    @blp.response(200, PlainUserRegisterSchema)
    def get(self, user_id):  # GET Method: Informazioni utente
        user = UserModel.query.get_or_404(user_id)
        if user:
            return user
        abort(404, message="User not exists.")


@blp.route("/user/<int:user_id>/todo/")
class UserToDo(MethodView):
    @jwt_required()
    @blp.response(200, ToDoSchema(many=True), description="Return all To-Do created from user.")
    def get(self, user_id):
        jwt_user_id = get_jwt_identity()
        if user_id != jwt_user_id:
            abort(403, message="You can't enter in this section.")

        return ToDoModel.query.filter(ToDoModel.user_id == user_id)

    @jwt_required()
    @blp.arguments(ToDoSchema)
    def post(self, user_input_todo, user_id):
        todo = ToDoModel(**user_input_todo, user_id=user_id)
        try:
            db.session.add(todo)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="Internal server error.")
        return {"message": "Todo inserted correctly."}, 201


@blp.route("/user/<int:user_id>/todo/<int:todo_id>/")
class UserToDoDetail(MethodView):
    @jwt_required()
    @blp.response(200, ToDoSchema, description="Restituisce il To-Do richiesto dall'utente")
    def get(self, user_id, todo_id):
        jwt_user_id = get_jwt_identity()
        if user_id != jwt_user_id:
            abort(403, message="You can't enter in this section.")
        todo = ToDoModel.query.get_or_404(todo_id)
        return todo
