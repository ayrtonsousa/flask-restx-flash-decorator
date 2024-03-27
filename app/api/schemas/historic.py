from marshmallow import validates, ValidationError, Schema, fields

from app.api.models.word import HistoricHitsModel, WordModel


class HistoricSchema(Schema):

    id_word = fields.Integer(required=True)
    hit = fields.Boolean(required=True)

    @validates("id_word")
    def validate_words(self, value):
        result = WordModel.query.filter(WordModel.id==value).first()

        if result is None:
            raise ValidationError(f"Word ID {value} does not exist")
        return value