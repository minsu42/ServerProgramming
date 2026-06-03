import googlemaps
import pymysql.cursors
import json
from FrontEnd.GoogleAPI.GoogleAPI import *


def update_restaurant_data():
    print("====================================================================")
    print("====================================================================")
    print("====================================================================")

    key = "AIzaSyCvaEPdcDFt-fvkFr8PJRhVnUtfGIfWAZU"
    client = googlemaps.Client(key)

    category = ["barbecue_restaurant", "american_restaurant", "bakery", "brazilian_restaurant", "chinese_restaurant",
                "fast_food_restaurant", "italian_restaurant", "japanese_restaurant", "korean_restaurant",
                "pizza_restaurant", "sandwich_shop", "vietnamese_restaurant"]

    key_list = {"name", "types", "regularOpeningHours", "id", "formattedAddress", "location", "googleMapsUri", "photos",
                "takeout", "dineIn", "servesLunch", "servesDinner", "allowsDogs", "restroom", "rating"}

    conn_restaurant = pymysql.connect(host="place-mysql.cf60uusqyxge.ap-northeast-2.rds.amazonaws.com",
                                      user="root",
                                      passwd="rootroot",
                                      database='place_db',
                                      cursorclass=pymysql.cursors.DictCursor)

    def create_restaurant_table():
        cursor = conn_restaurant.cursor()
        sql_query = """
        CREATE TABLE IF NOT EXISTS Restaurants (
            name VARCHAR(255),
            id VARCHAR(255) PRIMARY KEY,
            types TEXT,
            rating DOUBLE,
            formattedAddress VARCHAR(255),
            latitude DOUBLE,
            longitude DOUBLE,
            googleMapsUri VARCHAR(255),
            photoUri VARCHAR(255),
            openNow BOOLEAN,
            weekdayDescriptions TEXT,
            dineIn BOOLEAN,
            servesLunch BOOLEAN,
            servesDinner BOOLEAN,
            allowsDogs BOOLEAN,
            restroom BOOLEAN,
            createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """
        cursor.execute(sql_query)
        conn_restaurant.commit()
        cursor.close()

    def insert_restaurant(data):
        try:
            cursor = conn_restaurant.cursor()
            sql_query = """
            INSERT INTO Restaurants (name, id, types, rating, formattedAddress, latitude, longitude, googleMapsUri, photoUri,
                                    openNow, weekdayDescriptions, dineIn, servesLunch, servesDinner, allowsDogs, restroom, createdAt, updatedAt)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            ON DUPLICATE KEY UPDATE
            name = VALUES(name), types = VALUES(types), rating = VALUES(rating), formattedAddress = VALUES(formattedAddress), 
            latitude = VALUES(latitude), longitude = VALUES(longitude), googleMapsUri = VALUES(googleMapsUri), photoUri = VALUES(photoUri),
            openNow = VALUES(openNow), weekdayDescriptions = VALUES(weekdayDescriptions), dineIn = VALUES(dineIn), 
            servesLunch = VALUES(servesLunch), servesDinner = VALUES(servesDinner), allowsDogs = VALUES(allowsDogs), restroom = VALUES(restroom),
            updatedAt = CURRENT_TIMESTAMP
            """

            regular_opening_hours = data.get('regularOpeningHours', {})
            open_now = regular_opening_hours.get('openNow', False)
            weekday_descriptions = json.dumps(regular_opening_hours.get('weekdayDescriptions', []))

            record = (
                data.get('name', 'Unknown'),
                data['id'],
                json.dumps(data.get('types', [])),
                data.get('rating', None),
                data.get('formattedAddress', ''),
                data['location']['latitude'],
                data['location']['longitude'],
                data.get('googleMapsUri', ''),
                data.get('photos', ''),
                open_now,
                weekday_descriptions,
                data.get('dineIn', False),
                data.get('servesLunch', False),
                data.get('servesDinner', False),
                data.get('allowsDogs', False),
                data.get('restroom', False),
            )

            print(f"Inserting restaurant: {record}")  # 디버그: 삽입할 데이터 출력
            cursor.execute(sql_query, record)
            conn_restaurant.commit()
            print("Insert successful")  # 디버그: 삽입 성공 메시지

        except pymysql.MySQLError as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            cursor.close()

    def manage_database_size():
        cursor = conn_restaurant.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM Restaurants")
        total = cursor.fetchone()['total']

        if total > 10000:
            cursor.execute("""
                DELETE FROM Restaurants
                WHERE id IN (
                    SELECT id
                    FROM (SELECT id FROM Restaurants ORDER BY updatedAt LIMIT %s) AS subquery
                )
            """, (total - 10000,))
            conn_restaurant.commit()
        cursor.close()

        cursor = conn_restaurant.cursor()
        cursor.execute("SELECT COUNT(*) AS total FROM users_responses")
        total = cursor.fetchone()['total']

        if total > 10000:
            # 절반 삭제
            delete_count = total // 2
            cursor.execute("""
                    DELETE FROM users_responses
                    WHERE id IN (
                        SELECT id
                        FROM (SELECT id FROM users_responses ORDER BY id LIMIT %s) AS subquery
                    )
                """, (delete_count,))
            conn_restaurant.commit()

            # ID 재정렬
            cursor.execute("SET @new_id := 0")
            cursor.execute("""
                    UPDATE users_responses SET id = (@new_id := @new_id + 1) ORDER BY id
                """)
            conn_restaurant.commit()

            # AUTO_INCREMENT 값 재설정
            cursor.execute("ALTER TABLE users_responses AUTO_INCREMENT = 1")
            conn_restaurant.commit()

        cursor.close()

    # clear_table("Restaurants")
    create_restaurant_table()
    myPosition = geolocate()
    my_lat = myPosition['location']['lat']
    my_lng = myPosition['location']['lng']
    ssu_lat = 37.4963538
    ssu_lng = 126.9572222

    for restaurant_type in category:
        print(restaurant_type)
        result = search_nearby(key, restaurant_type, latitude=my_lat, longitude=my_lng)
        # result = search_nearby(key, restaurant_type, latitude=ssu_lat, longitude=ssu_lng)

        if "places" in result:
            places = result["places"]
            for place in places:
                place_data = {key: value for key, value in place.items() if key in key_list}
                if 'photos' in place_data:
                    place_data["photos"] = place_data["photos"][0]['name']
                if 'id' in place_data:
                    rst = place_details(place_data["id"])
                    if rst:
                        place_data["name"] = rst["result"]['name']
                        print(place_data["types"])
                    insert_restaurant(place_data)
        else:
            print("No restaurants found")

    manage_database_size()


if __name__ == '__main__':
    update_restaurant_data()
