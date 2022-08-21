from marshmallow import Schema, fields


class AuthRequestBody(Schema):
    login = fields.Str()
    password = fields.Str()