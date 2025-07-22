from marshmallow import Schema, fields

class UserSchema(Schema):
    id = fields.UUID()
    username = fields.Str()
    email = fields.Email()
    profile_data = fields.Dict()
    created_at = fields.DateTime()
