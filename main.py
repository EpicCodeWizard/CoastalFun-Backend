from cors import crossdomain
from deso import Media
from replit import db
from flask import *
import json
import uuid
import os

app = Flask(__name__, template_folder="", static_folder="")
desoMedia = Media(publicKey=os.environ["publicKey"], seedHex=os.environ["seedHex"])

def from_db(name):
  return json.loads(db.get_raw(name))

def upload_to_deso(file):
  return desoMedia.uploadImage([("file", (file.name, file.stream, file.mimetype))]).json()["ImageURL"]

def create_user_if_not_exist(uid):
  if uid not in db["users"].keys():
    tempdata = {}
    tempdata["uid"] = uid
    tempdata["badges"] = []
    tempdata["events"] = []
    tempdata["trash"] = 0
    db["users"][uid] = tempdata
    tempuuid = str(uuid.uuid4())
    db["collections"][tempuuid] = {"name": "Default", "uid": uid, "cid": tempuuid, "urls": [], "default": True}

@crossdomain(origin="*")
@app.route("/image/save", methods=["POST"])
def save_image():
  create_user_if_not_exist(request.json["uid"])
  if len(request.form["cid"]) != 0:
    db["collections"][request.form["cid"]]["urls"].append(upload_to_deso(request.files["image"]))
  else:
    for collection in from_db("collections").values():
      if collection["uid"] == request.form["uid"] and collection["default"] == True:
        db["collections"][collection["cid"]]["urls"].append(upload_to_deso(request.files["image"]))
  return ""

@crossdomain(origin="*")
@app.route("/collections/get/user/<uid>", methods=["GET"])
def user_collections(uid):
  tempcollections = []
  for collection in from_db("collections").values():
    if collection["uid"] == uid:
      tempcollections.append(collection)
  return jsonify(tempcollections)

@crossdomain(origin="*")
@app.route("/collections/get/<cid>", methods=["GET"])
def get_collection(cid):
  return jsonify(from_db("collections")[cid])

@crossdomain(origin="*")
@app.route("/collections/all", methods=["GET"])
def all_collections():
  return jsonify(list(from_db("collections").values()))

@crossdomain(origin="*")
@app.route("/collections/create", methods=["POST"])
def create_collection():
  tempuuid = str(uuid.uuid4())
  data = request.json
  data["cid"] = tempuuid
  data["urls"] = []
  data["default"] = False
  db["collections"][tempuuid] = data
  return ""

@crossdomain(origin="*")
@app.route("/events/create", methods=["POST"])
def create_event():
  tempuuid = str(uuid.uuid4())
  data = request.json
  data["eid"] = tempuuid
  data["comments"] = []
  data["rating"] = 0
  db["events"][tempuuid] = data
  return ""

@crossdomain(origin="*")
@app.route("/events/get/<eid>", methods=["GET"])
def get_event(eid):
  return jsonify(from_db("events")[eid])

@crossdomain(origin="*")
@app.route("/events/all", methods=["GET"])
def all_events():
  return jsonify(list(from_db("events").values()))

@crossdomain(origin="*")
@app.route("/events/comment/<eid>", methods=["POST"])
def add_comment(eid):
  create_user_if_not_exist(request.json["uid"])
  db["events"][eid]["comments"].append(request.json)
  return ""

@crossdomain(origin="*")
@app.route("/events/rate/<eid>", methods=["POST"])
def add_rate(eid):
  db["events"][eid]["rate"] += 1
  return ""

@crossdomain(origin="*")
@app.route("/events/join/<eid>", methods=["POST"])
def join_event(eid):
  create_user_if_not_exist(request.json["uid"])
  db["users"][request.json["uid"]]["events"].append(eid)
  return ""

@crossdomain(origin="*")
@app.route("/users/trash/<uid>", methods=["POST"])
def add_trash(uid):
  create_user_if_not_exist(uid)
  db["users"][uid]["trash"] += int(request.json["trash"])
  return ""

@crossdomain(origin="*")
@app.route("/users/get/<uid>", methods=["GET"])
def get_user(uid):
  create_user_if_not_exist(uid)
  return jsonify(from_db("users")[uid])

@crossdomain(origin="*")
@app.route("/users/all", methods=["GET"])
def all_users():
  return jsonify(list(from_db("users").values()))

app.run(host="0.0.0.0")
