from app import app
from bson.json_util import dumps
from flask import request, jsonify, Flask
from config import db
import json, jwt, ast
from geopy import distance
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
from datetime import datetime as dt

store_list_collection = db["storeList"]
user_list_collection = db["userList"]


def get_new_token(data, req="user"):
    if data:
        if req == "user":
            token = jwt.encode(
                {
                    "user": data["id"],
                    "pass": dt.timestamp(dt.utcnow()),
                },
                app.config["SECRET_KEY"],
            )
        elif req == "store":
            token = jwt.encode(
                {
                    "user": data["sid"],
                    "pass": dt.timestamp(dt.utcnow),
                },
                app.config["SECRET_KEY"],
            )
        return True, token
    return False, ""


def validate_token():
    token = str(request.headers["Authorization"]).split()[1]
    if not token:
        return False, 403

    try:
        data = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])
        # Check whether token is expired
        if (dt.timestamp(dt.utcnow()) - data["pass"]) // (
            int(app.config["TOKEN_VALID_FOR"]) * 60
        ) > 0:
            return False, 403
        return True, 200
    except Exception as e:
        if e:
            # return False, 500
            return False, e
        return False, 403


@app.route("/api/userLogin", methods=["POST"])
def user_login():
    data = request.get_json()
    if data:
        try:
            user_list = get_all_users(call="login", find_query={"email": data["email"]})
            if user_list:
                for user in user_list:
                    if (
                        check_password_hash(user["password"], data["password"])
                        and user["email"] == data["email"]
                    ):
                        status, token = get_new_token(user)
                        if status:
                            return jsonify(
                                {
                                    "msg": "Login Successful",
                                    "status": True,
                                    "token": str(token)[2:-1],
                                }
                            )
                    else:
                        return {"msg": "Incorrect Password", "status": False}

            return {"msg": "User does not exist.", "status": False}

        except Exception as e:
            return str(e), 500
        return jsonify({"message": "User unauthorized."}), 401
    return jsonify({"message": "Invalid Credentials."}), 401


@app.route("/api/storeLogin", methods=["POST"])
def store_login():
    data = request.get_json()
    try:
        store_list = get_all_stores(
            call="login", find_query={"username": data["username"]}
        )
        if len(store_list) > 0:
            for store in store_list:
                if check_password_hash(store["password"], data["password"]):
                    return {"msg": "Login Successful", "status": True}
                else:
                    return {"msg": "Incorrect Password", "status": False}

        return {"msg": "User does not exist.", "status": False}

    except Exception as e:
        return str(e), 500


@app.route("/api/stores", methods=["GET"])
def get_all_stores(call="server", find_query={}):
    try:
        if (
            call == "login" or call == "local"
        ):  # add geofence if we want to open maps after login (token auth)
            query = store_list_collection.find(find_query)
            store_list = [store for store in query]

            return store_list
        elif call == "server":
            status, code = validate_token()
            if status:
                query = store_list_collection.find(find_query)
                store_list = [store for store in query]

                return dumps(store_list), 200
            else:
                return jsonify({"status": status, "code": code})

    except Exception as e:
        return jsonify({"status": False, "code": 500})


@app.route("/api/stores", methods=["POST"])
def create_store_record():
    data = request.get_json()
    try:
        store_list = get_all_stores("local")
        for store in store_list:
            if store["username"] == data["sName"] + "_" + data["city"]:
                return "Store already exists.", 409

        data["sid"] = str(uuid.uuid4())
        data["username"] = data["sName"] + "_" + data["city"]
        data["password"] = generate_password_hash(data["password"])
        data["timestampUTC"] = dt.timestamp(dt.utcnow())
        record_created = store_list_collection.insert(data)
        return jsonify({"status": True}), 201
    except Exception as e:
        return jsonify({"status": False}), 500


@app.route("/api/users", methods=["GET"])
def get_all_users(call="server", find_query={}):
    try:
        if call == "login" or call == "local":  # new record or login
            query = user_list_collection.find(find_query)
            user_list = [user for user in query]

            return user_list
        elif call == "server":
            status, code = validate_token()
            if status:
                query = user_list_collection.find(find_query)
                user_list = [user for user in query]

                return dumps(user_list), 200
            else:
                return jsonify({"status": status, "code": code})

    except Exception as e:
        return jsonify({"status": False, "code": 500})


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
        data["addedDate"] = dt.timestamp(dt.utcnow())
        record_created = user_list_collection.insert(data)

        return jsonify({"status": True}), 201
    except Exception as e:
        return jsonify({"status": False}), 500


@app.route("/api/users", methods=["DELETE"])
def delete_user():
    data = request.get_json()
    try:
        status, code = validate_token()
        if status:
            query = {"id": data["id"]}

            # Soft Delete
            newvalues = {"$set": {"isActive": False}}

            try:
                user_list_collection.update_one(query, newvalues)
            except Exception as x:
                return jsonify({"status": False}), 500

            return {"msg": "User Deleted Succesfully.", "status_code": 200}
        else:
            return jsonify({"status": status, "code": code})

    except Exception as e:
        return jsonify({"status": False}), 500


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
        return jsonify({"err": e}), 500


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
        return dumps(response_list), 501
    except Exception as ex:
        return jsonify({"err": ex}), 500


@app.errorhandler(404)
def page_not_found(e):
    user_message = {
        "msg": "This route is currently not supported. Please refer API documentation or contact admin."
    }
    page_not_found_response = jsonify(user_message)
    page_not_found_response.status_code = 404
    return page_not_found_response
