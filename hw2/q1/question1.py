import collections
from collections import defaultdict
import sys
import networkx as nx


# This class makes it easier mapping of edges to a number
class EdgeScores(defaultdict):
    def __init__(self):
        # default score is 0, int is the same as lambda:0
        super(EdgeScores, self).__init__(int)

    def __setitem__(self, key, value):
        # key is (u,v). Sort it cause graph is non-directed
        u, v = sorted(key)
        super(EdgeScores, self).__setitem__((u,v),value)

    def __getitem__(self, key):
        # key is (u,v). Sort it cause graph is non-directed
        u, v = sorted(key)
        return super(EdgeScores, self).__getitem__((u,v))

    def __contains__(self, key):
        # key is (u,v). Sort it cause graph is non-directed
        u, v = sorted(key)
        return super(EdgeScores, self).__contains__((u,v))

    def get_highest(self):
        """
        Return a list of edges that have the maximum score in this dict.
        """
        max_lst = []
        max_score = 0
        for e, score in self.items():
            if score > max_score:
                max_lst=[e]
                max_score = score
            elif score == max_score:
                max_lst.append(e)
        return max_lst


def print_components(g):
    for idx, component in enumerate(nx.connected_components(g)):
        print("Component {} of size:{}".format(idx+1, len(component)))
        print(component)


def calc_node_betweeness(g, n):
    """
    Helper function for calc_edge_betweenness.
    Calculate the edge betweenness scores for bfs garph starting in
    node labeled n in graph g
    """
    t = nx.bfs_tree(g, n)
    weights = EdgeScores()
    def recursive_update(G, starting_node, weights):
        """
        Update weights on graph G starting from starting_node
        Returns weight of the edges leading to starting_node
        """
        out_edges = G.edges(starting_node)
        if len(out_edges) == 0:
            for e in G.in_edges(starting_node):
                weights[e] = 1
            return 1
        # else: recursively update the dict for all children.
        # Calculate edge sum of children
        total = 0
        for u,v in out_edges:
            total += recursive_update(G, v, weights)
        # update weight of edge leading here(one edge,really): weight is children_total+1
        for e in G.in_edges(starting_node):
            weights[e] = total + 1
        return total + 1
    recursive_update(t, n, weights)
    return weights


def calc_edge_betweenness(g):
    """
    Given graph g, calculate edge betweeness for each edge.
    Returns EdgeScores class(dict-like edge to score)
    """
    totals = EdgeScores()
    for node in g.nodes:
        cur_scores = calc_node_betweeness(g, node)
        for e in cur_scores:
            totals[e] += cur_scores[e]
    # finally, divide all values by 2:
    for e in totals:
        totals[e] = int(totals[e]/2)
    return totals


def neuman_girvan(network, k):
    while True:
        num_of_components = len(list(nx.connected_components(network)))
        if num_of_components >= k or network.number_of_edges() == 0:
            # algorithm is finished
            break
        scores = calc_edge_betweenness(network)
        network.remove_edges_from(scores.get_highest())
    print_components(network)


def load_graph(fname):
    """
    Load graph from a file formatted as the communities file in the assignment.
    """
    g = nx.Graph()
    with open(fname) as fl:
        for line in fl:
            u, v = line.split(" ")
            g.add_edge(int(u), int(v))
    print("Loaded graph with {} nodes".format(len(g.nodes)))
    return g


def biggest_component(G):
    """
    Return largest connected component of graph G
    """
    Gc = max(nx.connected_component_subgraphs(G), key=len)
    print("Larget component size: {}".format(len(Gc.nodes)))
    return Gc

def get_lecture_graph():
    """
    For debugging purposes.
    Construct and return graph from slide 14 in the lecture
    """
    g = nx.Graph()
    g.add_edge("A", "C")
    g.add_edge("A", "B")
    g.add_edge("C", "B")
    g.add_edge("C", "D")
    g.add_edge("D", "E")
    g.add_edge("D", "F")
    g.add_edge("E", "F")
    return g

def main(input_file):
    g = load_graph(input_file)
    g = biggest_component(g)
    # this is for debugging:
    # g = get_lecture_graph()
    neuman_girvan(g, 3)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    else:
        fname = "communities.txt"
    main(fname)