from datetime import datetime
from typing import NamedTuple


class WebEntity(NamedTuple):
    id: int
    url: str
    scraped_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
