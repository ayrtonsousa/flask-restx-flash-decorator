from app.extensions import db 
from app.api.models.user import RoleModel, AppRoleModel
from app import create_app

from sqlalchemy import exc


app = create_app()

def load_initial_data():
    with app.app_context():
        # apps
        app1 = AppRoleModel(name='words')
        app2 = AppRoleModel(name='set_words')
        
        apps_role = [app1, app2]
        for app_role in apps_role:
            try:
                db.session.add(app_role)
                db.session.commit()
            except exc.IntegrityError as e:
                db.session.rollback()
                app_role = AppRoleModel.query.filter_by(name=app_role.name).first()

        # roles
        role1_app1 = RoleModel(name='create_word', app_id=app1.id)
        role2_app1 = RoleModel(name='delete_word', app_id=app1.id)
        role3_app1 = RoleModel(name='update_word', app_id=app1.id)

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