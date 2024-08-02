from flask import request
from flask_restful import Resource
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from mysql.connector import Error
from mysql_connection import get_connection
from decimal import Decimal
import re
from collections import Counter

class LocationListResource(Resource):
    def get(self):
        offset = int(request.args.get('offset', 0))
        limit = int(request.args.get('limit', 20))
        try:
            verify_jwt_in_request() 
            user_id = get_jwt_identity()
        except Exception as e:
            user_id = None

        connection = get_connection()
        try:
            mediaType = request.args.get('mediaType', 'Null')
            title = request.args.get('title', 'Null')
            locationType = request.args.get('locationType', 'Null')
            location = request.args.get('location', 'Null')
            city = request.args.get('city', 'Null')
            address = request.args.get('address', 'Null')
            region = request.args.get('region', 'Null')
            keyword = request.args.get('query')

            
            if keyword:
                query = '''
                    SELECT m.id, mediaType, title, location, locationType, locationDes, operatingTime,imgUrl, 
                        SUBSTRING_INDEX(address, ' ', 1) AS city,
                        SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) AS region,
                        address, latitude, longitude,IF(l.id IS NULL, 0, 1) AS isLike
                    FROM media m
                    left join mediaLikes l 
                    on m.id = l. mediaid and l.userId = %s
                    WHERE (mediaType LIKE %s OR %s = 'Null')
                    OR (title LIKE %s OR %s = 'Null')
                    OR (location LIKE %s OR %s = 'Null')
                    OR (locationType LIKE %s OR %s = 'Null')
                    OR (address LIKE %s OR %s = 'Null')
                    OR (SUBSTRING_INDEX(address, ' ', 1) LIKE %s OR %s = 'Null')
                    OR (SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) LIKE %s OR %s = 'Null')
                    ORDER BY Region ASC, location ASC
                    LIMIT %s, %s;
                '''
                record = (user_id,
                    f'%{keyword}%', keyword,
                    f'%{keyword}%', keyword,
                    f'%{keyword}%', keyword,
                    f'%{keyword}%', keyword,
                    f'%{keyword}%', keyword,
                    f'%{keyword}%', keyword,
                    f'%{keyword}%', keyword,
                    offset, limit
                )
            else:
                query = '''
                    SELECT m.id, mediaType, title, location, locationType, locationDes, operatingTime,imgUrl,
                        SUBSTRING_INDEX(address, ' ', 1) AS city,
                        SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) AS region,
                        address, latitude, longitude,IF(l.id IS NULL, 0, 1) AS isLike
                    FROM media m
                    left join mediaLikes l 
                    on m.id = l.mediaid and l.userId = %s
                    WHERE (mediaType LIKE %s OR %s = 'Null')
                    AND (title LIKE %s OR %s = 'Null')
                    AND (location LIKE %s OR %s = 'Null')
                    AND (locationType LIKE %s OR %s = 'Null')
                    AND (address LIKE %s OR %s = 'Null')
                    AND (SUBSTRING_INDEX(address, ' ', 1) LIKE %s OR %s = 'Null')
                    AND (SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) LIKE %s OR %s = 'Null')
                    ORDER BY Region ASC, location ASC
                    LIMIT %s, %s;
                '''
                record = (user_id,
                    f'%{mediaType}%', mediaType,
                    f'%{title}%', title,
                    f'%{location}%', location,
                    f'%{locationType}%', locationType,
                    f'%{address}%', address,
                    f'%{city}%', city,
                    f'{region}%', region,
                    offset, limit
                )

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


class LocationListSearchResource(Resource):
    def get(self):
        offset = int(request.args.get('offset', 0))
        limit = int(request.args.get('limit', 20))
        try:
            verify_jwt_in_request() 
            user_id = get_jwt_identity()
        except Exception as e:
            user_id = None

        connection = get_connection()
        try:
            mediaType = request.args.get('mediaType', 'Null')
            title = request.args.get('title', 'Null')
            locationType = request.args.get('locationType', 'Null')
            location = request.args.get('location', 'Null')
            city = request.args.get('city', 'Null')
            address = request.args.get('address', 'Null')
            region = request.args.get('region', 'Null')
            keyword = request.args.get('query','Null')
            
            
            query = '''
                SELECT m.id, mediaType, title, location, locationType, locationDes, operatingTime,imgUrl, 
                    SUBSTRING_INDEX(address, ' ', 1) AS city,
                    SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) AS region,
                    address, latitude, longitude,IF(l.id IS NULL, 0, 1) AS isLike
                FROM media m
                left join mediaLikes l 
                on m.id = l. mediaid and l.userId = %s
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
                ORDER BY Region ASC, location ASC
                LIMIT %s, %s;
            '''
            record = (user_id,
                f'%{locationType}%', locationType,
                f'%{city}%', city,
                f'{region}%', region,
                f'%{keyword}%', keyword,
                f'%{keyword}%', keyword,
                f'%{keyword}%', keyword,
                f'%{keyword}%', keyword,
                offset, limit
                )
            
               
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





class distanceListResource(Resource):
    def get(self):
        offset = int(request.args.get('offset', 0))
        limit = int(request.args.get('limit', 20))
        try:
            verify_jwt_in_request() 
            user_id = get_jwt_identity()
        except Exception as e:
            user_id = None

        connection = get_connection()
        try:
            mediaType = request.args.get('mediaType', 'Null')
            title = request.args.get('title', 'Null')
            locationType = request.args.get('locationType', 'Null')
            location = request.args.get('location', 'Null')
            city = request.args.get('city', 'Null')
            address = request.args.get('address', 'Null')
            region = request.args.get('region', 'Null')
            
            latitude = request.args.get('latitude')
            longitude = request.args.get('longitude')
            keyword = request.args.get('query')
            
            if keyword:
                query = '''
                    SELECT m.id, mediaType, title, location, locationType, locationDes, operatingTime,imgUrl, 
                        SUBSTRING_INDEX(address, ' ', 1) AS city,
                        SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) AS region,
                        address, latitude, longitude,IF(l.id IS NULL, 0, 1) AS isLike,(ABS(latitude - %s) + ABS(longitude - %s)) AS distance
                    FROM media m
                    left join mediaLikes l 
                    on m.id = l. mediaid and l.userId = %s
                    WHERE (mediaType LIKE %s OR %s = 'Null')
                    OR (title LIKE %s OR %s = 'Null')
                    OR (location LIKE %s OR %s = 'Null')
                    OR (locationType LIKE %s OR %s = 'Null')
                    OR (address LIKE %s OR %s = 'Null')
                    OR (SUBSTRING_INDEX(address, ' ', 1) LIKE %s OR %s = 'Null')
                    OR (SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) LIKE %s OR %s = 'Null')
                    ORDER BY distance ASC
                    LIMIT %s, %s;
                ''' 
                record = (latitude,longitude,
                          user_id,
                          f'%{keyword}%', keyword,
                          f'%{keyword}%', keyword,
                          f'%{keyword}%', keyword,
                          f'%{keyword}%', keyword,
                          f'%{keyword}%', keyword,
                          f'%{keyword}%', keyword,
                          f'%{keyword}%', keyword,
                    offset, limit
                )

            else:
                query = '''
                    SELECT m.id, mediaType, title, location, locationType, locationDes, operatingTime,imgUrl, 
                        SUBSTRING_INDEX(address, ' ', 1) AS city,
                        SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) AS region,
                        address, latitude, longitude,IF(l.id IS NULL, 0, 1) AS isLike,(ABS(latitude - %s) + ABS(longitude - %s)) AS distance
                    FROM media m
                    left join mediaLikes l 
                    on m.id = l. mediaid and l.userId = %s
                    WHERE (mediaType LIKE %s OR %s = 'Null')
                    AND (title LIKE %s OR %s = 'Null')
                    AND (location LIKE %s OR %s = 'Null')
                    AND (locationType LIKE %s OR %s = 'Null')
                    AND (address LIKE %s OR %s = 'Null')
                    AND (SUBSTRING_INDEX(address, ' ', 1) LIKE %s OR %s = 'Null')
                    AND (SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) LIKE %s OR %s = 'Null')
                    ORDER BY distance ASC
                    LIMIT %s, %s;
                ''' 
                record = (latitude,longitude,
                        user_id,
                        f'%{mediaType}%', mediaType,
                        f'%{title}%', title,
                        f'%{location}%', location,
                        f'%{locationType}%', locationType,
                        f'%{address}%', address,
                        f'%{city}%', city,
                        f'{region}%', region,
                        offset, limit
                        )

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
    


class distanceListResource2(Resource):
    def get(self):
        offset = int(request.args.get('offset', 0))
        limit = int(request.args.get('limit', 20))
        

        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
        except Exception as e:
            user_id = None
        connection = get_connection()
        try:
            locationType = request.args.get('locationType', 'Null')
            city = request.args.get('city', 'Null')
            region = request.args.get('region', 'Null')
            latitude = request.args.get('latitude')
            longitude = request.args.get('longitude')
            keyword = request.args.get('query','Null')

            keywords = re.split(r'[,\s+]', keyword)
            keywords = [part for part in keywords if part]
            print(keywords)
            keyword_list= []
            
            if len(keywords) >= 2:
                for keyword in keywords:
                    query = '''
                        SELECT m.id, mediaType, title, location, locationType, locationDes, operatingTime, imgUrl, 
                            SUBSTRING_INDEX(address, ' ', 1) AS city,
                            SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) AS region,
                            address, latitude, longitude, IF(l.id IS NULL, 0, 1) AS isLike, 
                            (ABS(latitude - %s) + ABS(longitude - %s)) AS distance
                        FROM media m
                        LEFT JOIN mediaLikes l 
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
                        ORDER BY distance ASC;
                    '''
                    record = (latitude, longitude, 
                            user_id,
                            f'%{locationType}%', locationType,
                            f'%{city}%', city,
                            f'{region}%', region,
                            f'%{keyword}%', keyword,
                            f'%{keyword}%', keyword,
                            f'%{keyword}%', keyword,
                            f'%{keyword}%', keyword
                    )
                    cursor = connection.cursor(dictionary=True)
                    cursor.execute(query, record)
                    result_list = cursor.fetchall()
                    keyword_list.extend(result_list)
                    
                    dict_strings = [str(d) for d in keyword_list]
        
                    # 문자열의 빈도 수를 계산합니다.
                    count = Counter(dict_strings)
                    
                    # 중복된 항목을 찾습니다.
                    duplicates = {s for s in count if count[s] > 1}
                    
                    # 중복된 문자열을 딕셔너리로 변환하여 리스트를 만듭니다.
                    result_lists = [eval(s) for s in duplicates]

            else:
                query = '''
                    SELECT m.id, mediaType, title, location, locationType, locationDes, operatingTime, imgUrl, 
                        SUBSTRING_INDEX(address, ' ', 1) AS city,
                        SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) AS region,
                        address, latitude, longitude, IF(l.id IS NULL, 0, 1) AS isLike, 
                        (ABS(latitude - %s) + ABS(longitude - %s)) AS distance
                    FROM media m
                    LEFT JOIN mediaLikes l 
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
                    ORDER BY distance ASC
                    LIMIT %s, %s;
                '''
                record = (latitude, longitude, user_id,
                          f'%{locationType}%', locationType,
                          f'%{city}%', city,
                          f'{region}%', region,
                          f'%{keyword}%', keyword,
                          f'%{keyword}%', keyword,
                          f'%{keyword}%', keyword,
                          f'%{keyword}%', keyword,
                          offset, limit
                )
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                result_lists = cursor.fetchall()

            for row in result_lists:
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

        return {'result': 'success', 'items': result_lists, 'count': len(result_lists)}




class HotLocationListResource(Resource):
    def get(self):
        offset = int(request.args.get('offset', 0))
        limit = int(request.args.get('limit', 20))
        try:
            verify_jwt_in_request() 
            user_id = get_jwt_identity()
        except Exception as e:
            user_id = None

        connection = get_connection()
        try:
            mediaType = request.args.get('mediaType', 'Null')
            title = request.args.get('title', 'Null')
            locationType = request.args.get('locationType', 'Null')
            location = request.args.get('location', 'Null')
            city = request.args.get('city', 'Null')
            address = request.args.get('address', 'Null')
            region = request.args.get('region', 'Null')
            keyword = request.args.get('query')
            if keyword:
                query = '''
                    SELECT m.id, mediaType, title, location, locationType, locationDes, operatingTime, imgUrl, 
                    SUBSTRING_INDEX(address, ' ', 1) AS city,
                    SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) AS region,
                    address, latitude, longitude,
                    COUNT(l.id) AS likeCount,
                    IF(MAX(l.userId = %s), 1, 0) AS isLike
                    FROM media m
                    LEFT JOIN mediaLikes l 
                    ON m.id = l.mediaid
                    WHERE (mediaType LIKE %s OR %s = 'Null')
                    OR (title LIKE %s OR %s = 'Null')
                    OR (location LIKE %s OR %s = 'Null')
                    OR (locationType LIKE %s OR %s = 'Null')
                    OR (address LIKE %s OR %s = 'Null')
                    OR (SUBSTRING_INDEX(address, ' ', 1) LIKE %s OR %s = 'Null')
                    OR (SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) LIKE %s OR %s = 'Null')
                
                    GROUP BY m.id
                    order by likeCount DESC
                        LIMIT %s, %s;
                    '''
                
                record = (user_id,
                          f'%{keyword}%', keyword,
                          f'%{keyword}%', keyword,
                          f'%{keyword}%', keyword,
                          f'%{keyword}%', keyword,
                          f'%{keyword}%', keyword,
                          f'%{keyword}%', keyword,
                          f'%{keyword}%', keyword,
                            offset, limit
                        )
            else:
                query = '''
                    SELECT m.id, mediaType, title, location, locationType, locationDes, operatingTime, imgUrl, 
                    SUBSTRING_INDEX(address, ' ', 1) AS city,
                    SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) AS region,
                    address, latitude, longitude,
                    COUNT(l.id) AS likeCount,
                    IF(MAX(l.userId = %s), 1, 0) AS isLike
                    FROM media m
                    LEFT JOIN mediaLikes l 
                    ON m.id = l.mediaid
                    WHERE (mediaType LIKE %s OR %s = 'Null')
                    AND (title LIKE %s OR %s = 'Null')
                    AND (location LIKE %s OR %s = 'Null')
                    AND (locationType LIKE %s OR %s = 'Null')
                    AND (address LIKE %s OR %s = 'Null')
                    AND (SUBSTRING_INDEX(address, ' ', 1) LIKE %s OR %s = 'Null')
                    AND (SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) LIKE %s OR %s = 'Null')
                
                    GROUP BY m.id
                    order by likeCount DESC
                        LIMIT %s, %s;
                    '''
                record = (user_id,
                          f'%{mediaType}%', mediaType,
                        f'%{title}%', title,
                        f'%{location}%', location,
                        f'%{locationType}%', locationType,
                        f'%{address}%', address,
                        f'%{city}%', city,
                        f'{region}%', region,
                            offset, limit
                        )
                
                
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

class HotLocationListResource2(Resource):
    def get(self):
        offset = int(request.args.get('offset', 0))
        limit = int(request.args.get('limit', 20))
        

        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
        except Exception as e:
            user_id = None
        connection = get_connection()
        try:
            locationType = request.args.get('locationType', 'Null')
            city = request.args.get('city', 'Null')
            region = request.args.get('region', 'Null')
            latitude = request.args.get('latitude')
            longitude = request.args.get('longitude')
            keyword = request.args.get('query','Null')

            keywords = re.split(r'[,\s+]', keyword)
            keywords = [part for part in keywords if part]
            print(keywords)
            keyword_list= []
            
            if len(keywords) >= 2:
                for keyword in keywords:
                    query = '''
                        SELECT m.id, mediaType, title, location, locationType, locationDes, operatingTime, imgUrl, 
                        SUBSTRING_INDEX(address, ' ', 1) AS city,
                        SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) AS region,
                        address, latitude, longitude,
                        COUNT(l.id) AS likeCount,
                        IF(MAX(l.userId = %s), 1, 0) AS isLike
                        FROM media m
                        LEFT JOIN mediaLikes l 
                        ON m.id = l.mediaid
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
                        ORDER BY likeCount DESC;
                    '''
                    record = ( 
                            user_id,
                            f'%{locationType}%', locationType,
                            f'%{city}%', city,
                            f'{region}%', region,
                            f'%{keyword}%', keyword,
                            f'%{keyword}%', keyword,
                            f'%{keyword}%', keyword,
                            f'%{keyword}%', keyword
                    )
                    cursor = connection.cursor(dictionary=True)
                    cursor.execute(query, record)
                    result_list = cursor.fetchall()
                    keyword_list.extend(result_list)
                    
                    dict_strings = [str(d) for d in keyword_list]
        
                    # 문자열의 빈도 수를 계산합니다.
                    count = Counter(dict_strings)
                    
                    # 중복된 항목을 찾습니다.
                    duplicates = {s for s in count if count[s] > 1}
                    
                    # 중복된 문자열을 딕셔너리로 변환하여 리스트를 만듭니다.
                    result_lists = [eval(s) for s in duplicates]

            else:
                query = '''
                    SELECT m.id, mediaType, title, location, locationType, locationDes, operatingTime, imgUrl, 
                    SUBSTRING_INDEX(address, ' ', 1) AS city,
                    SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) AS region,
                    address, latitude, longitude,
                    COUNT(l.id) AS likeCount,
                    IF(MAX(l.userId = %s), 1, 0) AS isLike
                    FROM media m
                    LEFT JOIN mediaLikes l 
                    ON m.id = l.mediaid
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
                    ORDER BY likeCount DESC
                    LIMIT %s, %s;
                '''
                record = (user_id,
                          f'%{locationType}%', locationType,
                          f'%{city}%', city,
                          f'{region}%', region,
                          f'%{keyword}%', keyword,
                          f'%{keyword}%', keyword,
                          f'%{keyword}%', keyword,
                          f'%{keyword}%', keyword,
                          offset, limit
                )
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                result_lists = cursor.fetchall()

            for row in result_lists:
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

        return {'result': 'success', 'items': result_lists, 'count': len(result_lists)}
    




class CityLocationListResource(Resource):
    def get(self):
        offset = int(request.args.get('offset', 0))
        limit = int(request.args.get('limit', 20))
        

        connection = get_connection()
        try:
            city = request.args.get('city')

            query = '''
                SELECT DISTINCT region, city
                    FROM (
                        SELECT 
                            SUBSTRING_INDEX(address, ' ', 1) AS city,
                            SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) AS region
                        FROM media
                        WHERE SUBSTRING_INDEX(address, ' ', 1) LIKE %s
                    ) AS subquery
                    LIMIT %s, %s;
                '''
            record = (f'%{city}%',
                offset, limit
            )
                
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
    


class LocationListSearchResource2(Resource):
    def get(self):
        offset = int(request.args.get('offset', 0))
        limit = int(request.args.get('limit', 20))
        try:
            verify_jwt_in_request() 
            user_id = get_jwt_identity()
        except Exception as e:
            user_id = None

        connection = get_connection()
        try:
            locationType = request.args.get('locationType', 'Null')    
            city = request.args.get('city', 'Null')
            region = request.args.get('region', 'Null')
            keyword = request.args.get('query','Null')
            print(keyword)   
            keywords = re.split(r'[,\s+]', keyword)
            keywords = [part for part in keywords if part]
            print(keywords)
            keyword_list=[]
            
            if len(keywords)>=2:
                for keyword in keywords:
                    query = '''
                        SELECT m.id, mediaType, title, location, locationType, locationDes, operatingTime,imgUrl, 
                            SUBSTRING_INDEX(address, ' ', 1) AS city,
                            SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) AS region,
                            address, latitude, longitude,IF(l.id IS NULL, 0, 1) AS isLike
                        FROM media m
                        left join mediaLikes l 
                        on m.id = l. mediaid and l.userId = %s
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
                        ORDER BY Region ASC, location ASC
                    '''
                    record = (user_id,
                        f'%{locationType}%', locationType,
                        f'%{city}%', city,
                        f'{region}%', region,
                        f'%{keyword}%', keyword,
                        f'%{keyword}%', keyword,
                        f'%{keyword}%', keyword,
                        f'%{keyword}%', keyword,
                        )
                    cursor = connection.cursor(dictionary=True)
                    cursor.execute(query, record)
                    result_list = cursor.fetchall()
                    keyword_list.extend(result_list)

                    dict_strings = [str(d) for d in keyword_list]
    
                    # 문자열의 빈도 수를 계산합니다.
                    count = Counter(dict_strings)
                    
                    # 중복된 항목을 찾습니다.
                    duplicates = {s for s in count if count[s] > 1}
                    
                    # 중복된 문자열을 딕셔너리로 변환하여 리스트를 만듭니다.
                    result_lists = [eval(s) for s in duplicates]
                    
                    

            else:
                query = '''
                SELECT m.id, mediaType, title, location, locationType, locationDes, operatingTime,imgUrl, 
                    SUBSTRING_INDEX(address, ' ', 1) AS city,
                    SUBSTRING_INDEX(SUBSTRING_INDEX(address, ' ', 2), ' ', -1) AS region,
                    address, latitude, longitude,IF(l.id IS NULL, 0, 1) AS isLike
                FROM media m
                left join mediaLikes l 
                on m.id = l. mediaid and l.userId = %s
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
                ORDER BY Region ASC, location ASC
                LIMIT %s, %s;
                '''
                record = (user_id,
                    f'%{locationType}%', locationType,
                    f'%{city}%', city,
                    f'{region}%', region,
                    f'%{keyword}%', keyword,
                    f'%{keyword}%', keyword,
                    f'%{keyword}%', keyword,
                    f'%{keyword}%', keyword,
                    offset, limit
                    )
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                result_lists = cursor.fetchall()

            for row in result_lists:
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

        return {'result': 'success', 'items': result_lists, 'count': len(result_lists)}