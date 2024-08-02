from flask import request
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, jwt_required
from flask_restful import Resource
from email_validator import EmailNotValidError,validate_email

from mysql_connection import get_connection
from utils import check_password, hash_password
from mysql.connector import Error



class UserRegisterResource(Resource):
    def post(self):
        data = request.get_json()
        if data.get('email') is None or data.get('email').strip() =='' or \
            data.get('name') is None or data.get('name').strip() =='' or \
            data.get('gender') is None or\
            data.get('password') is None or data.get('password').strip() =='' :
            return {"result": "fail"},400

        try:
            validate_email(data['email'])
        except EmailNotValidError as e:
            return{'result' : 'fail' , 'error' : str(e)},400
        

        if not 4 <= len(data['password']) <=12 :
            return {"result": "fail"},401
        passwrod = hash_password(data['password'])
        print(passwrod)

        try: 
            connection = get_connection()
            query = '''insert into users
                    (name, email, password, gender)
                    values
                    (%s,%s,%s,%s);'''
            record = (data['name'],data['email'],passwrod,data['gender'])
            cursor = connection.cursor()
            cursor.execute(query,record)
            connection.commit()
            user_id=cursor.lastrowid

            cursor.close()
            connection.close()
            
        except Error as e:
            if cursor is not None :
                cursor.close()
            if connection is not None :
                connection.close()
            return {'result': 'fail','error': str(e)}, 501
        access_token = create_access_token(user_id)
        return {"result": "success",'accessToken' : access_token}


class UserLoginResource(Resource) :
    def post(self) :
        
        data = request.get_json()

        if 'email' not in data or 'password' not in data:
            return {'result' : 'fail'}, 400
        if data['email'].strip() == '' or data['password'].strip() == '':  
            return {'result' : 'fail'}, 400
        try :
            connection = get_connection()
            query = '''select *
                        from users
                        where email = %s ;'''
            record = ( data['email'] ,  )
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)

            result_list = cursor.fetchall()

            print(result_list)

            cursor.close()
            connection.close()

        except Error as e:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()
            return {'result':'fail', 'error':str(e)},500

        if result_list == [] :
            return {'result' : 'fail'} , 401

        isCorrect = check_password(data['password'] , result_list[0]['password'])
        if isCorrect == False :
            return {'result' : 'fail'} , 401

        user_id = result_list[0]['id']
        access_token = create_access_token(user_id)

        return {'result' : 'success', 'accessToken':access_token}



# 로그아웃된 토큰을 저장할, set 을 만든다. 
jwt_blacklist = set()

class UserLogoutResource(Resource) :

    @jwt_required()
    def delete(self):

        jti = get_jwt()['jti']
        jwt_blacklist.add(jti)
        return {'result' : 'success'}