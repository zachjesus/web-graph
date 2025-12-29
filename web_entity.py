from typing import NamedTuple
from datetime import datetime

class WebEntity(NamedTuple):
    id: int
    url: str
    scraped_at: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")