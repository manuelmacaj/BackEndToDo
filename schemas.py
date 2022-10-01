from marshmallow import Schema, fields


class LoginUserSchema(Schema):
    email = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class PlainToDoSchema(Schema):
    id = fields.Int(dump_only=True)
    todo_text = fields.Str(required=True)
    current_time = fields.Str(required=True)
    fatto = fields.Bool(required=True)


class PlainUserRegisterSchema(LoginUserSchema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    surname = fields.Str(required=True)
    todos = fields.List(fields.Nested(PlainToDoSchema(), load_only=True))


class ToDoSchema(PlainToDoSchema):
    user_id = fields.Nested(PlainUserRegisterSchema(), load_only=True)


class ToDoUpdateSchema(Schema):
    todo_text = fields.Str()
    fatto = fields.Bool()
