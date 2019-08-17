def three_groups(n):
    g = nx.Graph()
    group_size = n//3
    nodes = list(range(n))
    g.add_nodes_from(nodes)
    for i in range(3):
        edges = itertools.combinations(range(i*group_size, i*group_size + group_size, 1),2)
        g.add_edges_from(edges)
    return g
