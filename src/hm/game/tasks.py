def schedule_game_tasks():
    from ..tasks.helper import schedule_from_config
    # the import order matters for the order in which the scheduled tasks are being ran for each module
    from .lobby import tasks

    from .heroes import config as heroes_config
    from .guild import config as guild_config
    from .grow import config as grow_config
    from .chat import config as chat_config
    from . import config as game_config

    # from db json config
    schedule_from_config(heroes_config()['tasks'])
    schedule_from_config(guild_config()['tasks'])
    schedule_from_config(grow_config()['tasks'])
    schedule_from_config(game_config()['tasks'])
    schedule_from_config(chat_config()['tasks'])

