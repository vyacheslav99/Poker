from marshmallow import Schema, fields


class AuthRequestBody(Schema):
    login = fields.String()
    password = fields.String()
