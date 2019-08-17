import networkx as nx
import matplotlib.pyplot as plt
import random


# Qusetion 3a

def check_balance(G):
    triangles = [cycle for cycle in nx.cycle_basis(G) if len(cycle) == 3]
    for t in triangles:
        if not is_triangle_balanced(G, t):
            return False, t
    return True, None


def is_triangle_balanced(G, triangle):
    e1 = (triangle[0], triangle[1])
    e2 = (triangle[1], triangle[2])
    e3 = (triangle[0], triangle[2])
    edges_sign = nx.get_edge_attributes(G, 'sign')
    if e1 in edges_sign:  # undirected graph - check both i->j j->i
        sign1 = edges_sign[e1]
    else:
        sign1 = edges_sign[e1[::-1]]
    if e2 in edges_sign:
        sign2 = edges_sign[e2]
    else:
        sign2 = edges_sign[e2[::-1]]
    if e3 in edges_sign:
        sign3 = edges_sign[e3]
    else:
        sign3 = edges_sign[e3[::-1]]
    return [sign1, sign2, sign3].count('-') % 2 == 0


# Qusetion 3a V2

def check_balance_v2(G):
    try:
        G = get_connected_components_on_plus_edges_graph(G)
    except NoConnectedComponentError as e:
        return False, G, dict([(x,0) for x in e.err_group]), e.err_node
    G.remove_edges_from(G.selfloop_edges())
    component_list = [c for c in sorted(nx.connected_components(G), key=len, reverse=True)]
    node_coloring = dict((k, 0) for k in G.nodes())
    for component_nodes in component_list:
        is_balanced, bad_vertex = check_component_is_balanced(G, list(component_nodes)[0], node_coloring)
        if not is_balanced:
            return False, G, node_coloring, bad_vertex
    return True, G, None, None


def check_component_is_balanced(G, start, node_coloring):
    visited, queue = set(), [start]
    node_coloring[start] = 1
    while queue:
        vertex = queue.pop(0)
        neighbors_colors_already_used = set()
        for nextVertex in G.neighbors(vertex):
            neighbors_colors_already_used.add(node_coloring[nextVertex])
            if node_coloring[nextVertex] == 0:
                queue.append(nextVertex)
        if 1 in neighbors_colors_already_used and 2 in neighbors_colors_already_used:
            return False, vertex
        else:
            if 1 not in neighbors_colors_already_used:
                node_coloring[vertex] = 1
            else:
                node_coloring[vertex] = 2
    return True, None

class NoConnectedComponentError(RuntimeError):
    def __init__(self, err_node, err_group):
        self.err_node = err_node
        self.err_group = err_group

def get_connected_components_on_plus_edges_graph(G):
    res = G.copy()
    for n in list(G.nodes):
        if not res.has_node(n):
            # we already handled this node by contracting it.
            continue
        attr = nx.get_edge_attributes(G, "sign")
        def get_attr(edge):
            # cause dict keys arent comutative
            a,b = edge
            return attr.get((a,b)) or attr.get((b,a))

        cur_group = {n}
        for e in list(res.edges(n)):
            if get_attr(e) == '-':
                # skip minus connections
                pass
            else:
                # try to concat
                assert e[0] == n
                b = e[1]
                for cur_edge in G.edges(b):
                    assert cur_edge[0] == b
                    err_candidate = cur_edge[1]
                    # check if b has any minus edge to the current group
                    if get_attr(cur_edge) == '-' and err_candidate in cur_group:
                        #fail
                        err = NoConnectedComponentError(b, cur_group)
                        raise err
                # successfully concat
                cur_group.add(b)
                res.remove_node(b)
    return res


#####################################################################
#####################################################################

# Qusetion 3b

def generateRandomNetworkWithER(p_plus):
    G = nx.Graph()
    n = 30
    p = 0.5
    for i in range(0, n):
        G.add_node(i)
    for i in range(0, n - 1):
        for j in range(i + 1, n):
            if p >= random.uniform(0, 1):  # create edge with prob >= p
                if p_plus >= random.uniform(0, 1):  # edge is + with prob >= p_plus
                    G.add_edge(i, j, sign='+')
                else:
                    G.add_edge(i, j, sign='-')
    return G


def generate_graphs_for_question_3b():
    G1 = generateRandomNetworkWithER(0.9)
    G2 = generateRandomNetworkWithER(0.5)
    return G1, G2


#####################################################################
#####################################################################

# Qusetion 3c

def check_balance_run():
    G1, G2 = generate_graphs_for_question_3b()
    is_balanced_G1, unbalanced_triangle_G1 = check_balance(G1)
    is_balanced_G2, unbalanced_triangle_G2 = check_balance(G2)
    print("G1 is: " + ("balanced" if is_balanced_G1 else "unbalanced"))
    print_graph_with_reasons(G1, unbalanced_triangle_G1)
    print("G2 is: " + ("balanced" if is_balanced_G2 else "unbalanced"))
    print_graph_with_reasons(G2, unbalanced_triangle_G2)

def get_edges_of_triangle(G, triangle):
    e1 = tuple(sorted((triangle[0], triangle[1])))
    e2 = tuple(sorted((triangle[1], triangle[2])))
    e3 = tuple(sorted((triangle[0], triangle[2])))
    return [e1, e2, e3]


def print_graph_with_reasons(G, unbalanced_triangle):
    edges_of_unbalanced_triangle = []
    if unbalanced_triangle != None:
        edges_of_unbalanced_triangle = get_edges_of_triangle(G, unbalanced_triangle)
    unbalanced_plus_edges = []
    unbalanced_minus_edges = []
    balanced_plus_edges = []
    balanced_minus_edges = []
    for edge in G.edges(data=True):
        if edge[2]['sign'] == '+':
            if edge[:-1] in edges_of_unbalanced_triangle:
                unbalanced_plus_edges.append(edge[:-1])
            else:
                balanced_plus_edges.append(edge[:-1])
        else:
            if edge[:-1] in edges_of_unbalanced_triangle:
                unbalanced_minus_edges.append(edge[:-1])
            else:
                balanced_minus_edges.append(edge[:-1])

    pos = nx.spring_layout(G)
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_nodes(G, pos)
    # dashed for minus edge. green: balanced edge, red: unbalanced edge
    nx.draw_networkx_edges(G, pos, edgelist=balanced_plus_edges, width=2, edge_color='g', alpha=0.2)
    nx.draw_networkx_edges(G, pos, edgelist=balanced_minus_edges, width=2, edge_color='g', style='dashed', alpha=0.2)
    nx.draw_networkx_edges(G, pos, edgelist=unbalanced_plus_edges, width=2, edge_color='r')
    nx.draw_networkx_edges(G, pos, edgelist=unbalanced_minus_edges, width=2, edge_color='r', style='dashed')
    plt.show()


#  Question 3c V2

def check_balance_run_v2():
    G1, G2 = generate_graphs_for_question_3b()
    is_balanced_G1, G1_new, node_coloring_G1, bad_vertex_G1 = check_balance_v2(G1)
    is_balanced_G2, G2_new, node_coloring_G2, bad_vertex_G2 = check_balance_v2(G2)
    print("G1 is: " + ("balanced" if is_balanced_G1 else "unbalanced"))
    print_graph(G1)
    if not is_balanced_G1:
        print_graph_with_reasons_v2(G1_new, node_coloring_G1, bad_vertex_G1)
    print("G2 is: " + ("balanced" if is_balanced_G2 else "unbalanced"))
    print_graph(G2)
    if not is_balanced_G2:
        print_graph_with_reasons_v2(G2_new, node_coloring_G2, bad_vertex_G2)

def print_graph(G):
    pos = nx.spring_layout(G)
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_nodes(G, pos)
    minus_edges = []
    plus_edges = []
    for edge in G.edges(data=True):
        if edge[2]['sign'] == '+':
            plus_edges.append(edge[:-1])
        else:
            minus_edges.append(edge[:-1])
    nx.draw_networkx_edges(G, pos, edgelist=minus_edges, edge_color='r', style='dashed')
    nx.draw_networkx_edges(G, pos, edgelist=plus_edges, edge_color='g')
    plt.show()

def print_graph_with_reasons_v2(G_component_graph, node_coloring, bad_vertex):
    pos = nx.spring_layout(G_component_graph)
    nx.draw_networkx_labels(G_component_graph, pos)
    no_color_nodes = [key for (key, value) in node_coloring.items() if value == 0 and key is not bad_vertex]
    first_color_nodes = [key for (key, value) in node_coloring.items() if value == 1 and key is not bad_vertex]
    second_color_nodes = [key for (key, value) in node_coloring.items() if value == 2 and key is not bad_vertex]
    nx.draw_networkx_nodes(G_component_graph, pos, nodelist=[bad_vertex], node_color='#b41f1f')
    nx.draw_networkx_nodes(G_component_graph, pos, nodelist=no_color_nodes, node_color='#b6b6ba')
    nx.draw_networkx_nodes(G_component_graph, pos, nodelist=first_color_nodes, node_color='#0ebf0b')
    nx.draw_networkx_nodes(G_component_graph, pos, nodelist=second_color_nodes, node_color='#00d4ff')
    nx.draw_networkx_edges(G_component_graph, pos)
    plt.show()


#####################################################################
#####################################################################

# question 3d

def create_politician_graph():
    G = nx.Graph()
    G.add_node('Bibi')
    G.add_node('Yair')
    G.add_node('Beni')
    G.add_node('Moshe')
    G.add_node('Benet')
    G.add_node('Aryeh')
    G.add_node('Gabi')
    G.add_node('Tibi')
    G.add_node('Bogie')
    G.add_edge('Benet', 'Tibi', sign='-')
    G.add_edge('Benet', 'Bibi', sign='+')
    G.add_edge('Moshe', 'Bibi', sign='+')
    G.add_edge('Aryeh', 'Bibi', sign='+')
    G.add_edge('Bogie', 'Bibi', sign='-')
    G.add_edge('Yair', 'Bibi', sign='-')
    G.add_edge('Beni', 'Bibi', sign='-')
    G.add_edge('Tibi', 'Bibi', sign='-')
    G.add_edge('Yair', 'Beni', sign='+')
    G.add_edge('Bogie', 'Beni', sign='+')
    G.add_edge('Bogie', 'Yair', sign='+')
    G.add_edge('Gabi', 'Yair', sign='+')
    G.add_edge('Gabi', 'Bogie', sign='+')
    G.add_edge('Gabi', 'Beni', sign='+')
    G.add_edge('Moshe', 'Beni', sign='+')
    G.add_edge('Moshe', 'Yair', sign='+')
    G.add_edge('Moshe', 'Beni', sign='+')
    a, b, c, d = check_balance_v2(G)
    eplus = []
    eminus = []
    for (u, v, d) in G.edges(data=True):
        if d['sign'] == '+':
            eplus.append((u, v))
        else:
            eminus.append((u, v))

    pos = nx.spring_layout(G)
    nx.draw_networkx_nodes(G, pos, node_size=1300)
    nx.draw_networkx_edges(G, pos, edgelist=eplus)
    nx.draw_networkx_edges(G, pos, edgelist=eminus, style='dashed')
    nx.draw_networkx_labels(G, pos)
    plt.show()


#####################################################################
#####################################################################
# TESTS

def test_graph_from_lecture_on_connected_components():
    G = nx.Graph()
    G.add_node(1)
    G.add_node(2)
    G.add_node(3)
    G.add_node(4)
    G.add_node(5)
    G.add_node(6)
    G.add_node(7)
    G.add_node(8)
    G.add_node(9)
    G.add_node(10)
    G.add_node(11)
    G.add_node(12)
    G.add_node(13)
    G.add_node(14)
    G.add_node(15)
    G.add_edge(1, 2, sign='+')
    G.add_edge(1, 3, sign='+')
    G.add_edge(2, 3, sign='+')
    G.add_edge(2, 4, sign='-')
    G.add_edge(2, 5, sign='+')
    G.add_edge(3, 6, sign='-')
    G.add_edge(4, 7, sign='-')
    G.add_edge(4, 9, sign='-')
    G.add_edge(5, 6, sign='-')
    G.add_edge(6, 8, sign='+')
    G.add_edge(6, 11, sign='-')
    G.add_edge(7, 12, sign='+')
    G.add_edge(8, 11, sign='-')
    G.add_edge(9, 12, sign='+')
    G.add_edge(10, 11, sign='-')
    G.add_edge(10, 12, sign='+')
    G.add_edge(11, 13, sign='-')
    G.add_edge(11, 14, sign='-')
    G.add_edge(12, 13, sign='+')
    G.add_edge(13, 15, sign='-')
    G.add_edge(14, 15, sign='-')
    print_graph(G)
    G = get_connected_components_on_plus_edges_graph(G)
    print_graph(G)

def test_a():
    G = nx.Graph()
    G.add_node(1)
    G.add_node(2)
    G.add_node(3)
    G.add_edge(1, 2, sign='+')
    G.add_edge(1, 3, sign='-')
    G.add_edge(2, 3, sign='+')
    print_graph(G)
    G = get_connected_components_on_plus_edges_graph(G)
    print_graph(G)





def test1():
    G = nx.Graph()
    nx.add_path(G, [1, 2, 3, 1], sign='+')
    nx.add_path(G, [1, 4, 5, 1], sign='+')
    G.add_edge(1, 7, sign='+')
    G.add_edge(7, 8, sign='-')
    G.add_edge(8, 9, sign='-')
    G.add_edge(9, 1, sign='-')
    print(check_balance(G))
    # nx.draw(G, with_labels=True, font_weight='bold')
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True)
    nx.draw_networkx_edge_labels(G, pos, labels='sign')
    plt.show()


def test2():
    G1, G2 = generate_graphs_for_question_3b()
    print("G1")
    print_sign_statistics(G1)
    print("G2")
    print_sign_statistics(G2)
    print_signed_graph(G2)
    print_signed_graph(G1)


def print_sign_statistics(G):
    a = nx.get_edge_attributes(G, 'sign')
    plus = 0
    minus = 0
    for k in a:
        if a[k] == '+':
            plus += 1
        else:
            minus += 1
    print("PLUS: " + str(plus))
    print("MINUS: " + str(minus))
    print("PRECENT: Plus- " + str(plus / (plus + minus)) + " Minus- " + str(minus / (plus + minus)))


def print_signed_graph(G):
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True)
    nx.draw_networkx_edge_labels(G, pos, labels='sign')
    plt.show()

# END TESTS
#################################


# test1()
# test2()
# test_graph_from_lecture_on_connected_components()
# test_a()
# create_politician_graph()
# check_balance_run_v2()
# check_balance_run()

