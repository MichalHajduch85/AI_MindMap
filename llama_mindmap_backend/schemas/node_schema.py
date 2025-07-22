from marshmallow import Schema, fields

class NodeSchema(Schema):
    id = fields.UUID()
    conversation_id = fields.UUID()
    parent_id = fields.UUID(allow_none=True)
    content = fields.Str()
    level = fields.Int()
    steps = fields.List(fields.Str(), allow_none=True)
    analysis = fields.Str(allow_none=True)
    created_at = fields.DateTime()
