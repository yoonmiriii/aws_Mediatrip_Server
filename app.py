from flask import Flask, jsonify, make_response
import serverless_wsgi
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_restful import Api
from config import Config
from resources.user import jwt_blacklist


from resources.user import UserLoginResource, UserLogoutResource, UserRegisterResource
from resources.filter import LocationListResource,distanceListResource,HotLocationListResource,CityLocationListResource,LocationListSearchResource,LocationListSearchResource2,distanceListResource2,HotLocationListResource2
from resources.likes import LikeResource,MyLikeListResource,MyLikeListSearchResource
app = Flask(__name__)
app = Flask(__name__)


# 환경변수 셋팅
app.config.from_object(Config)
jwt = JWTManager(app)

@jwt.token_in_blocklist_loader
def check_if_token_is_revoked(jwt_header, jwt_payload):
    jti = jwt_payload['jti']
    return jti in jwt_blacklist

api = Api(app)
# 경로와 리소스를 연결하는 코드 작성.
api.add_resource(UserRegisterResource, '/user/register')
api.add_resource(UserLoginResource, '/user/login')
api.add_resource(UserLogoutResource, '/user/logout')

api.add_resource(LocationListResource,'/filter')
api.add_resource(distanceListResource,'/location/distance')
api.add_resource(distanceListResource2,'/location/distance2')
api.add_resource(HotLocationListResource,'/location/hot')
api.add_resource(HotLocationListResource2,'/location/hot2')
api.add_resource(CityLocationListResource,'/filter/location')
api.add_resource(LocationListSearchResource,'/filter/search')
api.add_resource(LocationListSearchResource2,'/filter/search2')


api.add_resource(LikeResource,'/like/<int:media_id>')
api.add_resource(MyLikeListResource,'/mylike')
api.add_resource(MyLikeListSearchResource,'/mylike/search')

def handler(event,context):
    return serverless_wsgi.handle_request(app,event,context)

if __name__ == '__main__' :
    app.run
