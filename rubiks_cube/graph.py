from typing import Iterable

import networkx as nx

from rubiks_cube.cube import RubikCube
from rubiks_cube.movements import CubeMove


def make_graph(dims: tuple[int, int, int], permitted_movements: set[CubeMove] = None) -> nx.Graph:
    """
    Creates a graph using a Rubik's Cube with dimensions `dims` and permitted movements `permitted_movements`, using
    the Rubik's Cubes as nodes. Two Rubik's Cubes are connected if you can draw it with one movement.

    :param dims: A tuple with the dimensions of a Rubik's Cube
    :param permitted_movements: A set of permitted movements
    :return: A graph as described
    """
    # Principal Rubik's Cube
    rc = RubikCube.from_dims(dims, permitted_movements)
    # Queue to make a BFS
    queue = [rc]
    # The graph
    g = nx.Graph()
    g.add_node(rc)
    while queue:  # While d is not empty
        current_rc = queue.pop()  # Actualize the current cube
        # Make every permitted movement and add the new cube to the graph
        for m in permitted_movements:
            other_rc = current_rc.make_movements(m)
            if other_rc not in g.nodes:
                queue.append(other_rc)  # Add to the queue
                g.add_node(other_rc)  # Add to the graph
            if other_rc not in g[current_rc]:
                g.add_edge(current_rc, other_rc, move=set())
            g[current_rc][other_rc]["move"].add(m)

    def order_list_of_rc(iterable: Iterable[RubikCube]) -> list[RubikCube]:
        ordered_iterable: list[RubikCube] = list(iterable)
        ordered_iterable.sort(key=lambda x: hash(x))
        return ordered_iterable

    for i, rc in enumerate(order_list_of_rc(g.nodes)):
        g.nodes[rc]["id"] = i
    return g


def find_bipartite(g: nx.Graph) -> tuple[set[RubikCube], set[RubikCube]]:
    """
    Find a bipartite in the graph g and label it. Returns the sets of nodes that make the graph bipartite.

    :param g: A graph.
    :return: two sets of nodes that makes the partition.
    """
    U, V = nx.algorithms.bipartite.sets(g)
    for n in g.nodes:
        if n in U:
            g.nodes[n].update(color="blue", bipartite=0)
        else:
            g.nodes[n].update(color="red", bipartite=1)
    return U, V


def make_simple_graph(complex_graph: nx.Graph) -> dict[int, set[int]]:
    """
    Make a simple graph (a dict of sets) from a complex graph (the nx.Graph instance).
    It can be seen as a dictionary of neighbours.

    :param complex_graph: A complex graph.
    :return: A simple graph as described.
    """
    simple_graph: dict[int, set[int]] = {}
    for n in complex_graph.nodes:
        n_id: int = complex_graph.nodes[n]["id"]
        simple_graph[n_id] = {complex_graph.nodes[other]["id"] for other in complex_graph[n]}
    return simple_graph


def generate_file(g: nx.Graph, path=None):
    """
    Creates a file in the format "'number of nodes' 'number of edges'"
    and the different edges with its nodes.

    :param g: A graph
    :param path: A path
    :return: Nothing.
    """
    path = path or "graph.txt"

    simple_graph = make_simple_graph(g)

    def sort_list(other):
        lst = list(other)
        lst.sort()
        return lst

    with open(path, "w") as f:
        # Write n and m
        f.write(f"{len(g.nodes)} {len(g.edges)}\n")
        # Write the edges
        for u in sort_list(simple_graph.keys()):
            for v in sort_list(simple_graph[u]):
                if u < v:
                    f.write(f"{u} {v}\n")
