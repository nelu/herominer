from datetime import datetime
from pytimeparse import parse
from .. import config
from app.utils.screen_data import ScreenData
from app.utils.session import status, daily


class StatusData(dict, ScreenData):
    def __init__(self, data=None, default_data=None, session_name="hero"):
        dict.__init__(self, data or {})  # Directly initialize dict with data
        ScreenData.__init__(self, collection=session_name)  # Directly call ScreenData’s init
        self.available = (data and data.get('available')) or (default_data or {})
        self.last_update = 0

    def is_old(self):
        now_ts = int(datetime.now().timestamp())
        return now_ts - self.last_update >= parse(config()['stats_timeout'])

    def get_upgradable_items(self, sort_by=None, **args):
        filtered = {
            name: item for name, item in self.available.items()
            if self.is_upgradable(item, **args)
        }

        if filtered and sort_by:
            filtered = dict(sorted(filtered.items(), key=lambda item: item[1].get(sort_by) or 0))

        return filtered

    @staticmethod
    def is_upgradable(item, bellow=None):

        if not item["lvl"]:
            return False
        if bellow and item["lvl"] >= bellow:
            return False

        return 0 < item["lvl"]

    def has_upgrades(self, **args):
        return any(
            self.is_upgradable(item, **args)
            for item in self.available.values()
        )

    @staticmethod
    def increase_stats(name, incr=1):
        i = 0
        for s in [daily(), status()]:
            if s.increment(name, incr): i += 1

        return i

    def min_value(self, field='lvl', items=None):
        items = items or self.available.values()
        levels = [
            item.get(field) or 0
            for item in items
            if item.get(field, False) is not False
        ]
        return sum(levels) if levels else float("inf")

    def update(self, mapping=None, **kwargs):
        mapping = mapping or {}
        mapping.update(kwargs)

        for field, value in mapping.items():
            if hasattr(self, field):
                setattr(self, field, value)
            else:
                self[field] = value  # fallback to dict update

        return self

    def to_dict(self):
        output = {}
        for k, v in self.__dict__.items():
            if not k.startswith('_'):
                if isinstance(v, StatusData):
                    output[k] = v.to_dict()
                else:  # if isinstance(v, dict):
                    output[k] = v
        return output
