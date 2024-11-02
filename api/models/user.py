from pydantic import BaseModel


class SignupSchema(Schema):
    login = fields.String(required=True)
    password = fields.String(required=True)
    secret = fields.String(required=True)


class UserSchema(Schema):
    uid = fields.UUID()
    login = fields.String()
    name = fields.String()
    avatar = fields.String(allow_none=True)
    session_id = fields.String(allow_none=True)


class SessionSchema(Schema):
    session_id: fields.String()