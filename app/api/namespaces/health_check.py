from flask_restx import Namespace, Resource

from app.extensions import limiter


health_check_ns = Namespace('health', description='Health Check related operations')


@health_check_ns.route('/health_check', doc=False)
class HealthCheck(Resource):
    @health_check_ns.doc(security=None)
    @limiter.limit("30 per minute")
    def get(self):
        return 'ok', 200


        