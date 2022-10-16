from db import db


class UserModel(db.Model):
    __tablename__ = "User_table"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(80), nullable=False)
    surname = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    todos = db.relationship("ToDoModel", back_populates="user", lazy="dynamic")
