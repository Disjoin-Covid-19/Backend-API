from config import client
from app import app
from bson.json_util import dumps
from flask import request, jsonify
import json, jwt, ast
import pymongo

from geopy import distance

db = client["DisJoin_data"]
store_list_collection = db["storeList"]


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
        data["sid"] = len(store_list) + 1
        record_created = store_list_collection.insert(data)
        return "", 201
    except Exception as e:
        return e, 500


@app.route("/api/v1/geofence_stores", methods=["GET"])
def get_stores_by_geofence():
    try:
        data = request.get_json()
    except Exception as e:
        return e, 300
    try:
        query = store_list_collection.find()
        store_list = [store for store in query]

        response_list = []
        center = data["center"]
        radius = data["radius"]

        for store in store_list:
            points = store["coordinates"]
            test_tuple = tuple(points)
            center_tuple = tuple(center)

            dis = distance.distance(center_tuple, test_tuple).km

            if dis <= radius:
                response_list.append(store)

        return dumps(response_list), 200

    except Exception as e:
        return e, 500


@app.errorhandler(404)
def page_not_found(e):
    user_message = {
        "err": {
            "msg": "This route is currently not supported. Please refer API documentation."
        }
    }
    resp = jsonify(user_message)
    resp.status_code = 404
    return resp
