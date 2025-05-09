import time
import json
from app.utils.redis_helpers import redis_client as redis
from app.utils.service import check_shutdown

EVENT_HANDLERS = {}
pubsub = redis.pubsub(ignore_subscribe_messages=True)

def register_event(event_type, handler):
    """
    Register a handler function for a specific Redis event type.
    Automatically subscribes to the channel.
    """
    if event_type not in EVENT_HANDLERS:
        EVENT_HANDLERS[event_type] = []
        pubsub.subscribe(event_type)
    EVENT_HANDLERS[event_type].append(handler)

def unregister_event(event_type, handler):
    """
    Optionally unregister a specific handler.
    """
    if event_type in EVENT_HANDLERS:
        EVENT_HANDLERS[event_type] = [h for h in EVENT_HANDLERS[event_type] if h != handler]
        if not EVENT_HANDLERS[event_type]:
            del EVENT_HANDLERS[event_type]

def one_time_handler(event_type, handler):
    """
    Register a handler that automatically unregisters itself after being called once.
    """
    def wrapper(data):
        try:
            handler(data)
        finally:
            unregister_event(event_type, wrapper)
    register_event(event_type, wrapper)

def poll_event(event_type, handler=None):
    """
    Polls Redis pubsub once. If an event matching event_type is found, calls handler.
    Returns the data if event matched, otherwise None.
    """
    message = pubsub.get_message()
    if message and message["type"] == "message":
        try:
            payload = json.loads(message["data"])
            if payload.get("event") == event_type:
                data = payload.get("data", {})
                if handler:
                    handler(data)
                return data
        except Exception as e:
            print(f"[poll_event] Error: {e}")
    return None

def on_event(event_type, handler=None, timeout=None):
    """
    Blocking wait for a specific event. Returns the event data or None on timeout.
    """
    local_pubsub = redis.pubsub(ignore_subscribe_messages=True)
    local_pubsub.subscribe(event_type)

    start_time = time.time()

    while True:
        message = local_pubsub.get_message()
        if message and message["type"] == "message":
            try:
                payload = json.loads(message["data"])
                if payload.get("event") == event_type:
                    data = payload.get("data", {})
                    if handler:
                        handler(data)
                    local_pubsub.close()
                    return data
            except Exception as e:
                print(f"[on_event] Error: {e}")

        if timeout and (time.time() - start_time) > timeout:
            local_pubsub.close()
            return None

        time.sleep(0.25)

def run_handle_events():
    """
    Poll Redis for any registered events and dispatch them.
    Also calls check_shutdown() for global shutdown checks.
    """
    message = pubsub.get_message()
    if message and message["type"] == "message":
        try:
            payload = json.loads(message["data"])
            event_type = payload.get("event")
            data = payload.get("data", [])

            for handler in EVENT_HANDLERS.get(event_type, []):
                handler(*data)

        except Exception as e:
            print(f"[run_handle_events] Error: {e}")

    # Passive shutdown trigger or service signal hook
    check_shutdown()


def publish_event(event_type, data):
    """
    Publish an event with structured data.
    """
    message = {
        "event": event_type,
        "data": data
    }
    return redis.publish(event_type, json.dumps(message))
