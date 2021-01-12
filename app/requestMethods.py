from app import app
from bson.json_util import dumps
from flask import request, jsonify, Flask
import json, jwt, ast
from pymongo import MongoClient
from geopy import distance
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

conn_client = MongoClient(
    "mongodb+srv://DisJoin:1234@cluster0-bk4u2.mongodb.net/test?retryWrites=true&w=majority"
)
db = conn_client["DisJoin_data"]
store_list_collection = db["storeList"]
user_list_collection = db["userList"]


@app.route("/api/userLogin", methods=["POST"])
def user_login():
    data = request.get_json()
    try:
        user_list = get_all_users(call="local", find_query={"email": data["email"]})
        if len(user_list) > 0:
            for user in user_list:
                if check_password_hash(user["password"], data["password"]):
                    return {"msg": "Login Successful", "status": True}
                else:
                    return {"msg": "Incorrect Password", "status": False}

        return {"msg": "User does not exist.", "status": False}

    except Exception as e:
        return e, 500


# @app.route("/api/storeLogin", methods=["POST"])
# def store_login():
#     data = request.get_json()
#     try:
#         store_list = get_all_stores(call="local", find_query={"email": data["email"]})
#         if len(store_list) > 0:
#             for store in store_list:
#                 if check_password_hash(store["password"], data["password"]):
#                     return {"msg": "Login Successful", "status": True}
#                 else:
#                     return {"msg": "Incorrect Password", "status": False}

#         return {"msg": "User does not exist.", "status": False}

#     except Exception as e:
#         return e, 500


@app.route("/api/stores", methods=["GET"])
def get_all_stores(call="server", find_query={}):
    try:
        query = store_list_collection.find(find_query)
        store_list = [store for store in query]

        if call == "server":
            return dumps(store_list), 200
        elif call == "local":
            return store_list

    except Exception as e:
        return e, 500


@app.route("/api/stores", methods=["POST"])
def create_store_record():
    data = request.get_json()
    try:
        store_list = get_all_stores("local")
        # for store in store_list:
        #     if store["name"] == data["name"]:
        #         return "Store already exists.", 409

        data["sid"] = str(uuid.uuid4())
        data["password"] = generate_password_hash(data["password"])
        record_created = store_list_collection.insert(data)
        return "", 201
    except Exception as e:
        return e, 500


@app.route("/api/users", methods=["GET"])
def get_all_users(call="server", find_query={}):
    try:
        query = user_list_collection.find(find_query)
        user_list = [user for user in query]

        if call == "server":
            return dumps(user_list), 200
        elif call == "local":
            return user_list

    except Exception as e:
        return e, 500


@app.route("/api/users", methods=["POST"])
def create_user_record():
    data = request.get_json()
    try:
        user_list = get_all_users("local")
        for user in user_list:
            if user["email"] == data["email"]:
                return "User already exists.", 409

        data["id"] = str(uuid.uuid4())
        data["password"] = generate_password_hash(data["password"])
        record_created = user_list_collection.insert(data)
        return "", 201
    except Exception as e:
        return e, 500


@app.route("/api/users", methods=["DELETE"])
def delete_user():
    data = request.get_json()
    try:
        query = {"id": data["id"]}
        newvalues = {"$set": {"isActive": False}}

        # Soft Delete
        try:
            user_list_collection.update_one(query, newvalues)
        except Exception as x:
            return x, 500

        return {"msg": "User Deleted Succesfully.", "status_code": 200}

    except Exception as e:
        return e, 500


def within_range(store_list, center_point, radius):
    response_list = []
    try:
        for store in store_list:
            points = [store["Latitude"], store["Longitude"]]
            store_point_tuple = tuple(points)
            center_point_tuple = tuple(center_point)

            dis = distance.distance(center_point_tuple, store_point_tuple).miles

            if dis > 0 and dis <= radius:
                response_list.append(store)

        return response_list, 200
    except Exception as e:
        return e, 500


@app.route("/api/geofence_stores", methods=["GET"])
def get_stores_by_geofence():
    try:
        data = request.get_json()
        store_list = get_all_stores("local")

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
            "msg": "This route is currently not supported. Please refer API documentation or contact admin."
        }
    }
    page_not_found_response = jsonify(user_message)
    page_not_found_response.status_code = 404
    return page_not_found_response
