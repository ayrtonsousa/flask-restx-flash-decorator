import logging

from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError


logging.basicConfig(level=logging.INFO)

def configure_error_validation_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        """ Get validation errors """
        error_messages = {}
        for field, messages in error.messages.items():
            for message in messages:
                error_messages.update({field: message})
        return {'message': 'Validation error', 'errors': error_messages}, 400
 
def configure_error_handlers(app):
    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(error):
        """ Get Database errors """
        logging.exception(str(error))
        return {'message': 'Database error'}, 500

    @app.errorhandler(Exception)
    def handle_server_error(error):
        """ Get Internal server errors """
        logging.exception(str(error))
        return {'message': 'Internal server error'}, 500