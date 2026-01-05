import asyncio
import mimetypes
import sys
from collections import deque
from typing import Callable, NamedTuple, Optional
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx as r
from bs4 import BeautifulSoup as bs4

from graph import Attrs, Graph


class CrawlItem(NamedTuple):
    url: str
    parent_id: Optional[int]
    depth: int
    max_depth: int


class Scraper:
    def __init__(
        self,
        name: str = "example.com",
        roots: str | list[str] | dict[str, int] = "https://example.com/",
        depth: int = 2,
        delay: float = 1.0,
        retries: int = 3,
        timeout: float = 2.0,
        get_color: Callable[[str], str] | None = None,
        shorten_labels: bool = False,
    ) -> None:
        self.name = name
        self.delay = delay
        self.timeout = timeout
        self.retries = retries
        self.get_color = get_color or (lambda _: "#3498db")
        self.shorten_labels = shorten_labels
        self._graph = Graph()
        self._queue: deque[CrawlItem] = deque()
        self._url_to_node: dict[str, int] = {}
        self._robots_cache: dict[str, dict] = {}
        self._domains_seen: set[str] = set()
        self._errors: list[str] = []
        self._processed = 0

        # Normalize roots to dict[str, int]
        if isinstance(roots, str):
            self._roots = {roots: depth}
        elif isinstance(roots, list):
            self._roots = {u: depth for u in roots}
        else:
            self._roots = roots

    def _make_label(self, url: str) -> str:
        if not self.shorten_labels:
            return url
        label = url.replace("https://", "").replace("http://", "")
        for suffix in ["/index.html", "/index.htm", "/index.php", "/default.html"]:
            label = label.removesuffix(suffix)
        return label.rstrip("/") or "/"

    def customize_appearance(self, graph: Attrs, nodes: Attrs, edges: Attrs) -> None:
        self._graph.update_graph_attrs(graph)
        self._graph.update_nodes_attrs(nodes)
        self._graph.update_edges_attrs(edges)

    def run(self) -> None:
        asyncio.run(self._scrape())

    async def _scrape(self) -> None:
        print("Jobs:")
        for url, max_depth in self._roots.items():
            print(f"  {url} (depth: {max_depth})")
            self._queue.append(CrawlItem(url, None, 0, max_depth))
        print()

        while self._queue:
            item = self._queue.popleft()
            await self._process_item(item)

        print()
        for err in self._errors:
            print(f"  ERR: {err}")

    def _print_status(self) -> None:
        status = f"Processed: {self._processed} | Queued: {len(self._queue)} | Domains: {len(self._domains_seen)}"
        sys.stdout.write(f"\r{status:<60}")
        sys.stdout.flush()

    async def _process_item(self, item: CrawlItem) -> None:
        if item.url in self._url_to_node:
            if item.parent_id is not None:
                self._graph.add_edge(item.parent_id, self._url_to_node[item.url])
            return

        robots = await self.parse_robots(item.url)
        if not robots.get("can_fetch", True):
            return

        await asyncio.sleep(robots.get("crawl_delay") or self.delay)

        self._processed += 1
        self._domains_seen.add(urlparse(item.url).netloc)
        self._print_status()

        label = self._make_label(item.url)
        node_id = self._graph.add_node(label=label, url=item.url)
        self._graph._dot.node(str(node_id), label, fillcolor=self.get_color(item.url))
        self._url_to_node[item.url] = node_id

        if item.parent_id is not None:
            self._graph.add_edge(item.parent_id, node_id)

        if item.depth >= item.max_depth:
            return

        links = await self.parse_html(item.url)
        if links:
            for link in links:
                self._queue.append(
                    CrawlItem(link, node_id, item.depth + 1, item.max_depth)
                )

    async def parse_robots(self, url: str) -> dict:
        parsed = urlparse(url)
        domain = parsed.netloc

        if domain in self._robots_cache:
            return self._robots_cache[domain]

        robots_url = f"{parsed.scheme}://{domain}/robots.txt"

        for attempt in range(self.retries):
            try:
                async with r.AsyncClient(
                    follow_redirects=True, timeout=self.timeout
                ) as client:
                    resp = await client.get(robots_url)

                if resp.status_code == 404:
                    return {"can_fetch": True, "crawl_delay": None}
                if resp.status_code != 200:
                    return {"can_fetch": True, "crawl_delay": self.delay * 2}

                parser = RobotFileParser()
                parser.parse(resp.text.splitlines())
                result = {
                    "can_fetch": parser.can_fetch("*", url),
                    "crawl_delay": parser.crawl_delay("*"),
                }
                self._robots_cache[domain] = result
                return result

            except Exception:
                if attempt < self.retries - 1:
                    await asyncio.sleep(self.delay)

        return {"can_fetch": True, "crawl_delay": self.delay * 2}

    async def parse_html(self, url: str) -> list[str] | None:
        for attempt in range(self.retries):
            try:
                async with r.AsyncClient(
                    follow_redirects=True, timeout=self.timeout
                ) as client:
                    resp = await client.get(url)

                if resp.status_code != 200:
                    return None
                if "text/html" not in resp.headers.get("content-type", ""):
                    return None

                soup = bs4(resp.text, "html.parser")
                links = []
                for a in soup.find_all("a", href=True):
                    href = urljoin(url, str(a["href"]))
                    mime, _ = mimetypes.guess_type(href)
                    if mime is None or mime == "text/html":
                        links.append(href)
                return links

            except Exception as e:
                self._errors.append(f"{urlparse(url).netloc}: {type(e).__name__}")
                if attempt < self.retries - 1:
                    await asyncio.sleep(self.delay)

        return None

    def render(self, **kwargs) -> None:
        self._graph.render(**kwargs)
