from itertools import count
from typing import Dict, Optional, TypeAlias

import graphviz as gv

from web_entity import WebEntity

Attrs: TypeAlias = Dict[str, str]
NodeId: TypeAlias = int


class Graph:
    def __init__(self, name: str = "webgraph") -> None:
        self._dot = gv.Digraph(name=name)

        self._node_id_counter = count(1)

        self._nodes: Dict[NodeId, WebEntity] = dict()
        self._edges: Dict[NodeId, NodeId] = dict()

    def update_graph_attrs(self, attrs: Attrs) -> None:
        self._dot.graph_attr.update(attrs)

    def update_nodes_attrs(self, attrs: Attrs) -> None:
        self._dot.node_attr.update(attrs)

    def update_edges_attrs(self, attrs: Attrs) -> None:
        self._dot.edge_attr.update(attrs)

    def get_node(self, node_id: NodeId) -> WebEntity:
        return self._nodes[node_id]

    def get_nodes(self) -> Dict[NodeId, WebEntity]:
        return self._nodes

    def get_edges(self) -> Dict[NodeId, NodeId]:
        return self._edges

    def add_node(self, label: str, url: str, attrs: Optional[Attrs] = None) -> NodeId:
        node_id = next(self._node_id_counter)
        node = WebEntity(node_id, url)
        self._nodes[node_id] = node
        if attrs:
            self._dot.node(str(node_id), str(label), **attrs)
        else:
            self._dot.node(str(node_id), str(label))
        return node_id

    def add_edge(
        self, source_id: NodeId, target_id: NodeId, attrs: Optional[Attrs] = None
    ) -> None:
        self._edges[source_id] = target_id
        if attrs:
            self._dot.edge(str(source_id), str(target_id), **attrs)
        else:
            self._dot.edge(str(source_id), str(target_id))
    
    def render(self, **kwargs):
        self._dot.render(**kwargs)
