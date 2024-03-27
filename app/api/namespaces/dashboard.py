from flask_restx import Resource, fields, Namespace
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import request

from app.api.models.word import HistoricHitsModel
from app.api.schemas.historic import HistoricSchema
from app.extensions import limiter, cache


dashboard_ns = Namespace('dashboard', description='Dashboard related operations')

historic_schema = HistoricSchema(many=True)

historic_model = dashboard_ns.model('historic_model', {
    'id_word': fields.Integer,
    'hit': fields.Boolean,
})

historic_list_model = dashboard_ns.model('historic_list_model', {
    'historics': fields.List(fields.Nested(historic_model))
})


historic_hits_model = dashboard_ns.model('HistoricHitsModel', {
    'hits': fields.Integer,
    'errors': fields.Integer,
})

historic_hits_and_errors_by_day_model = dashboard_ns.model('HistoricHitsModel', {
    'hit_type': fields.String,
    'count': fields.Integer,
})

top10_wrong_words_user_model = dashboard_ns.model('HistoricHitsModel', {
    'word': fields.String,
    'count': fields.Integer,
})

historic_90days_by_user = dashboard_ns.model('HistoricHitsModel', {
    'date': fields.Date,
    'hits': fields.Integer,
    'errors': fields.Integer
})

def get_user_cache_key():
    user_id = get_jwt_identity()
    route_path = request.path
    return f'user_{user_id}_{route_path}'


@dashboard_ns.route('/create_historic')
class Historic(Resource):

    @limiter.limit("500 per day")
    @jwt_required()
    @dashboard_ns.doc('create_historic')
    @dashboard_ns.expect(historic_list_model)
    @dashboard_ns.response(201, 'historic created')
    def post(self):
        '''Create historics'''
        user_id = get_jwt_identity()

        data = dashboard_ns.payload

        errors = historic_schema.validate(data['historics'])

        if errors:
           raise ValidationError(errors)

        data = HistoricHitsModel.create_historics(data['historics'], user_id)
        data_serialized = historic_schema.dump(data)
        return data_serialized, 201


@dashboard_ns.route('/total_hits_last_30days')
class HistoricHitsUser(Resource):

    @jwt_required()
    @limiter.limit("24 per day")
    @cache.cached(timeout=3600, key_prefix=get_user_cache_key)
    @dashboard_ns.doc('get_historic_hits')
    @dashboard_ns.marshal_with(historic_hits_model)
    def get(self):
        '''Get hits from the user in the last 30 days'''
        user_id = get_jwt_identity()
        data = HistoricHitsModel.get_historic_hits_by_user(user_id)
        return data


@dashboard_ns.route('/historic_by_day/<string:date>')
class HistoricByDayUser(Resource):
    
    @jwt_required()
    @limiter.limit("24 per day")
    @cache.cached(timeout=3600, key_prefix=get_user_cache_key)
    @dashboard_ns.doc('get_historic_hits_and_errors_by_day')
    @dashboard_ns.marshal_with(historic_hits_and_errors_by_day_model)
    def get(self, date):
        '''Get hits and errors by day from user'''
        user_id = get_jwt_identity()
        data = HistoricHitsModel.\
            get_historic_by_day_by_user(user_id, date)
        return data


@dashboard_ns.route('/top10_wrong_words_by_user')
class Top10WrongWordsUser(Resource):

    @jwt_required()
    @cache.cached(timeout=3600, key_prefix=get_user_cache_key)
    @limiter.limit("24 per day")
    @dashboard_ns.marshal_with(top10_wrong_words_user_model)
    @dashboard_ns.doc('get_top10_wrong_words_by_user')
    def get(self):
        '''Get top 10 wrong words by user'''
        user_id = get_jwt_identity()
        data = HistoricHitsModel.\
            get_historic_by_user_top10_words_error(user_id)
        return data


@dashboard_ns.route('/historic_90days_by_user')
class Historic90daysUser(Resource):

    @jwt_required()
    @cache.cached(timeout=3600, key_prefix=get_user_cache_key)
    @limiter.limit("24 per day")
    @dashboard_ns.doc('get_historic_90days_by_user')
    @dashboard_ns.marshal_with(historic_90days_by_user)
    def get(self):
        '''Get results 90 days by user'''
        user_id = get_jwt_identity() 
        data = HistoricHitsModel.get_historic_90days_by_user(user_id)
        return data

