from app.utils.events import publish_event
from app.utils.session import write, DailySessionManager, status, BaseSessionManager

PLAY_RESULT = "macro_result"


def _get_arg_pairs(pairs):
    if len(pairs) % 2 != 0:
        raise ValueError("Each key must have a corresponding value (even number of arguments required)")

    # Convert to dictionary
    kwargs = {
        str(pairs[i]): int(pairs[i+1]) if isinstance(pairs[i+1], str) and pairs[i+1].isnumeric()
            else pairs[i+1].encode('utf-8').decode('unicode_escape')
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
        return DailySessionManager.entry(set_name).increment(name, value)
    else:
        return False


def daily(name, data, set_name="status"):
    if data.isnumeric():
        data = int(data)
    publish_event('daily', [name, data, set_name])
    return DailySessionManager.entry(set_name).set(name, data)

def append(set_name="status", entry_name = None, *data):
    #args_pairs =_get_arg_pairs(pairs)
    session = BaseSessionManager.entry(set_name)

    if entry_name is None:
        return False

    # for key, value in args_pairs.items():
    #     current = session.get(key) or ""
    #     r = session.set(key, current + value)

    current = session.get(entry_name) or ""
    r = session.set(entry_name, current + " ".join(data))

    publish_event('append', [set_name, entry_name, data])

    return r

def stats(set_name="status", *pairs):
    args_pairs = _get_arg_pairs(pairs)

    session = BaseSessionManager.entry(set_name)
    r = False
    for key, value in args_pairs.items():
        r = session.set(key, value)

    publish_event('stats', args_pairs)

    return r

def complete(name, set_name="status"):
    publish_event('complete', [name, set_name])
    return DailySessionManager.entry(set_name).mark_complete(name)


# aliases
def menu(name, value="1"):
    publish_event('menu', [name, value])
    if value.isnumeric():
        value = int(value)
    return status('menu').set(name, value)
