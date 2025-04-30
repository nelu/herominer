from flask import request, jsonify, render_template
from . import hero_api
import uuid

from app.game.heroes.hero import Hero
from app.game.heroes.hero_data import HeroData
from app.game.heroes.manager import instance

hdata = HeroData()
@hero_api.route("/", methods=["GET"])
def list_heroes():
    if request.headers.get('Accept') == 'application/json':
        # API request - return JSON
        data = instance.all_heroes(available=False).to_dictionary(lambda h: h._slug)
        serialized = {str(k): v.to_dict() for k, v in data.items()}
        return jsonify(serialized)
    else:
        # Browser request - return HTML
        return render_template("list_heroes.html")

@hero_api.route("/", methods=["POST"])
def create_hero():
    data = request.json or {}
    hero = Hero("nony")  # deep copy
    hero.update(data)
    hero_id = str(uuid.uuid4())
    hero["id"] = hero_id
    return jsonify({"id": hero_id, "data": hero}), 201

@hero_api.route("/edit/<slug>")
def edit_hero(slug):
    return render_template("edit.html", slug=slug)

@hero_api.route("/<hero_id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def hero_ops(hero_id):
    exists = hdata.get_hero(hero_id) and Hero.load(hero_id)
    if request.method == "GET":
        return jsonify(exists.to_dict()) if exists else ({"error": "Not found"}, 404)
    elif request.method in ("PUT", "PATCH"):
        if not exists:
            return {"error": "Not found"}, 404

        if request.json:
            exists.update(request.json)
            exists.save()
        return {"id": hero_id, "data": exists}
    elif request.method == "DELETE":
        return {"message": "Deleted"} if hdata.delete_hero(hero_id) else ({"error": "Not found"}, 404)