import click
from flask.cli import with_appcontext

from app.api.models.user import UserModel
from app.extensions import db
from app.api.schemas.user import UserSchema 


@click.command("create-user-admin")
@click.argument("name")
@click.argument("email")
@click.argument("password")
@with_appcontext
def create_user_admin(name, email, password):
    data = {
        "name": name,
        "password": password,
        "email": email
    }
    errors = UserSchema().validate(data)
    if errors:
        print(errors)
    else:
        user = UserModel.create_user(data)
        user.is_admin = True
        db.session.commit()
        click.echo("User admin created")

def init_app(app):
    app.cli.add_command(create_user_admin)