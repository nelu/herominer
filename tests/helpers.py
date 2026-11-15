import json
from pathlib import Path

from hm.game import game_stats
from hm.utils.session import daily

temp = daily('tests')
game_stats.api_response = '{"result": null}'


def load_fixture(filename):
    path = Path(__file__).parent / 'fixtures' / filename
    with path.open(encoding='utf-8') as fixture:
        data = json.load(fixture)
        for entry in data:
            temp.set(entry['field'], entry['value'])
        return data
