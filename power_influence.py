import networkx as nx
import os
import numpy as np
import argparse

def power_support_influence(Graph):
    copy = Graph.copy()
    copy.remove_node('H')
    M = nx.MultiDiGraph()
    M.add_nodes_from(copy.nodes(data=True))
    nx.set_node_attributes(M, 0, 'support')
    for node in copy.nodes(data=True):
        sum_Wij = 0
        # perform depth first search in each node and compute Power
        edge_tree = [x for x in list(nx.edge_dfs(copy, node[0])) if (x[2] == node[0]) and (x[1] != node[0])]
        out_dg = list(copy.out_edges(node[0], keys=True))
        node_tree = list(set(edge_tree + out_dg))
        for ed in node_tree:
            Wij = copy[ed[0]][ed[1]][ed[2]]['weight']
            Nik = Graph.in_degree(ed[1],'weight')
            sum_Wij += Wij / Nik
            M.add_edge(ed[0], ed[1], ed[2], weight=(Wij / Nik))
        M.node[node[0]]['support'] = sum_Wij
    return M

def power_attract_influence(Graph):
    copy = Graph.copy()
    copy.remove_node('H')
    #This procedure makes easy to compute out_power
    copy = copy.reverse()
    M = nx.MultiDiGraph()
    M.add_nodes_from(copy.nodes(data=True))
    nx.set_node_attributes(M, 0, 'attract')
    for node in copy.nodes(data=True):
        sum_Wij = 0
        # perform depth first search in each node and compute Power in reverse order.
        #beware! the order of edges could be confusing ex: edge [1][2][1] -> [2][1][1]
        node_tree = get_out_degree_edges(copy, node[0])
        for ed in node_tree:
            Wij = Graph[ed[1]][ed[0]][ed[2]]['weight']
            #compute out degree do node
            Nik = Graph.out_degree(ed[1],'weight')
            sum_Wij += Wij / Nik
            M.add_edge(ed[1], ed[0], ed[2], weight=(Wij / Nik))
        M.node[node[0]]['attract'] = sum_Wij
    return M


def get_out_degree_edges(G, node):
    tmp = set()
    edges = G.out_edges(node, keys=True)
    #add edges from out_degree (in_degree in orignal graph)
    tmp.update(edges)
    for x in edges:
        #get edges with successors (predecessors in original graph)
        if x[1]!=x[2]:
            tmp.update([y for y in list(nx.edge_dfs(G, node)) if (y[2] != node) and y[2]==x[2]])
    return list(tmp)


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
    write_csv(In_G, Out_G, file_name)
