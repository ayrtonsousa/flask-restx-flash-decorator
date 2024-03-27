from flask_restx import Resource, fields, Namespace
from marshmallow import ValidationError
from flask_jwt_extended import get_jwt_identity, jwt_required, verify_jwt_in_request, get_jwt


from app.api.models.user import UserModel, RoleModel
from app.api.schemas.user import UserSchema, UserUpdatePasswordSchema, RolesSchema, UserUpdateRolesSchema
from app.api.utils.wrappers_auth import role_or_admin_required, admin_required
from app.extensions import limiter


users_ns = Namespace('users', description='Users related operations')

user_schema = UserSchema()
user_put_schema = UserSchema(only=('email','name',))
user_output_schema = UserSchema(exclude=('password',))
user_list_schema = UserSchema(many=True, exclude=('password',))
user_update_password_schema = UserUpdatePasswordSchema()
roles_list_schema = RolesSchema(many=True, only=('id','name',))
user_roles_put_schema = UserUpdateRolesSchema(only=('is_admin','roles',))


ITEM_NOT_FOUND = 'User not found'

user_model = users_ns.model('user', {
    'email': fields.String(description='user email'),
    'name': fields.String(description='user name'),
    'password': fields.String(description='user password'),
})

user_update_model = users_ns.model('user_update', {
    'email': fields.String(description='user email'),
    'name': fields.String(description='user name'),
})

user_model_password = users_ns.model('user_password', {
    'old_password': fields.String(description='old password'),
    'new_password': fields.String(description='new password')
})

user_roles_model = users_ns.model('user_roles', {
    'is_admin': fields.Boolean(description='set admin user'),
    'roles': fields.List(fields.Integer, description='List of role', default=[])
})


@users_ns.route('/<int:id_user>')
class User(Resource):

    @jwt_required()
    @users_ns.doc('get_user')
    def get(self, id_user):
        '''Get data user'''
        id_user_request = get_jwt_identity()
        verify_jwt_in_request()
        claims = get_jwt()
        is_admin = claims.get('is_admin', False)
        if id_user_request == id_user or is_admin:
            user_data = UserModel.get_user_by_id(id_user)
            if user_data:
                return user_output_schema.dump(user_data)
            return {'message': ITEM_NOT_FOUND}, 404
        else:
            return {'message': 'user must be himself or admin!'}, 403

    @admin_required()
    @users_ns.doc('delete_user_only_by_admin_users')
    @users_ns.response(204, 'user deleted')
    def delete(self, id_user):
        '''Delete user'''
        user_admin_id = get_jwt_identity()
        if user_admin_id == id_user:
            return {'message': 'admin cannot delete himself'}, 400
        user_data = UserModel.get_user_by_id(id_user)
        if user_data:
            UserModel.delete_user(user_data)
            return '', 204
        return {'message': ITEM_NOT_FOUND}, 404


@users_ns.route('/')
class UserList(Resource):

    @admin_required()
    @users_ns.doc('list_users')
    def get(self):
        '''List all users'''
        all_users = UserModel.get_all_users()
        return user_list_schema.dump(all_users), 200

    @limiter.limit("20 per day")
    @users_ns.doc(security=None)
    @users_ns.doc('create_user')
    @users_ns.expect(user_model)
    @users_ns.response(201, 'user created')
    def post(self):
        '''Create a user'''
        data = users_ns.payload
        errors = user_schema.validate(data)
        if errors:
           raise ValidationError(errors)

        user_data = UserModel.create_user(data)
        user_serialized = user_output_schema.dump(user_data)
        return user_serialized, 201


@users_ns.route('/me')
class UserUpdateProfile(Resource):

    @limiter.limit("50 per day")
    @users_ns.doc('update_user')
    @jwt_required()
    @users_ns.expect(user_update_model)
    def put(self):
        '''Update user'''
        user_id = get_jwt_identity()
        data_user = UserModel.get_user_by_id(user_id)
        if data_user:
            data = users_ns.payload
            # passes id to context to validate user data
            user_put_schema.context = {'user_id': user_id}
            errors = user_put_schema.validate(data)
            if errors:
                raise ValidationError(errors)
            user = UserModel.update_user(user_id, data)
            user_serialized = user_output_schema.dump(user)
            return user_serialized, 200
        return {'message': ITEM_NOT_FOUND}, 404


@users_ns.route('/me/update_password')
@users_ns.response(400, 'password is incorrect')
class UpdatePasswordUser(Resource):

    @limiter.limit("10 per day")
    @jwt_required()
    @users_ns.doc('password_user')
    @users_ns.expect(user_model_password)
    def post(self):
        '''Update password user'''
        user_id = get_jwt_identity()
        data = users_ns.payload
        user = UserModel.get_user_by_id(user_id)
        if user:
            errors = user_update_password_schema.validate(data)
            if errors:
                raise ValidationError(errors)
            if user.verify_password(data['old_password'], user.password):
                UserModel.update_password(user_id, data['new_password'])
                return {"message": "password updated"}, 200
            else:
                return {'message': 'password is incorrect'}, 400
        return {'message': ITEM_NOT_FOUND}, 404


@users_ns.route('/roles')
class RoleList(Resource):

    @jwt_required()
    @users_ns.doc('list_roles')
    def get(self):
        '''List all roles'''
        all_roles = RoleModel.get_all_roles()
        return roles_list_schema.dump(all_roles), 200


@users_ns.route('/update_roles/<int:id_user>')
class UserUpdateRoles(Resource):

    @limiter.limit("50 per day")
    @users_ns.doc('update_user_roles')
    @admin_required()
    @users_ns.expect(user_roles_model)
    def put(self, id_user):
        ''' Update roles user '''
        data_user = UserModel.get_user_by_id(id_user)
        if data_user:
            data = users_ns.payload
            errors = user_roles_put_schema.validate(data)
            if errors:
                raise ValidationError(errors)
            user = UserModel.update_roles_user(id_user, data)
            user_serialized = user_output_schema.dump(user)
            return user_serialized, 200
        return {'message': ITEM_NOT_FOUND}, 404