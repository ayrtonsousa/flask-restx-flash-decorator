from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request

from app.api.models.user import UserModel
from app.extensions import limiter


auth_ns = Namespace('auth', description='Auth related operations')

item = auth_ns.model('login', {
    'email': fields.String(description='email'),
    'password': fields.String(description='user password')
})

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.doc(security=None)
    @auth_ns.expect(item)
    @limiter.limit("50 per day")
    def post(self):
        data = auth_ns.payload
        email = data['email']
        password = data['password']
        user = UserModel.get_user_by_email(email)
        if user:
            if user.verify_password(password, user.password):
                access_token = create_access_token(
                    identity=user.id,
                    additional_claims={
                        "name": user.name.split(' ')[0],
                        "is_admin": user.is_admin,
                        "roles": [role.name for role in user.roles]
                    },
                )
                refresh_token = create_refresh_token(identity=user.id)
                return {'access_token': access_token, 'refresh_token': refresh_token}
        return {'message': 'Invalid credentials'}, 401


@auth_ns.route('/refresh')
class Refresh(Resource):
    @limiter.limit("100 per day")
    @jwt_required(refresh=True)
    def post(self):
        user_id = get_jwt_identity()
        user = UserModel.get_user_by_id(user_id)
        if user:
            access_token = create_access_token(
                identity=user.id,
                additional_claims={
                    "name": user.name.split(' ')[0],
                    "is_admin": user.is_admin,
                    "roles": [role.name for role in user.roles]
                },
            )
        return {'access_token': access_token}