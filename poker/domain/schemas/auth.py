from marshmallow import Schema, fields


class AuthRequestBody(Schema):
    login = fields.Str(required=True)
    password = fields.Str(required=True)


class UserUIDResponse(Schema):
    user_uid = fields.String()


class RegisterRequestBody(AuthRequestBody):
    name = fields.Str(required=True)
