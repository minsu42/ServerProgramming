import glob
import json
import os
import time
import urllib
from selenium.webdriver.support import expected_conditions as EC
from urllib.request import urlopen

import googlemaps
import mysql
import requests
import polyline
import folium
import webbrowser

from bs4 import BeautifulSoup
from pandas import options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

key = "AIzaSyCvaEPdcDFt-fvkFr8PJRhVnUtfGIfWAZU"
client = googlemaps.Client(key)

#**********************************************************************************************
def geocode(location): # 주소 변환
    results = client.geocode(location)
    return results

# results = geocode("숭실대학교")
# print("Geocode 결과: ", results)
# formatted_address = results[0]['formatted_address']
#
# # 경도 및 위도 추출
# location = results[0]['geometry']['location']
# latitude = location['lat']
# longitude = location['lng']

# # 출력
# print("주소:", formatted_address)
# print("경도:", longitude)
# print("위도:", latitude)
#**********************************************************************************************
def reverse_geocode(latitude, longitude):  # 주소 역변환(위도, 경도) -> 숭실대
    results = client.reverse_geocode((latitude, longitude))
    return results

# results = reverse_geocode(latitude, longitude)
# # print("Reverse Geocode 결과: ", results)
# # 경도 및 위도 추출
# location = results[0]['geometry']['location']
# latitude = location['lat']
# longitude = location['lng']
# # 출력
# print("주소:", formatted_address)
# print("경도:", longitude)
# print("위도:", latitude)
#**********************************************************************************************
def geolocate():  # 내 위치
    results = client.geolocate()
    return results

# results = geolocate()
#
# print("rst: ", results)
# print(results['location']['lat'], results['location']['lng'])
#**********************************************************************************************
def photo(photoUri, maxWidthPx = 2000, maxHeightPx = 1200): #사진 url 반환
    photo_url = f"https://places.googleapis.com/v1/{photoUri}/media?key={key}&maxWidthPx={maxWidthPx}&maxHeightPx={maxHeightPx}"
    return photo_url
#**********************************************************************************************
from googlemaps import Client

def place_details(place_id):
    # Google Maps 클라이언트 객체 생성
    client = Client("AIzaSyCvaEPdcDFt-fvkFr8PJRhVnUtfGIfWAZU")
    try:
        # Google Places API를 사용하여 장소의 세부 정보 가져오기
        results = client.place(
            place_id=place_id,
            language="ko",  # 언어를 한국어로 설정
            reviews_no_translations=False,
            reviews_sort="most_relevant",
        )
        return results
    except Exception as e:
        # 오류 발생 시 오류 메시지 출력
        print(f"Error fetching place details: {e}")
        return None

#**********************************************************************************************
def search_nearby(api_key, types, latitude, longitude, radius=500, max_results=10):
    # 요청 헤더
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": api_key,
        "X-Goog-FieldMask": "*"
    }

    # 요청 데이터
    data = {
        "includedTypes": types,
        "maxResultCount": max_results,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "radius": radius
            }
        },
    }

    # 요청 보내기
    response = requests.post("https://places.googleapis.com/v1/places:searchNearby", json=data, headers=headers)

    # 응답 확인
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": response.status_code, "message": response.text}

category=["american_restaurant", "bakery", "brazilian_restaurant", "chinese_restaurant", "fast_food_restaurant", "hamburger_restaurant", "italian_restaurant", "japanese_restaurant", "korean_restaurant", "pizza_restaurant", "ramen_restaurant", "sandwich_shop", "steak_house", "vietnamese_restaurant"]
#
# result = search_nearby(key, "ramen_restaurant", 37.4963538, 126.9572222)
# # 결과 출력
# if "places" in result:
#     places = result["places"]
#     for index, place in enumerate(places, start=1):
#         # print(f"음식점 {index}:")
#         for key, value in place.items():
#             if key in ["regularOpeningHours","id", "types", "formattedAddress", "location", "googleMapsUri", "primaryTypeDisplayName", "takeout", "dineIn", "servesLunch", "servesDinner", "allowsDogs", "restroom", "websiteUri", "weekdayDescriptions"]:
#                 if key == "id":
#                     rst = place_details(value)
#                     if rst==None:
#                         continue
#         #             print(rst["result"]['name'])
#         #             print(f"{key}: {value}")
#         #         else:
#         #             print(f"{key}: {value}")
#         # print("=" * 50)
# else:
#     print("주변 음식점을 찾을 수 없습니다.")
#**********************************************************************************************

def get_static_map(center, dest, filename, map_type='roadmap'):
    base_url = "https://maps.googleapis.com/maps/api/staticmap?"
    api_key = key
    size = "600x400"
    zoom = 16
    params = {
        "center": f"{center[0]},{center[1]}",
        "zoom": zoom,
        "size": size,
        "maptype": map_type,
        "markers": [
            f"color:red|label:C|{center[0]},{center[1]}",
            f"color:blue|label:O|{dest[0]},{dest[1]}"
        ],
        "key": api_key
    }

    url_params = urllib.parse.urlencode(params, doseq=True)
    full_url = base_url + url_params
    return full_url

# results = geolocate()
# print(results['location']['lat'], results['location']['lng'])
# ssu_lat = 37.4963538
# ssu_lng = 126.9572222
# # center = (results['location']['lat'], results['location']['lng'])
# center = (ssu_lat, ssu_lng)
# dest = (37.5129241, 126.9377834)
#
# # 지도 요청
# get_static_map(center, dest, "test")

import mysql.connector
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


def showNaverMapURL(restaurant_name):
    search_url = generate_naver_map_search_url(restaurant_name)
    print(search_url)



def generate_naver_map_search_url(restaurant_name):
    base_url = "https://map.naver.com/v5/search/"
    query = urllib.parse.quote(restaurant_name)
    search_url = f"{base_url}{query}"
    return search_url

def delete_png_files(directory):
    files = glob.glob(os.path.join(directory, '*.png'))
    for file in files:
        try:
            os.remove(file)
            print(f"Deleted: {file}")
        except Exception as e:
            print(f"Error deleting file {file}: {e}")



