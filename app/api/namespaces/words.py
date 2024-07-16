from flask_restx import Resource, fields, Namespace
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity


from app.api.models.word import WordModel, TagModel, SetModel
from app.api.schemas.word import WordSchemaInput, WordSchemaOutPut, TagSchema, SetWordsSchema
from app.api.utils.wrappers_auth import role_or_admin_required
from app.extensions import limiter


words_ns = Namespace('words', description='Words related operations')
tags_ns = Namespace('tags', description='Tags related operations')
sets_words_ns = Namespace('set_words', description='Sets Words related operations')

word_input_schema = WordSchemaInput(exclude=('sets',))
word_output_schema = WordSchemaOutPut(exclude=('sets',))
word_list_schema = WordSchemaOutPut(many=True, exclude=('sets',))

tag_schema = TagSchema()
tag_list_schema = TagSchema(many=True)

set_words_schema = SetWordsSchema()
set_words_list_schema = SetWordsSchema(many=True)

ITEM_NOT_FOUND = 'Word not found'
TAG_NOT_FOUND = 'Tag not found'
SET_WORDS_NOT_FOUND = 'Set Words not found'

word_model = words_ns.model('word', {
    'name': fields.String(description='name word'),
    'translation': fields.String(description='translation word'),
    'annotation': fields.String(description='annotation word'),
    'tags': fields.List(fields.Integer, description='List of tags', default=[])
})

tag_model = words_ns.model('tag', {
    'name': fields.String(description='name tag')
})

set_words_model = words_ns.model('set_words', {
    'name': fields.String(description='name tag'),
    'words': fields.List(fields.Integer, description='List of words', default=[])
})


@words_ns.route('/<int:id_word>')
class Word(Resource):

    @jwt_required()
    @words_ns.doc('get_word')
    def get(self, id_word):
        '''Get word by id'''
        word_data = WordModel.get_word_by_id(id_word)
        if word_data:
            return word_input_schema.dump(word_data)
        return {'message': ITEM_NOT_FOUND}, 404

    @limiter.limit("500 per day")
    @words_ns.doc('update_word')
    @role_or_admin_required('update_word')
    @words_ns.expect(word_model)
    def put(self, id_word):
        '''Update word'''
        data_word = WordModel.get_word_by_id(id_word)
        if data_word:
            data = words_ns.payload
            errors = word_input_schema.validate(data)
            if errors:
                raise ValidationError(errors)
            word = WordModel.update_word(id_word, data)
            word_serialized = word_output_schema.dump(word)
            return word_serialized, 200
        return {'message': ITEM_NOT_FOUND}, 404

    @role_or_admin_required('delete_word')
    @words_ns.doc('delete_word')
    @words_ns.response(204, 'word deleted')
    def delete(self, id_word):
        '''Delete word'''
        word_data = WordModel.get_word_by_id(id_word)
        if word_data:
            WordModel.delete_word(word_data)
            return '', 204
        return {'message': ITEM_NOT_FOUND}, 404


@words_ns.route('/')
class WordList(Resource):

    @jwt_required()
    def get(self):
        '''List all words'''
        all_words = WordModel.get_all_words()
        return word_list_schema.dump(all_words), 200

    @limiter.limit("500 per day")
    @role_or_admin_required('create_word')
    @words_ns.doc('create_word')
    @words_ns.expect(word_model)
    @words_ns.response(201, 'word created')
    def post(self):
        '''Create a word'''
        data = words_ns.payload
        errors = word_input_schema.validate(data)
        if errors:
           raise ValidationError(errors)

        word_data = WordModel.create_word(data)
        word_serialized = word_output_schema.dump(word_data)
        return word_serialized, 201


@tags_ns.route('/<int:tag_id>')
class Tag(Resource):

    @jwt_required()
    @tags_ns.doc('get_tag')
    def get(self, tag_id):
        '''Get tag by id'''
        tag_data = TagModel.get_tag_by_id(tag_id)
        if tag_data:
            return tag_schema.dump(tag_data)
        return {'message': ITEM_NOT_FOUND}, 404


    @role_or_admin_required('delete_word')
    @tags_ns.doc('delete_tag')
    @tags_ns.response(204, 'tag deleted')
    def delete(self, tag_id):
        '''Delete tag'''
        tag_data = TagModel.get_tag_by_id(tag_id)
        if tag_data:
            TagModel.delete_tag(tag_data)
            return '', 204
        return {'message': ITEM_NOT_FOUND}, 404


@tags_ns.route('/')
class TagList(Resource):

    @jwt_required()
    @tags_ns.doc('list_tags')
    def get(self):
        '''List all tags'''
        all_tags = TagModel.get_all_tags()
        return tag_list_schema.dump(all_tags), 200

    @limiter.limit("100 per day")
    @role_or_admin_required('create_word')
    @tags_ns.doc('create_tag')
    @tags_ns.expect(tag_model)
    @tags_ns.response(201, 'tag created')
    def post(self):
        '''Create a tag'''
        data = tags_ns.payload
        errors = tag_schema.validate(data)
        if errors:
           raise ValidationError(errors)

        tag_data = TagModel.create_tag(data)
        tag_serialized = tag_schema.dump(tag_data)
        return tag_serialized, 201


@sets_words_ns.route('/<int:set_words_id>')
class SetWords(Resource):

    @jwt_required()
    @sets_words_ns.doc('get_set_words')
    def get(self, set_words_id):
        '''Get set words by id'''
        set_words_data = SetModel.get_set_by_id(set_words_id)
        if set_words_data:
            return set_words_schema.dump(set_words_data)
        return {'message': ITEM_NOT_FOUND}, 404

    @limiter.limit("50 per day")
    @sets_words_ns.doc('update_set_words')
    @role_or_admin_required('update_set_words')
    @sets_words_ns.expect(set_words_model)
    def put(self, set_words_id):
        '''Update word'''
        data_word = SetModel.get_set_by_id(set_words_id)
        if data_word:
            data = sets_words_ns.payload
            errors = set_words_schema.validate(data)
            if errors:
                raise ValidationError(errors)
            set_words = SetModel.update_set(set_words_id, data)
            set_words_serialized = set_words_schema.dump(set_words)
            return set_words_serialized, 200
        return {'message': ITEM_NOT_FOUND}, 404

    @role_or_admin_required('delete_set_words')
    @sets_words_ns.doc('delete_set_words')
    @sets_words_ns.response(204, 'word deleted')
    def delete(self, set_words_id):
        '''Delete set words'''
        set_words_data = SetModel.get_set_by_id(set_words_id)
        if set_words_data:
            SetModel.delete_set(set_words_data)
            return '', 204
        return {'message': ITEM_NOT_FOUND}, 404


@sets_words_ns.route('/')
class SetWordsList(Resource):

    @jwt_required()
    @words_ns.doc('list_sets_words')
    def get(self):
        '''List all set words'''
        all_set_words = SetModel.get_all_sets()
        return set_words_list_schema.dump(all_set_words), 200

    @limiter.limit("50 per day")
    @role_or_admin_required('create_set_words')
    @sets_words_ns.doc('create_set_words')
    @sets_words_ns.expect(set_words_model)
    @sets_words_ns.response(201, 'word created')
    def post(self):
        '''Create a set words'''
        data = sets_words_ns.payload

        errors = set_words_schema.validate(data)
        if errors:
           raise ValidationError(errors)

        set_data = SetModel.create_set(data)
        set_words_serialized = set_words_schema.dump(set_data)
        return set_words_serialized, 201


@sets_words_ns.route('/words/<int:set_id>')
class SetWordsListSearch(Resource):

    @jwt_required()
    @sets_words_ns.doc('get_words_by_set_id')
    def get(self, set_id):
        '''Search words by id set'''
        data = SetModel.get_words_by_set_id(set_id)
        if data:
            return word_output_schema.dump(data, many=True)
        return {'message': 'Words not found'}, 404