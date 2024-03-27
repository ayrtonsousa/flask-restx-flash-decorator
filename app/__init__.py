from flask import Flask

from config import Config
from .extensions import db, migrate, ma, jwt, limiter, cache, cors


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    cache.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS'] }})
    
    from commands import init_app
    init_app(app)

    from app.api import api
    api.init_app(app)

    from app.api.errors import configure_error_handlers, configure_error_validation_handlers
    configure_error_validation_handlers(app)

    if not app.debug:
        configure_error_handlers(app)

    return app