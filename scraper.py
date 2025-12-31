import sys
from collections import deque
from typing import List
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx as r
from bs4 import BeautifulSoup as bs4

from graph import Attrs, Graph


class Scraper:
    def __init__(
        self,
        name: str = "Web Graph",
        root: str = "https://example.com/",
        depth: int = 2,
        rate: float = 0.5,
        retries: int = 3,
        timeout: float = 2.0,
    ) -> None:
        self.name = name
        self.root = root
        self.depth = depth
        self.rate = rate
        self.timeout = timeout
        self.retries = retries
        self._graph = Graph()
        self._queue = deque()
        self._curr_depth = 0
        self._stop_render = False

    def customize_appearance(self, graph: Attrs, nodes: Attrs, edges: Attrs) -> None:
        """Pass a dictionary of strings attribute name pointing to value."""
        self._graph.update_graph_attrs(graph)
        self._graph.update_nodes_attrs(nodes)
        self._graph.update_edges_attrs(edges)

    def run(self) -> None:
        self._queue.append(self.root)

        while self._queue and self._curr_depth < self.depth:
            url = self._queue.pop()
            self.grab_urls(url)
            self.render()
            
        while True:
            self.render()

    def grab_urls(self, url: str, urls: set[str]) -> None:
        self._curr_depth += 1

    def render(self) -> None:
        if self._stop_render:
            sys.exit("Render Stopped")
        self._graph.render()

    def stop_render(self) -> None:
        self._stop_render = True
