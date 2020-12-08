from app import app
from bson.json_util import dumps
from flask import request, jsonify
import json, jwt, ast
from pymongo import MongoClient
from geopy import distance
import uuid

conn_client = MongoClient(
    "mongodb+srv://DisJoin:1234@cluster0-bk4u2.mongodb.net/test?retryWrites=true&w=majority"
)
db = conn_client["DisJoin_data"]
store_list_collection = db["storeList"]
user_list_collection = db["userList"]


@app.route("/api/v1/stores", methods=["GET"])
def get_all_stores():
    try:
        query = store_list_collection.find()
        store_list = [store for store in query]

        return dumps(store_list), 200

    except Exception as e:
        return e, 500


@app.route("/api/v1/stores", methods=["POST"])
def create_store_record():
    store_list = get_all_stores()
    data = request.get_json()
    try:
        # data["sid"] = len(store_list) + 1  # needs improvisation
        data["sid"] = str(uuid.uuid4())
        record_created = store_list_collection.insert(data)
        return "", 201
    except Exception as e:
        return e, 500


@app.route("/api/v1/users", methods=["GET"])
def get_all_users():
    try:
        query = user_list_collection.find()
        user_list = [user for user in query]

        return dumps(user_list), 200

    except Exception as e:
        return e, 500


@app.route("/api/v1/users", methods=["POST"])
def create_user_record():
    data = request.get_json()
    try:
        data["uid"] = str(uuid.uuid4())
        record_created = user_list_collection.insert(data)
        return "", 201
    except Exception as e:
        return e, 500


def within_range(store_list, center_point, radius):
    response_list = []
    try:
        for store in store_list:
            points = store["coordinates"]
            store_point_tuple = tuple(points)
            center_point_tuple = tuple(center_point)

            dis = distance.distance(center_point_tuple, store_point_tuple).miles

            if dis <= radius:
                response_list.append(store)

        return response_list, 200
    except Exception as e:
        return e, 500


@app.route("/api/v1/geofence_stores", methods=["GET"])
def get_stores_by_geofence():
    try:
        data = request.get_json()

        store_collection = store_list_collection.find()
        store_list = [store for store in store_collection]

        center_point = data["center"]
        radius = data["radius"]

        response_list, status_code = within_range(store_list, center_point, radius)

        if status_code == 200:
            return dumps(response_list), 200
        return dumps(response_list), 500
    except Exception as ex:
        return ex, 500


@app.errorhandler(404)
def page_not_found(e):
    user_message = {
        "err": {
            "msg": "This route is currently not supported. Please refer API documentation."
        }
    }
    page_not_found_response = jsonify(user_message)
    page_not_found_response.status_code = 404
    return page_not_found_response
