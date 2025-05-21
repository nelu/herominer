from flask import request, jsonify, render_template

from app.driver import JSONConfig
from app.utils.session import status
from . import config_api


@config_api.route("/", methods=["GET"])
def list_configs():
    if 'application/json' in request.headers.get('Accept'):
        store = status("config_data")
        all_configs = store.get_all()
        return jsonify(all_configs)
    else:
        # Browser request - return HTML
        return render_template("list_configs.html")

@config_api.route("/", methods=["POST"])
def create_config():
    data = request.json or {}
    name = data.get("name")
    content = data.get("content", {})

    if not name:
        return jsonify({"error": "Missing configuration name"}), 400
    if not name.endswith(".json"):
        name += ".json"

    store = status("config_data")
    if store.get(name):
        return jsonify({"error": f"Configuration '{name}' already exists"}), 409

    try:
        cfg = JSONConfig(name)
        cfg.clear()
        cfg.update(content)
        cfg.save()
        return jsonify({"message": f"Created config '{name}'", "data": dict(cfg)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@config_api.route("/<name>", methods=["GET"])
def get_config(name):
    if not name.endswith(".json"):
        name += ".json"
    cfg = JSONConfig(name)
    return jsonify(dict(cfg))


@config_api.route("/<name>", methods=["PUT"])
def update_config(name):
    if not name.endswith(".json"):
        name += ".json"

    try:
        cfg = JSONConfig(name)
        data = request.json or {}
        cfg.clear()
        cfg.update(data)
        cfg.save()
        return jsonify({"message": f"{name} updated", "data": dict(cfg)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@config_api.route("/<name>", methods=["DELETE"])
def delete_config(name):
    if not name.endswith(".json"):
        name += ".json"

    try:
        cfg = JSONConfig(name)
        cfg.reset()
        return jsonify({"message": f"{name} cleared"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
