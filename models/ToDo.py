from db import db


class ToDoModel(db.Model):
    __tablename__ = "TodoList_table"
    id = db.Column(db.Integer, primary_key=True)
    todo_text = db.Column(db.String(80), unique=False, nullable=False)
    current_time = db.Column(db.String(80), unique=False, nullable=False)
    fatto = db.Column(db.Boolean, unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("User_table.id"), unique=False, nullable=False)

    user = db.relationship("UserModel")
