from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restful import Resource

from mysql_connection import get_connection
from mysql.connector import Error
from decimal import Decimal

class LikeResource(Resource):
    @jwt_required()
    def post(self,media_id):
        user_id=get_jwt_identity()
        
        try:
            connection = get_connection()
            query = '''
                    insert into mediaLikes
                    (userId,mediaId)
                    values (%s,%s)'''
            record=(user_id,media_id)
            cursor = connection.cursor()
            cursor.execute(query,record)
            connection.commit()
            cursor.close()
            connection.close()
        except Error as e:
            if cursor is not None :
                cursor.close()
            if connection is not None :
                connection.close()
            return {'result' : 'fail', 'error' : str(e)}, 500
        return {'result' : 'success'}, 200
    


    @jwt_required()
    def delete(self,media_id):
        user_id=get_jwt_identity()
        try:
            connection = get_connection()

            query= '''delete from mediaLikes
                    where userId = %s AND mediaId = %s;'''
            
            record = (user_id,media_id)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
            cursor.close()
            connection.close()
            
        except Error as e :
            if cursor is not None :
                cursor.close()
            if connection is not None :
                connection.close()
            return {'result' : 'fail', 'error' : str(e)}, 500
        
        return {'result' : 'success'}, 200
    






class MyLikeListResource(Resource):
    @jwt_required()
    def get(self):
        offset = request.args.get('offset', default='0',)
        limit = request.args.get('limit', default='10',)
        user_id = get_jwt_identity()
        
        try:
            mediaType = request.args.get('mediaType', 'Null')
            title = request.args.get('title', 'Null')
            locationType = request.args.get('locationType', 'Null')
            location = request.args.get('location', 'Null')
            city = request.args.get('city', 'Null')
            address = request.args.get('address', 'Null')
            region = request.args.get('region', 'Null')
            keyword = request.args.get('query')
            connection = get_connection()
            if keyword:
                query = '''
                    SELECT m.id, mediaType, title, location, locationType, locationDes, operatingTime, imgUrl, 
                    SUBSTRING_INDEX(address, ' ', 1) AS city,
                    SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) AS region,
                    address, latitude, longitude, IF(l.id IS NULL, 0, 1) AS isLike
                    FROM media m
                    JOIN mediaLikes l 
                    ON m.id = l.mediaid AND l.userId = %s
                    WHERE (mediaType LIKE %s OR %s = 'Null')
                        OR (title LIKE %s OR %s = 'Null')
                        OR (location LIKE %s OR %s = 'Null')
                        OR (locationType LIKE %s OR %s = 'Null')
                        OR (address LIKE %s OR %s = 'Null')
                        OR (SUBSTRING_INDEX(address, ' ', 1) LIKE %s OR %s = 'Null')
                        OR (SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) LIKE %s OR %s = 'Null')
                    GROUP BY m.id
                    ORDER BY l.createdAt DESC
                    limit '''+offset+''','''+limit+''';'''
                record = (user_id,
                        f'%{keyword}%', keyword,
                            f'%{keyword}%', keyword,
                            f'%{keyword}%', keyword,
                            f'%{keyword}%', keyword,
                            f'%{keyword}%', keyword,
                            f'%{keyword}%', keyword,
                            f'%{keyword}%', keyword)
            else:
                query = '''
                    SELECT m.id, mediaType, title, location, locationType, locationDes, operatingTime, imgUrl, 
                    SUBSTRING_INDEX(address, ' ', 1) AS city,
                    SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) AS region,
                    address, latitude, longitude, IF(l.id IS NULL, 0, 1) AS isLike
                    FROM media m
                    JOIN mediaLikes l 
                    ON m.id = l.mediaid AND l.userId = %s
                    WHERE (mediaType LIKE %s OR %s = 'Null')
                        AND (title LIKE %s OR %s = 'Null')
                        AND (location LIKE %s OR %s = 'Null')
                        AND (locationType LIKE %s OR %s = 'Null')
                        AND (address LIKE %s OR %s = 'Null')
                        AND (SUBSTRING_INDEX(address, ' ', 1) LIKE %s OR %s = 'Null')
                        AND (SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) LIKE %s OR %s = 'Null')
                    GROUP BY m.id
                    ORDER BY l.createdAt DESC
                    limit '''+offset+''','''+limit+''';'''
                record = (user_id,
                        f'%{mediaType}%', mediaType,
                        f'%{title}%', title,
                        f'%{location}%', location,
                        f'%{locationType}%', locationType,
                        f'%{address}%', address,
                        f'%{city}%', city,
                        f'%{region}%', region)

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()
            for row in result_list:
                for key, value in row.items():
                    if isinstance(value, Decimal):
                        row[key] = float(value)

        except Error as e:
            return {"result": "fail", "error": str(e)}, 500

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        return {'result': 'success', 'items': result_list, 'count': len(result_list)}
    





class MyLikeListSearchResource(Resource):
    @jwt_required()
    def get(self):
        offset = request.args.get('offset', default='0',)
        limit = request.args.get('limit', default='10',)
        user_id = get_jwt_identity()
        
        try:
            mediaType = request.args.get('mediaType', 'Null')
            title = request.args.get('title', 'Null')
            locationType = request.args.get('locationType', 'Null')
            location = request.args.get('location', 'Null')
            city = request.args.get('city', 'Null')
            address = request.args.get('address', 'Null')
            region = request.args.get('region', 'Null')
            keyword = request.args.get('query')
            connection = get_connection()
            if keyword:
                query = '''
                    SELECT m.id, mediaType, title, location, locationType, locationDes, operatingTime, imgUrl, 
                    SUBSTRING_INDEX(address, ' ', 1) AS city,
                    SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) AS region,
                    address, latitude, longitude, IF(l.id IS NULL, 0, 1) AS isLike
                    FROM media m
                    JOIN mediaLikes l 
                    ON m.id = l.mediaid AND l.userId = %s
                    WHERE 
                    (locationType LIKE %s OR %s = 'Null')
                    AND (SUBSTRING_INDEX(address, ' ', 1) LIKE %s OR %s = 'Null')
                    AND (SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) LIKE %s OR %s = 'Null')
                    AND (
                        (mediaType LIKE %s OR %s = 'Null')
                        OR (title LIKE %s OR %s = 'Null')
                        OR (location LIKE %s OR %s = 'Null')
                        OR (address LIKE %s OR %s = 'Null')
                    )
                    GROUP BY m.id
                    ORDER BY l.createdAt DESC
                    limit '''+offset+''','''+limit+''';'''
                record = (user_id,
                        f'%{locationType}%', locationType,
                        f'%{city}%', city,
                        f'%{region}%', region,
                        f'%{keyword}%', keyword,
                        f'%{keyword}%', keyword,
                        f'%{keyword}%', keyword,
                        f'%{keyword}%', keyword,)
            else:
                query = '''
                    SELECT m.id, mediaType, title, location, locationType, locationDes, operatingTime, imgUrl, 
                    SUBSTRING_INDEX(address, ' ', 1) AS city,
                    SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) AS region,
                    address, latitude, longitude, IF(l.id IS NULL, 0, 1) AS isLike
                    FROM media m
                    JOIN mediaLikes l 
                    ON m.id = l.mediaid AND l.userId = %s
                    WHERE (mediaType LIKE %s OR %s = 'Null')
                        AND (title LIKE %s OR %s = 'Null')
                        AND (location LIKE %s OR %s = 'Null')
                        AND (locationType LIKE %s OR %s = 'Null')
                        AND (address LIKE %s OR %s = 'Null')
                        AND (SUBSTRING_INDEX(address, ' ', 1) LIKE %s OR %s = 'Null')
                        AND (SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) LIKE %s OR %s = 'Null')
                    GROUP BY m.id
                    ORDER BY l.createdAt DESC
                    limit '''+offset+''','''+limit+''';'''
                record = (user_id,
                        f'%{mediaType}%', mediaType,
                        f'%{title}%', title,
                        f'%{location}%', location,
                        f'%{locationType}%', locationType,
                        f'%{address}%', address,
                        f'%{city}%', city,
                        f'%{region}%', region)

            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, record)
            result_list = cursor.fetchall()
            for row in result_list:
                for key, value in row.items():
                    if isinstance(value, Decimal):
                        row[key] = float(value)

        except Error as e:
            return {"result": "fail", "error": str(e)}, 500

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

        return {'result': 'success', 'items': result_list, 'count': len(result_list)}