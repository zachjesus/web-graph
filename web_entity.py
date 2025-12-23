from typing import NamedTuple
from datetime import datetime

class WebEntity(NamedTuple):
    url: str
    scraped_at: datetime