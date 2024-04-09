from flask_restx import Api

from .namespaces import users_ns, auth_ns, words_ns, tags_ns, sets_words_ns, dashboard_ns, health_check_ns


authorizations = {
    'jwt': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'Authorization',
        'description': "Insert your token jwt 'Bearer <your_token_jwt>'.",
    }
}

api = Api(
    version='1.0',
    title="API",
    description='API to learn english words',
    doc='/',
    prefix='/api',
    authorizations=authorizations, security='jwt'
)

api.add_namespace(auth_ns)
api.add_namespace(users_ns)
api.add_namespace(words_ns)
api.add_namespace(tags_ns)
api.add_namespace(sets_words_ns)
api.add_namespace(dashboard_ns)
api.add_namespace(health_check_ns)