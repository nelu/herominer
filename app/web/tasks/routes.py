from flask import request, jsonify, render_template
from . import task_api
import uuid

from app.tasks.helper import schedule_tasks, get_configured_tasks, get_last_run
import schedule

@task_api.route("/", methods=["GET"])
def list_tasks():
    if request.headers.get('Accept') == 'application/json':
        # API request - return JSON
        #jobs = schedule.get_jobs()
        tasks = {}
        for task_name, task in get_configured_tasks().items():
            tasks[task_name] = {
                "id": task_name,
                "name": task_name,
                "interval": task['interval'],
                "next_run": str(task['job'].next_run),
                "last_run": str(get_last_run(task_name))
            }
        return jsonify(tasks)
    else:
        # Browser request - return HTML
        return render_template("list_tasks.html")

@task_api.route("/", methods=["POST"])
def create_task():
    data = request.json or {}
    task_id = str(uuid.uuid4())
    
    # Example of how you might schedule a task
    # This would need to be implemented based on your scheduling system
    task_name = data.get("name", "unknown_task")
    interval = data.get("interval", "1 hour")
    function_name = data.get("function", "")
    
    # Simple validation
    if not function_name:
        return jsonify({"error": "Function name is required"}), 400
    
    # Schedule the task (simplified example)
    try:
        task_data = {
            task_name: {
                "function": function_name,
                "interval": interval,
                "args": data.get("args", [])
            }
        }
        schedule_tasks(task_data)
        return jsonify({"id": task_id, "data": data}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@task_api.route("/edit/<task_id>")
def edit_task(task_id):
    return render_template("edit_task.html", task_id=task_id)

@task_api.route("/<task_id>", methods=["GET", "PUT", "PATCH", "DELETE"])
def task_ops(task_id):
    # Get all scheduled jobs
    jobs = schedule.get_jobs()
    existing_task = None
    
    # Find the task with the matching ID
    for job in jobs:
        if str(job.job_id) == task_id:
            existing_task = job
            break
    
    if request.method == "GET":
        if not existing_task:
            return jsonify({"error": "Task not found"}), 404
            
        task_data = {
            "id": task_id,
            "name": getattr(existing_task.job_func, "__name__", "unknown"),
            "interval": getattr(existing_task, "interval", "unknown"),
            "at_time": getattr(existing_task, "at_time", None),
            "next_run": existing_task.next_run,
            "last_run": existing_task.last_run,
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
        if not existing_task:
            return jsonify({"error": "Task not found"}), 404
            
        # Cancel the scheduled task
        schedule.cancel_job(existing_task)
        return jsonify({"message": "Task deleted"})
