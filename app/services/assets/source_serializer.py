from marshmallow import Schema, fields

class SourceSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    url = fields.Str()
    content_category = fields.Str()
    frequency = fields.Str()
    type = fields.Method("get_type_text")   # Custom method for enum text
    created_at = fields.Date()  # Custom format for the date
    updated_at = fields.Date(format="%Y-%m-%d")  # Custom format for the date

    def get_type_text(self, obj):
        return obj.type.value if obj.type else None

# Create an instance of the schema
user_schema = SourceSchema()