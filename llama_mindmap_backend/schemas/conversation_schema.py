from marshmallow import Schema, fields

class ConversationSchema(Schema):
    id = fields.UUID()
    user_id = fields.UUID()
    root_topic = fields.Str()
    created_at = fields.DateTime()
