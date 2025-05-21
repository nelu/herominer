
from flask import Flask, send_from_directory, render_template
import threading
import os

from app import settings


class WebServer:
    def __init__(self, host='0.0.0.0', port=80, static_folder='web', debug=False):
        self.host = host
        self.port = port
        self.debug = debug
        self.static_folder = os.path.join(settings.APP_DATA_DIR, static_folder)
        self.app = Flask(__name__, static_folder=self.static_folder,
                         template_folder=os.path.join(self.static_folder, "templates"))
        from .heroes import hero_api
        from .tasks import task_api
        from .configuration import config_api
        self.app.register_blueprint(hero_api, url_prefix="/heroes")
        self.app.register_blueprint(task_api, url_prefix="/tasks")
        self.app.register_blueprint(config_api, url_prefix="/configuration")
        # self.app.logger.setLevel(logging.DEBUG)
        self._thread = None
        self.register_routes()

    def register_routes(self):
        @self.app.route("/")
        def index():
            return render_template("main.html")
            
        @self.app.route("/static/<path:filename>")
        def serve_static(filename):
            return send_from_directory(self.static_folder, filename)

    def start(self):
        if self._thread and self._thread.is_alive():
            print("Server is already running.")
            return

        def run():
            self.app.run(host=self.host, port=self.port, debug=self.debug, use_reloader=False, threaded=True)

        self._thread = threading.Thread(target=run, daemon=True)
        self._thread.start()
        print(f"🚀 Server running at http://{self.host}:{self.port}")

    def stop(self):
        print("🛑 Stop requested. Use CTRL+C to terminate. Flask dev server can't be stopped programmatically.")
