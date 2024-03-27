from passlib.apps import custom_app_context as pwd_context

from app.extensions import db


roles_users = db.Table('roles_users',
            db.Column(
                'user_id', db.Integer(),
                db.ForeignKey('users.id', ondelete="CASCADE")
            ),
            db.Column(
                'role_id',
                db.Integer(),
                db.ForeignKey('roles.id', ondelete="CASCADE")
            ),
            db.UniqueConstraint('user_id', 'role_id', name='uq_user_role')
)

class AppRoleModel(db.Model):
    __tablename__ = 'apps'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)


class RoleModel(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    app_id = db.Column(db.Integer,
        db.ForeignKey('apps.id'), nullable=False,
        name='fk_roles_apps_app_id'
    )

    @classmethod
    def get_all_roles(cls):
        roles = cls.query.all()
        return roles

class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean, default=True)

    roles = db.relationship('RoleModel',
        secondary=roles_users,
        backref=db.backref('users', lazy='dynamic')
    )

    @staticmethod
    def hash_password(password):
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(password, hash_password):
        return pwd_context.verify(password, hash_password)

    @classmethod
    def get_user_by_id(cls, user_id):
        user = cls.query.filter_by(id=user_id).first()
        return user

    @classmethod
    def get_user_by_email(cls, email):
        user = cls.query.filter_by(email=email).first()
        return user

    @classmethod
    def get_all_users(cls):
        users = cls.query.all()
        return users

    @classmethod
    def create_user(cls, data):
        password_hash = cls.hash_password(data['password'])
        user = cls(
            email=data['email'],
            name=data['name'],
            password=password_hash,
        )
        if 'roles' in data:
            roles = RoleModel.query.filter(
                RoleModel.id.in_(data['roles'])
            ).all()
            user.roles.extend(roles)

        db.session.add(user)
        db.session.commit()
        return user

    @classmethod
    def update_user(cls, user_id, data):
        user = cls.get_user_by_id(user_id)
        if 'email' in data:
            user.email = data['email']
        if 'name' in data:
            user.name = data['name']

        db.session.commit()
        return user

    @classmethod
    def update_roles_user(cls, user_id, data):
        user = cls.get_user_by_id(user_id)
        if 'is_admin' in data:
            user.is_admin = data['is_admin']
        if 'roles' in data:
            roles = RoleModel.query.filter(
                RoleModel.id.in_(data['roles'])
            ).all()
            user.roles.clear()
            user.roles = roles

        db.session.commit()
        return user

    @classmethod
    def update_password(cls, user_id, new_password):
        user = cls.get_user_by_id(user_id)
        new_password_hash = cls.hash_password(new_password)
        user.password = new_password_hash
        db.session.commit()
        return user

    @classmethod
    def delete_user(cls, user):
        db.session.delete(user)
        db.session.commit()

    def __repr__(self):
        return '<User %r>' % self.email