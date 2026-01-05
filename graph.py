from collections import defaultdict
from itertools import count
from typing import Dict, Optional, Set, TypeAlias

import graphviz as gv

from web_entity import WebEntity

Attrs: TypeAlias = Dict[str, str]


class Graph:
    def __init__(self, name: str = "webgraph") -> None:
        self._dot = gv.Digraph(name=name)

        self._node_id_counter = count(1)

        self._nodes: Dict[int, WebEntity] = dict()
        self._edges: Dict[int, Set[int]] = defaultdict(set)

        self.update_graph_attrs = self._dot.graph_attr.update
        self.update_nodes_attrs = self._dot.node_attr.update
        self.update_edges_attrs = self._dot.edge_attr.update
        self.render = self._dot.render

    def get_node(self, node_id: int) -> WebEntity:
        return self._nodes[node_id]

    def get_nodes(self) -> Dict[int, WebEntity]:
        return self._nodes

    def get_edges(self) -> Dict[int, Set[int]]:
        return self._edges

    def add_node(self, label: str, url: str, attrs: Optional[Attrs] = None) -> int:
        node_id = next(self._node_id_counter)
        node = WebEntity(node_id, url)
        self._nodes[node_id] = node
        if attrs:
            self._dot.node(str(node_id), str(label), **attrs)
        else:
            self._dot.node(str(node_id), str(label))
        return node_id

    def add_edge(
        self, source_id: int, target_id: int, attrs: Optional[Attrs] = None
    ) -> None:
        if target_id in self._edges[source_id]:
            return
        self._edges[source_id].add(target_id)
        if attrs:
            self._dot.edge(str(source_id), str(target_id), **attrs)
        else:
            self._dot.edge(str(source_id), str(target_id))
