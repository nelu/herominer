import base64

from app.utils.events import publish_event
from app.utils.session import write, status, persist, daily

PLAY_RESULT = "macro_result"


def _get_arg_pairs(pairs):
    if len(pairs) % 2 != 0:
        raise ValueError("Each key must have a corresponding value (even number of arguments required)")

    # Convert to dictionary
    kwargs = {
        str(pairs[i]): int(pairs[i + 1]) if isinstance(pairs[i + 1], str) and pairs[i + 1].isnumeric()
        else pairs[i + 1].encode('utf-8').decode('unicode_escape')
        for i in range(0, len(pairs), 2)
    }

    return kwargs


# api entrypoint for cli actions
def action(value="1"):
    if value.isnumeric():
        value = int(value)
    write(PLAY_RESULT, value)
    return publish_event(PLAY_RESULT, [value])


def out(name, data):
    publish_event('out', [name, data])
    return write(name, data)


def incr(name, value="1", set_name="status"):
    if value.isnumeric():
        value = int(value)
        publish_event('incr', [name, value, set_name])
        return daily(set_name).increment(name, value)
    else:
        return False


def _set_session_values(session, data_pairs):
    r = 0
    for key, value in data_pairs.items():
        if value and isinstance(value, str) and value.isdigit():
            value = int(value)
        session.set(key, value)
        r += 1

    return r


def day(set_name="status", *data_pairs):
    args_pairs = _get_arg_pairs(data_pairs)
    r = _set_session_values(daily(set_name), args_pairs)
    publish_event('daily', [set_name, args_pairs])
    return r


def append(set_name="status", entry_name=None, *data):
    # args_pairs =_get_arg_pairs(pairs)
    session = status(set_name)

    if entry_name is None:
        return False

    # for key, value in args_pairs.items():
    #     current = session.get(key) or ""
    #     r = session.set(key, current + value)

    current = session.get(entry_name) or ""
    r = session.set(entry_name, current + " ".join(data))

    publish_event('append', [set_name, entry_name, data])

    return r


def stats(set_name="status", *data_pairs):
    args_pairs = _get_arg_pairs(data_pairs)
    r = _set_session_values(status(set_name), args_pairs)
    publish_event('stats', [set_name, args_pairs])

    return r


def complete(name, set_name="status"):
    publish_event('complete', [name, set_name])
    return daily(set_name).mark_complete(name)


def file(*file_pairs):
    args_pairs = _get_arg_pairs(file_pairs)
    publish_event('file', [args_pairs])
    r = 0
    for key, value in args_pairs.items():
        if persist(key, value):
            r += 1

    return r

def file_b64(*file_pairs):
    args_pairs = _get_arg_pairs(file_pairs)
    publish_event('file_img', [args_pairs])
    r = 0
    for key, value in args_pairs.items():
        if persist(key, base64.b64decode(value)):
            r += 1

    return r

# aliases
def menu(name, value="1"):
    publish_event('menu', [name, value])
    if value.isnumeric():
        value = int(value)
    return status('menu').set(name, value)
