import networkx as nx
import numpy as np

def closenessCentrality(graph, node=None):
    nodes = graph.nodes()
    result = {}
    numberOfNodes = len(graph)
    
    for vertex in nodes:
        distanceMap = calculateDistance(graph, vertex)     
        result[vertex] = (numberOfNodes - 1) *pow(sum(distanceMap.values()),-1) #from lecture
    return result



def degreeCentrality(graph):   
    nodes = graph.nodes()
    result = {}
    numberOfNodes = len(graph)

    for vertex in nodes:
        result[vertex] = len(list(graph.neighbors(vertex))) / (numberOfNodes - 1)#from lecture
    return result


def betweennessCentrality(graph):
    nodes = graph.nodes()
    numberOfNodes = len(graph)
    keys = nodes
    values = [0 for vertex in range(numberOfNodes)]
    result = dict(zip(keys,values))#create dic node and val
    
    for srcVertex in nodes:
        for dstVertex in nodes:
            if srcVertex < dstVertex:
                paths = [pth for pth in nx.all_shortest_paths(graph, source=srcVertex, target=dstVertex)]
                for pth in paths:
                    for p_i in pth[1:-1]:
                        if p_i in result:#check if p_i on the shortest path
                            result[p_i] += 1 / len(paths)#update table
    for res in result:
        result[res] = (2*result[res])/((numberOfNodes - 1) * (numberOfNodes - 2))#from lecture

    return result

def calculateDistance(graph, start):
    visited, queue = set(), [start]
    distanceMap = {}
    distanceMap[start] = 0
    while queue:
        vertex = queue.pop(0)
        for nextVertex in graph.neighbors(vertex):
            if nextVertex in distanceMap:
                continue
            queue.append(nextVertex)
            distanceMap[nextVertex] = distanceMap[vertex]+1
    return distanceMap


