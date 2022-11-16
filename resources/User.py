from flask_smorest import Blueprint, abort
from flask.views import MethodView
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from passlib.hash import pbkdf2_sha256

from db import db
from models import UserModel, ToDoModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas import LoginUserSchema, PlainUserRegisterSchema, ToDoSchema, ToDoUpdateSchema

blp = Blueprint("User", "user", description="User API function")


@blp.route("/sign-up/")
class UserRegister(MethodView):
    @blp.arguments(PlainUserRegisterSchema)
    def post(self, user_data):  # POST method: registrazione utente
        user = UserModel(**user_data)
        # pwd = pbkdf2_sha256.hash(user.password)
        user.password = pbkdf2_sha256.hash(user.password)
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            abort(401, message="Email already exists. Please try again")
        except SQLAlchemyError:
            abort(500, message="An error occurred while created the user")
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

        if user and pbkdf2_sha256.verify(user_login["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(user.id)
            return {"access_token": access_token,
                    "refresh_token": refresh_token,
                    "id": user.id}, 200
        abort(401, message="Invalid credentials. Please try again")


@blp.route("/user/<int:user_id>/")
class User(MethodView):
    @blp.response(200, PlainUserRegisterSchema, description="Return the user from DB.")
    @blp.alt_response(404, description="User not found into the database.")
    def get(self, user_id):  # GET Method: Informazioni utente
        user = UserModel.query.get_or_404(user_id)
        if user:
            return user
        abort(404, message="User not exists.")


@blp.route("/user/<int:user_id>/todo/")
class UserToDo(MethodView):
    @jwt_required(fresh=True)
    @blp.response(200, ToDoSchema(many=True), description="Return all To-Do created from user.")
    @blp.alt_response(403, description="Error if someone try to enter in forbidden section.")
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


@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_access_token}, 200


@blp.route("/user/<int:user_id>/todo/<int:todo_id>/")
class UserToDoDetail(MethodView):
    @jwt_required()
    @blp.response(200, ToDoSchema, description="Return the specific To-Do.")
    @blp.alt_response(403, description="Error if someone try to enter in forbidden section.")
    def get(self, user_id, todo_id):
        jwt_user_id = get_jwt_identity()
        if user_id != jwt_user_id:
            abort(403, message="You can't enter in this section.")

        todo = ToDoModel.query.get_or_404(todo_id)
        return todo

    @jwt_required()
    @blp.arguments(ToDoUpdateSchema)
    def patch(self, todo_receive_updated, **args):  # PATCH method, aggiorno il To-Do
        jwt_user_id = get_jwt_identity()
        if args.get("user_id") != jwt_user_id:
            abort(403, message="You can't enter in this section.")

        todo: ToDoModel = ToDoModel.query.get_or_404(args.get("todo_id"))  # ricerco
        # verifico e modifico
        if "todo_text" in todo_receive_updated:
            todo.todo_text = todo_receive_updated["todo_text"]
        if "fatto" in todo_receive_updated:
            todo.fatto = todo_receive_updated["fatto"]

        # Salvo modifiche
        db.session.add(todo)
        db.session.commit()
        return {"message": "ToDo Updated."}

    @jwt_required()
    @blp.response(200, description="To-Do deleted")
    @blp.alt_response(403, description="Forbidden function")
    @blp.alt_response(404, description="To-Do not found")
    def delete(self, user_id, todo_id):
        jwt_user_id = get_jwt_identity()
        if user_id != jwt_user_id:
            abort(403, message="You can't enter in this section.")

        todo: ToDoModel = ToDoModel.query.get_or_404(todo_id)  # ricerco
        # cancello
        db.session.delete(todo)
        db.session.commit()
        return {"message": "ToDo deleted."}
