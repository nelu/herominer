import json
import os

from app.game import game_stats
from app.utils.session import daily

temp = daily('tests')
game_stats.api_response = '{"result": null}'


def load_fixture(filename):
    path = os.path.join(os.path.dirname(__file__), 'fixtures', filename)
    with open(path, 'r', encoding='utf-8') as f:
        jdata = json.load(f)
        for entry in jdata:
            temp.set(entry['field'], entry['value'])
        return jdata

