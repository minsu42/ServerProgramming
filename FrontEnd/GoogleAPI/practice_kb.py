import re
import time
import random

import haversine
import mysql.connector

from . import GoogleAPI


class resultRestaurant():
    def __init__(self, answer_place, static_map=0, place_url=0, dis=0):
        self.answer_place = answer_place
        self.static_map = static_map
        self.place_url = place_url
        self.dis = dis


def connect_db():
    return mysql.connector.connect(
        host="place-mysql.cf60uusqyxge.ap-northeast-2.rds.amazonaws.com",
        user="root",
        passwd="rootroot",
        database="place_db"
    )

def extract_number_from_string(s):
    match = re.search(r'\((\d+)m\)', s)
    if match:
        return int(match.group(1))
    return None

def rst_from_question(username, excluded):
    # 모든 후보 카테고리
    answer_category=[]
    answer_store=[]
    category = ["barbecue_restaurant","american_restaurant", "bakery", "brazilian_restaurant",
                "chinese_restaurant", "fast_food_restaurant", "italian_restaurant", "japanese_restaurant",
                "korean_restaurant", "pizza_restaurant", "sandwich_shop", "vietnamese_restaurant"]
    connection = connect_db()
    cursor = connection.cursor(dictionary=True)

    query = """
            SELECT * FROM users_responses 
            WHERE username = %s
        """

    # 쿼리 실행
    cursor.execute(query, (username,))
    results = cursor.fetchall()

    if results:
        # 가장 마지막 객체 선택
        last_result = results[-1]

        # 각 속성별로 데이터 파싱
        id = last_result['id']
        username = last_result['username']
        question1_answer = last_result['question1_answer']
        question2_answer = last_result['question2_answer']

        print(f"ID: {id}, Username: {username}, Q1: {question1_answer}, Q2: {question2_answer}")
    else:
        print("No matching user found.")
        return

    # 커서와 연결 닫기
    cursor.close()
    connection.close()


    # question1(Morning, Launch, Dinner
    ans_question1 = question1_answer   # 아침, 점심, 저녁 중 하나
    if ans_question1 == "아침":
        answer_category.append("bakery")
        answer_category.append("fast_food_restaurant")
        answer_category.append("sandwich_shop")
        answer_category.append("korean_restaurant")
    elif ans_question1 == "점심":
        answer_category.append("chinese_restaurant")
        answer_category.append("fast_food_restaurant")
        answer_category.append("italian_restaurant")
        answer_category.append("korean_restaurant")
        answer_category.append("japanese_restaurant")
        answer_category.append("pizza_restaurant")
        answer_category.append("vietnamese_restaurant")
    elif ans_question1 == "저녁":
        answer_category.append("american_restaurant")
        answer_category.append("chinese_restaurant")
        answer_category.append("fast_food_restaurant")
        answer_category.append("italian_restaurant")
        answer_category.append("barbecue_restaurant")
        answer_category.append("japanese_restaurant")
        answer_category.append("pizza_restaurant")
        answer_category.append("brazilian_restaurant")



    for idx in answer_category:
        if excluded[idx] == 1:
            print("aaa", idx, excluded[idx])
            answer_category.remove(idx)
    print("After: ", answer_category)
    # question2 거리
    ans_question2 = extract_number_from_string(question2_answer) # () 안의 숫자만 추출
    myPosition = GoogleAPI.geolocate()  # 현재 위치 정보 출력
    my_lat = myPosition['location']['lat']
    my_lng = myPosition['location']['lng']
    my_gps = (my_lat, my_lng)
    # ssu_lat = 37.4963538
    # ssu_lng = 126.9572222
    # ssu_gps = (ssu_lat, ssu_lng)
    name_list=[]
    try:
        connection = connect_db()
        cursor = connection.cursor(dictionary=True)

        query = f"""
                SELECT * FROM Restaurants 
                WHERE types LIKE %s AND rating >= 4.0 AND openNow = 1 #별점 4.0이상, 현재 운영 선택
                """

        for category in answer_category:
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            print(category)
            cursor.execute(query, (f"%{category}%",))
            rows = cursor.fetchall()
            for row in rows:
                store_gps = (row["latitude"], row["longitude"])
                distance = haversine.haversine(my_gps, store_gps, unit='m')
                # distance = haversine.haversine(ssu_gps, store_gps, unit='m')
                if distance <= ans_question2:
                    answer_store.append(row)
                    name_list.append(row['name'])

        unique_answer_store = list({row['name']: row for row in answer_store}.values())

        # 결과가 0개인 경우 -1 반환
        if len(unique_answer_store) == 0:
            return -1

        # 결과가 1개 이상인 경우 출력하고 처리
        answer_store_n = unique_answer_store if len(unique_answer_store) <= 3 else random.sample(unique_answer_store, 3)
        answer_store_list = []

        for row in answer_store_n:
            results = GoogleAPI.geolocate()
            center = (results['location']['lat'], results['location']['lng'])  # 내 위치 기반
            # center = (ssu_lat, ssu_lng)   # SSU 기반
            dest = (row['latitude'], row['longitude'])
            static_map = GoogleAPI.get_static_map(center, dest, row["name"]) # 맵에 마커 찍은 후 PNG 저장&출력

            if "places/" in row["name"]:
                place_url = row["googleMapsUri"]
            else:
                place_url = GoogleAPI.generate_naver_map_search_url(row["name"])

            store_gps = (row["latitude"], row["longitude"])
            distance = int(haversine.haversine(my_gps, store_gps, unit='m'))
            # distance = int(haversine.haversine(ssu_gps, store_gps, unit='m'))

            place = resultRestaurant(row, static_map, place_url, distance)
            answer_store_list.append(place)

    except mysql.connector.Error as err:
        print("Error: ", err)
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    return answer_store_list

def removePNG():
    GoogleAPI.delete_png_files('./')
    GoogleAPI.delete_png_files('places')



if __name__ == "__main__":
    a = rst_from_question("aa")
    print("*********************************************")
    #removePNG()
    print(a)
