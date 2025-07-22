from marshmallow import Schema, fields

class LogSchema(Schema):
    id = fields.UUID()
    user_id = fields.UUID()
    event_type = fields.Str()
    event_data = fields.Dict()
    timestamp = fields.DateTime()
