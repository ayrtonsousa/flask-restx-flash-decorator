from app.extensions import db 
from app.api.models.user import RoleModel, AppRoleModel
from app import create_app

from sqlalchemy import exc


app = create_app()

def load_initial_data():
    with app.app_context():
        # create apps
        apps_to_create = [
            AppRoleModel(name='words'),
            AppRoleModel(name='set_words')
        ]
        for app_role in apps_to_create:
            try:
                db.session.add(app_role)
                db.session.commit()
            except exc.IntegrityError as e:
                db.session.rollback()

        # Roles

        # Words
        app1 = AppRoleModel.query.filter_by(name='words').first()

        role1_app1 = RoleModel(name='create_word', app_id=app1.id)
        role2_app1 = RoleModel(name='delete_word', app_id=app1.id)
        role3_app1 = RoleModel(name='update_word', app_id=app1.id)

        # Sets
        app2 = AppRoleModel.query.filter_by(name='set_words').first()

        role1_app2 = RoleModel(name='create_set_words', app_id=app2.id)
        role2_app2 = RoleModel(name='delete_set_words', app_id=app2.id)
        role3_app2 = RoleModel(name='update_set_words', app_id=app2.id)

        roles = [
            role1_app1, role2_app1, role3_app1,
            role1_app2, role2_app2, role3_app2
        ]

        for role in roles:
            try:
                db.session.add(role)
                db.session.commit()
            except exc.IntegrityError as e:
                db.session.rollback()


if __name__ == '__main__':
    load_initial_data()