import networkx as nx
import os
import numpy as np
import argparse
import pandas as pd
from collections import deque, defaultdict


def all_same( items ):
    return len( set( items ) ) == 1

def power_support_influence(Graph):
    copy = Graph.copy()
    if copy.has_node('H'):
        copy.remove_node('H')
    M = nx.MultiDiGraph()
    M.add_nodes_from(copy.nodes(data=True))
    nx.set_node_attributes(M, 0, 'support')
    paths = list(set([e[2] for e in copy.edges(keys=True)]))
    power = defaultdict(float)
    for path in paths:
        nodes = path.split("_")
        tot = 0
        if not all_same(nodes):
            # compute the support in bottom up order
            for i in reversed(range(1, len(nodes))):
                Wij = copy[nodes[i-1]][nodes[i]][path]['weight']
                Njk = Graph.in_degree(nodes[i],'weight')
                tot += Wij / Njk
                M.add_edge(nodes[i-1], nodes[i], path, weight=(Wij / Njk))
                power[nodes[i-1]] += tot
    for node in copy.nodes():
        M.node[node]['support'] = power[node]
    return M

def power_support_influence_2(Graph):
    copy = Graph.copy()
    if copy.has_node('H'):
        copy.remove_node('H')
    M = nx.MultiDiGraph()
    M.add_nodes_from(copy.nodes(data=True))
    nx.set_node_attributes(M, 0, 'support')
    for node in copy.nodes(data=True):
        sum_Wij = 0
        # perform depth first search in each node and compute Power
        edges = [x for x in list(copy.edges(keys=True)) if (x[2].split('_')[0] == "%s"%(node[0]))]
        out_dg = list(copy.out_edges(node[0], keys=True))
        node_tree = list(set(edges + out_dg))
        for ed in node_tree:
            Wij = copy[ed[0]][ed[1]][ed[2]]['weight']
            Nik = Graph.in_degree(ed[1],'weight')
            sum_Wij += Wij / Nik
            M.add_edge(ed[0], ed[1], ed[2], weight=(Wij / Nik))
        M.node[node[0]]['support'] = sum_Wij
    return M


def power_attract_influence(Graph):
    copy = Graph.copy()
    if copy.has_node('H'):
        copy.remove_node('H')
    M = nx.MultiDiGraph()
    M.add_nodes_from(copy.nodes(data=True))
    nx.set_node_attributes(M, 0, 'attract')
    paths = list(set([e[2] for e in copy.edges(keys=True)]))
    power = defaultdict(float)
    for path in paths:
        nodes = path.split("_")
        tot = 0
        if not all_same(nodes):
            for i in range(1, len(nodes)):
                Wij = Graph[nodes[i-1]][nodes[i]][path]['weight']
                Nik = Graph.out_degree(nodes[i-1],'weight')
                tot += Wij / Nik
                M.add_edge(nodes[i-1], nodes[i], path, weight=(Wij / Nik))
                power[nodes[i]] += tot
    for node in copy.nodes():
        M.node[node]['attract'] = power[node]
    return M

def power_attract_influence_2(Graph):
    copy = Graph.copy()
    if copy.has_node('H'):
        copy.remove_node('H')
    #This procedure makes easy to compute out_power
    M = nx.MultiDiGraph()
    M.add_nodes_from(copy.nodes(data=True))
    nx.set_node_attributes(M, 0, 'attract')
    for node in copy.nodes(data=True):
        sum_Wij = 0
        # perform depth first search in each node and compute Power in reverse order.
        #beware! the order of edges could be confusing ex: edge [1][2][1] -> [2][1][1]
        edges = [x for x in list(copy.edges(keys=True)) if (x[2].split('_')[1] == "%s"%(node[0]))]
        in_dg = list(copy.in_edges(node[0], keys=True))
        node_tree = list(set(edges + in_dg))
        for ed in node_tree:
            Wij = Graph[ed[0]][ed[1]][ed[2]]['weight']
            #compute out degree do node
            Nik = Graph.out_degree(ed[0],'weight')
            sum_Wij += Wij / Nik
            M.add_edge(ed[0], ed[1], ed[2], weight=(Wij / Nik))
        M.node[node[0]]['attract'] = sum_Wij
    return M

def attract_independece(Graph):
    node_indepence = dict()
    for node in Graph.nodes(data=True):
        total = Graph.in_degree(node[0], 'weight')
        #get the sum of H weight for each edge in node
        h_weight = sum([x[2] for x in  Graph.in_edges(node[0],'weight') if x[0]=='H'])
        node_indepence[node[0]] = (0 if total == 0 else h_weight / total)
    return node_indepence

def support_independece(Graph):
    node_indepence = dict()
    for node in Graph.nodes(data=True):
        total = Graph.out_degree(node[0], 'weight')
        #get the sum of H weight for each edge in node
        h_weight = sum([x[2] for x in  Graph.out_edges(node[0],'weight') if x[1]=='H'])
        node_indepence[node[0]] = (0 if total == 0 else h_weight / total)
    return node_indepence

def harmonic(value1, value2):
    return (2 * value1 * value2 / (value1 + value2))

def write_csv(In_G, Out_G, file_name):
    csv = "in,in_amenity,in_support,in_attract,support,out,out_amenity,out_support,out_attract\n"
    for edge in In_G.edges(data=True):
        csv += str(edge[0]) + ','
        csv += str(In_G.node[edge[0]]['amenity']) + ','
        csv += str(In_G.node[edge[0]]['support']) + ','
        csv += str(Out_G.node[edge[0]]['attract']) + ','
        csv += str(edge[2]['weight']) + ','
        csv += str(edge[1]) + ','
        csv += str(In_G.node[edge[1]]['amenity']) + ','
        csv += str(In_G.node[edge[1]]['support']) + ','
        csv += str(Out_G.node[edge[1]]['attract']) + '\n'
    f = open(file_name, 'w')
    f.writelines(csv)
    f.close()

if __name__ == "__main__":
    doc_list = list()
    #graphs = (["graphs/" + file for root, dirs, files in os.walk((os.getcwd() + "/graphs/"))
    #           for file in files if file.startswith('inf') and file.endswith('.gml')])
    
    parser = argparse.ArgumentParser(description='Compute Influence')
    parser.add_argument('-f', '--file', required=True)
    args = parser.parse_args()

    graph = args.file 

    #for graph in graphs:
    H = nx.read_gml(graph)
    In_G = power_support_influence(H)
    Out_G = power_attract_influence(H)
    file_name = graph.replace("inf", "support")
    print('saving graph %s' % file_name)
    nx.write_gml(In_G, file_name)
    file_name = graph.replace("inf", "attract")
    print('saving graph %s' % file_name)
    nx.write_gml(Out_G, file_name)
    file_name = graph.replace(".gml", ".csv")
    file_name = file_name.replace("inf", "power")
    print('saving CSV %s' % file_name)
    #write_csv(In_G, Out_G, file_name)
