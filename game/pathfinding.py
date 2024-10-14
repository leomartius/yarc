from __future__ import annotations

import numpy as np
import tcod.path

type CostArray = np.ndarray[tuple[int, int], np.dtype[np.int8]]


# Use the A* algorithm to find the shortest path on a graph with custom edge rules.
def find_path(start: tuple[int, int], goal: tuple[int, int], cost: CostArray) -> list[tuple[int, int]]:
    graph = _create_graph(cost)
    pathfinder = tcod.path.Pathfinder(graph)
    pathfinder.add_root(goal)
    path = pathfinder.path_from(start)
    return [tuple(e) for e in path.tolist()]


# Create a custom graph that adheres to the no corner-cutting rule.
def _create_graph(cost: CostArray) -> tcod.path.CustomGraph:
    assert np.min(cost) >= 0 and np.max(cost) <= 1
    graph = tcod.path.CustomGraph(cost.shape, order='F')
    graph.add_edges(edge_map=[[0, 2, 0], [2, 0, 2], [0, 2, 0]], cost=cost)
    padded = np.pad(cost, pad_width=1)
    for dx, dy in [(-1, -1), (+1, -1), (-1, +1), (+1, +1)]:
        graph.add_edge(
            edge_dir=(dx, dy),
            edge_cost=3,
            cost=cost,
            condition=_slide(padded, dx, dy) * _slide(padded, 0, dy) * _slide(padded, dx, 0) * cost,
        )
    graph.set_heuristic(cardinal=2, diagonal=3)
    return graph


def _slide(padded_matrix: CostArray, dx: int, dy: int) -> CostArray:
    w, h = padded_matrix.shape
    return padded_matrix[dx + 1 : dx + w - 1, dy + 1 : dy + h - 1]
