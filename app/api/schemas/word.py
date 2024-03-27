from marshmallow import validates, ValidationError, pre_load, validates_schema, fields

from app.extensions import ma
from app.api.models.word import WordModel, TagModel, SetModel


class WordSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WordModel
        load_instance = True
        include_relationships = True

    def transform_to_lower(self, data, field_name):
        if field_name in data:
            data[field_name] = data[field_name].lower()
        return data

    @pre_load
    def transform_fields(self, data, **kwargs):
        self.transform_to_lower(data, "name")
        return data

    @validates("tags")
    def validate_tags(self, tags):
        if not tags:
            return tags

        tag_ids = [tag.id for tag in TagModel.query.all()]

        for tag in tags:
            if tag.id not in tag_ids:
                raise ValidationError(f"Tag ID {tag.id} does not exist")
        
        return tags


class TagSchema(ma.SQLAlchemyAutoSchema):
    name = fields.String(required=True)

    class Meta:
        model = TagModel
        load_instance = True

    @validates("name")
    def validate_name(self, name):
            if name == '':
                raise ValidationError(f"Field 'name' cannot be left blank", field_name="name")

            query = TagModel.query.filter(TagModel.name == name)
            if query.first():
                raise ValidationError('this tag already exists', field_name="name") 


class SetWordsSchema(ma.SQLAlchemyAutoSchema):

    @validates_schema
    def validate_object(self, data, **kwargs):

        if data.get('name'):
            name = data.get('name')

            if name == '':
                raise ValidationError(f"Field 'name' cannot be left blank", field_name="name")

            id_set = data.get('id')

            query = SetModel.query.filter(SetModel.name == name)
            if query and id_set:
                query = query.filter(SetModel.id != id_set)
            if query.first():
                raise ValidationError('this name already exists', field_name="name") 

        if data.get('words'):
            words = data.get('words')                

            word_ids = [word.id for word in WordModel.query.all()]

            for word in words:
                if word.id not in word_ids:
                    raise ValidationError(f"Word ID {word.id} does not exist", field_name="words")
        else:
           raise ValidationError(f"Field 'words' cannot be left blank", field_name="words")
 

    class Meta:
        model = SetModel
        load_instance = True
        include_relationships = True