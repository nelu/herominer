from flask import request, jsonify, render_template
from pytimeparse import parse

from . import task_api
import uuid

from app.tasks.helper import get_configured_tasks
from app.utils.session import status


@task_api.route("/", methods=["GET"])
def list_tasks():
    if request.headers.get('Accept') == 'application/json':
        config_tasks = get_configured_tasks()
        redis_tasks = status('tasks').get_all()

        combined = {}

        # First pass: all configured tasks (persistent)
        for task_name, task in config_tasks.items():
            task_status = redis_tasks.get(task_name, {})
            combined[task_name] = {
                "id": task_name,
                "name": task_name,
                "interval": task.get("interval"),
                "function": str(task.get("function")),
                "args": task.get("args", []),
                "interval_seconds": parse(task.get("interval", "0")),
                "next_run": task["job"].next_run.strftime('%Y-%m-%d %H:%M:%S') if task.get("job") and task[
                    "job"].next_run else "0000-00-00 00:00:00",
                "task_start": task_status.get("task_start"),
                "task_finish": task_status.get("task_finish"),
                "task_nextrun": task_status.get("task_nextrun"),
                "task_result": task_status.get("task_result"),
                "before": task.get("before"),
                "after": task.get("after"),
                "type": task_status.get("once") and "once" or "persistent"
            }

        # Second pass: Redis-only tasks (once-off completed or temporary)
        for task_name, task_status in redis_tasks.items():
            if task_name not in combined:
                combined[task_name] = {
                    "id": task_name,
                    "name": task_name,
                    "interval": None,
                    "function": task_status.get("function"),
                    "interval_seconds": None,
                    "next_run": None,
                    "task_start": task_status.get("task_start"),
                    "task_finish": task_status.get("task_finish"),
                    "task_nextrun": task_status.get("task_nextrun"),
                    "task_result": task_status.get("task_result"),
                    "type": "once"
                }

        return jsonify(combined)

    else:
        # Browser request - return HTML
        return render_template("list_tasks.html")


@task_api.route("/", methods=["POST"])
def create_task():
    data = request.json or {}
    task_id = str(uuid.uuid4())

    task_name = data.get("name") or f"task_{task_id}"
    function_name = data.get("function")
    once = data.get("once", True)
    interval = data.get("interval", once and "1 second" or None)

    # Simple validation
    if not function_name or not interval:
        return jsonify({"error": "Function name, interval is required"}), 400

    # Schedule the task (simplified example)
    try:
        from app.utils.events import publish_event
        r = publish_event("schedule_task", [{
            "name": task_name,
            "function": function_name,
            "interval": interval,
            "args": data.get("args", []),
            "once": once
        }])

        return jsonify({"id": task_name, "data": data, "ack": r}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@task_api.route("/<task_id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def task_ops(task_id):
    # Get all scheduled jobs
    existing_task = status('tasks').get(task_id)

    if not existing_task:
        return jsonify({"error": "Task not found"}), 404

    if request.method == "GET":
        task_data = {
            "id": task_id,
            "name": getattr(existing_task.job_func, "__name__", "unknown"),
            "interval": getattr(existing_task, "interval", "unknown"),
            "at_time": getattr(existing_task, "at_time", None),
            "next_run": existing_task.next_run.strftime('%Y-%m-%d %H:%M:%S') if existing_task.next_run else None,
            "last_run": existing_task.last_run.strftime('%Y-%m-%d %H:%M:%S') if existing_task.last_run else None,
            "tags": list(existing_task.tags),
        }
        return jsonify(task_data)

    elif request.method in ("PUT", "PATCH"):
        if not existing_task:
            return jsonify({"error": "Task not found"}), 404

        # Update task - this would need custom implementation
        # based on your scheduling system
        return jsonify({"message": "Task updated", "id": task_id})

    elif request.method == "DELETE":

        return jsonify({"message": "Task deleted", "count": status('tasks').remove(task_id)})

    return jsonify({"error": f"Invalid method {request.method}"}), 404
