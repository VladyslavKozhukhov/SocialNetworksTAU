import networkx as nx
import random
import math 
from itertools import cycle
import collections
import matplotlib.pyplot as plt
#import networkx.algorithms.cluster as acluster

# note: written for python 3.6 or above

def erdos_renyl(n, p):
    """
    Input:  n - number of nodes
            p - probability of an edge
    Return random graph by erdos-renyl model with these parameters 
    """
    # first create a graph of the correct size:
    g = nx.Graph()
    g.add_nodes_from(range(n))

    # for each node, iterate over all nodes after it and randomly determine if an edge should exist
    for i in range(n):
        for j in range(i+1, n):
            if random.random() < p:
                g.add_edge(i,j)
    return g

def small_world(n, k, p):
    """
    Input:  n - number of nodes
            k - average degree
            p - probability for edge
    Return random graph using small world model
    """
    # step1 create the graph will k-neighbor nodes
    g = nx.Graph()
    nodes = range(n)
    g.add_nodes_from(nodes)
    nbrs = k//2
    for i in range(n):
        for j in range(1, nbrs + 1):
            g.add_edge(i, (i+j) % n)
            g.add_edge(i, (i-j) % n)
    # now, for each node, relocate it's right edges with probability p:
    for i in range(n):
        for j in range(1, nbrs + 1):
            if random.random() < p:
                g.remove_edge(i, (i+j) % n)
                non_neighbors = get_non_neighbors(g, i)
                g.add_edge(i, random.choice(list(non_neighbors)))
    return g


def get_non_neighbors(g, i):
    """
    Return all edges in graph g not connected to node i. 
    Result will not include i even if no self edge exists"
    """
    return set(g.nodes) - set(g.neighbors(i)) - set([i])

def graph_cluster_coeff(g):
    "Compute and return clastering coefficient for graph g"
    sum = 0
    for node in g.nodes:
        sum += node_cluster_coeff(g, node)

    return sum / g.number_of_nodes()


def node_cluster_coeff(g, i):
    "Return clustering coefficient for node i"
    neighbors = set(g.neighbors(i))
    count = 0
    for neighbor in neighbors:
        count += len(set(g.neighbors(neighbor)).intersection(neighbors))

    # we counter every edge twice:
    count /= 2
    max_links = len(neighbors) * (len(neighbors)-1) * 0.5
    res = count / max_links
    # for testing:
    #assert math.isclose(acluster.clustering(g, i), res)
    return res

def mytests():
    for n in [100, 1000, 2000]:
        p = 0.2
        g = erdos_renyl(n, p)
        print(f"Erdos-Renyl for n={n} has {g.number_of_edges()} edges. Expected:{p * n *(n-1)* 0.5 }")

    for n in [100,1000]:
        p = 0.2
        k = 10
        g = small_world(n,k,p)
        print(f"Small world clustering coefficient:{graph_cluster_coeff(g)}")

# Histogram code taken from:
# https://networkx.github.io/documentation/stable/auto_examples/drawing/plot_degree_histogram.html
def show_degree_histogram(name, g, save=True):
    degree_sequence = sorted([d for n, d in g.degree()], reverse=True)  # degree sequence
    # print "Degree sequence", degree_sequence
    degreeCount = collections.Counter(degree_sequence)
    deg, cnt = zip(*degreeCount.items())

    fig, ax = plt.subplots()
    plt.bar(deg, cnt, width=0.80, color='b')

    plt.title(f"Degree Histogram for {name}")
    plt.ylabel("Count")
    plt.xlabel("Degree")
    # ax.set_xticks([d + 0.4 for d in deg])
    # ax.set_xticklabels(deg)

    # draw graph in inset
    plt.axes([0.4, 0.4, 0.5, 0.5])
    Gcc = sorted(nx.connected_component_subgraphs(g), key=len, reverse=True)[0]
    pos = nx.spring_layout(g)
    plt.axis('off')
    #nx.draw_networkx_nodes(g, pos, node_size=20)
    #nx.draw_networkx_edges(g, pos, alpha=0.4)

    # plt.show()
    if save:
        fig.savefig(f'{name}_histogram.png', dpi=fig.dpi)


def analyze(name, g):
    print("Calculating coefficient...")
    cluster_coeff = graph_cluster_coeff(g)
    print("Calculating diameter...")
    try:
        diam = nx.diameter(g)
    except nx.NetworkXError as e:
        diam = "Infinite"
    print(f"{name} cluster coeff:{cluster_coeff}, diameter={diam}")
    print("Saving plot...")
    show_degree_histogram(name, g)



def question_d():
    n = 1000
    g1 = erdos_renyl(n, 0.2)
    g2 = small_world(n, 8, 0.1)

    analyze(f"Erdos-Renyl", g1)
    analyze(f"Small World", g2)

if __name__ == "__main__":
    # mytests()
    question_d()
    pass
