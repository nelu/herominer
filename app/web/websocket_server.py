import os
import threading
import time
import redis

from flask_socketio import SocketIO
from . import WebServer  # Your base class
from app.utils.redis_helpers import redis_client


class SocketIOWebServer(WebServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.socketio = SocketIO(self.app, async_mode='threading')

        self.redis_stream_key = "logs"
        self._stop_event = threading.Event()
        self._stream_thread = threading.Thread(target=self._stream_logs, daemon=True)
        self._server_thread = None

        self._register_socketio_handlers()

    def _register_socketio_handlers(self):
        @self.socketio.on('connect')
        def on_connect():
            print("🧠 WebSocket client connected")

        @self.socketio.on('disconnect')
        def on_disconnect():
            print("🔌 WebSocket client disconnected")

    def _stream_logs(self):
        last_id = '$'
        while not self._stop_event.is_set():
            try:
                messages = redis_client.xread({self.redis_stream_key: last_id}, block=5000)
                for _, entries in messages:
                    for msg_id, data in entries:
                        last_id = msg_id

                        # No decoding needed — data is already str:str
                        log_data = dict(data)  # or just use `data` directly

                        formatted = (
                            f"{log_data['asctime']} "
                            f"[{log_data['process']}] "
                            f"{log_data['levelname']} "
                            f"[{log_data['name']}] "
                            f"- {log_data['msg']}"
                        )
                        self.socketio.emit("log", {"message": formatted})

            except Exception as e:
                print(f"[LogStreamer] Error: {e}")
                time.sleep(1)

    def start(self, threaded=True):
        if not self._stream_thread.is_alive():
            self._stream_thread.start()

        def run_server():
            print(f"🚀 Starting Flask-SocketIO server on {self.host}:{self.port}")
            self.socketio.run(self.app, host=self.host, port=self.port, debug=self.debug, allow_unsafe_werkzeug=True)

        if threaded:
            self._server_thread = threading.Thread(target=run_server, daemon=True)
            self._server_thread.start()
        else:
            run_server()  # Blocking mode

    def stop(self):
        print("🛑 Stopping WebSocket server")
        self._stop_event.set()
        if self._server_thread and self._server_thread.is_alive():
            self._server_thread.join(timeout=5)
