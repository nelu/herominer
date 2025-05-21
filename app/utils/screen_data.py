from parse import search

from app.driver.config import parse_coords
from app.utils.session import status


class ScreenData:
    def __init__(self, collection='hero'):
        self._screen_data = status(collection)

    @staticmethod
    def clean_string(text):
        if not text:
            return ""
        if isinstance(text, str):
            text = text.encode('latin-1', errors='replace').decode('utf-8', errors='replace')
            # Normalize and clean
        text = text.replace('\n', ' ').replace('—', '-')
        # Split on pipe and take the first part, then remove leading dash
        name = text.split('|', 1)[0].lstrip('- ')
        return name.strip()

    def parse_data(self, entry, fields_format):
        value = self._screen_data.get(entry)
        return value and search(fields_format, f"{value}")

    def get_target_flag(self, flag):
        value = self._screen_data.get(flag)
        return parse_coords(value) and value or None

    def upgrade_target_flags(self, flags):
        r = 0
        for flag in flags:
            value = self.get_target_flag(flag)
            if value:
                setattr(self, flag, value)
                r += 1

        return r
