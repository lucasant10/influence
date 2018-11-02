import networkx as nx
import os
import numpy as np


def power_influence(Graph):
    copy = Graph.copy()
    copy.remove_edges_from(copy.selfloop_edges())
    M = nx.DiGraph()
    M.add_nodes_from(Graph.nodes(data=True))
    nx.set_node_attributes(M, 0, 'power')
    for node in Graph.nodes(data=True):
        sum_Wij = 0
        for j in copy.neighbors(node[0]):
            Wij = Graph[node[0]][j]['weight']
            Nik = Graph.in_degree(j, weight='weight')
            sum_Wij += Wij / Nik
            M.add_edge(node[0], j, weight=(Wij / Nik))
        M.node[node[0]]['power'] = sum_Wij
    return M


def power_indegree_influence(Graph):
    copy = Graph.copy()
    copy.remove_edges_from(list(copy.selfloop_edges()))
    M = nx.MultiDiGraph()
    M.add_nodes_from(Graph.nodes(data=True))
    nx.set_node_attributes(M, 0, 'powerIn')
    for node in Graph.nodes(data=True):
        sum_Wij = 0
        # perform depth first search in each node and compute Power
        edge_tree = [x for x in list(
            nx.edge_dfs(copy, node[0])) if (x[2] == node[0]) and (x[1] != node[0])]
        out_dg = list(copy.out_edges(node[0], keys=True))
        node_tree = list(set(edge_tree + out_dg))
        for ed in node_tree:
            Wij = Graph[ed[0]][ed[1]][ed[2]]['weight']
            Nik = get_in_degree_weight(Graph, ed[1])
            sum_Wij += Wij / Nik
            M.add_edge(ed[0], ed[1], ed[2], weight=(Wij / Nik))
        M.node[node[0]]['powerIn'] = sum_Wij
    return M


def power_outdegree_influence(Graph):
    Graph = convert_to_digraph(Graph)
    copy = Graph.copy()
    copy.remove_edges_from(list(copy.selfloop_edges()))
    M = nx.DiGraph()
    M.add_nodes_from(Graph.nodes(data=True))
    nx.set_node_attributes(M, 0, 'powerOut')
    for node in Graph.nodes(data=True):
        sum_Wij = 0
        in_dg = list(copy.in_edges(node[0]))
        for ed in in_dg:
            Wij = Graph[ed[0]][ed[1]]['weight']
            out_ed = copy.out_edges(ed[0], data=True)
            Nik = sum([x[2]['weight'] for x in list(out_ed)])
            sum_Wij += Wij / Nik
            M.add_edge(ed[0], ed[1], weight=(Wij / Nik))
        M.node[node[0]]['powerOut'] = sum_Wij
    return M


def get_in_degree_weight(G, node):
    # Avoid to compute weigth twice when a circuit exists
    ed = G.in_edges(node, keys=True, data=True)
    return sum([x[3]['weight'] for x in list(ed) if not((x[2] == node) and (x[0] != node))])


def write_csv(In_G, Out_G, file_name):
    csv = "in,in_amenity,in_power_in,in_power_out,influence,out,out_amenity,out_power_in,out_power_out\n"
    for edge in In_G.edges(data=True):
        csv += str(edge[0]) + ','
        csv += str(In_G.node[edge[0]]['amenity']) + ','
        csv += str(In_G.node[edge[0]]['powerIn']) + ','
        csv += str(Out_G.node[edge[0]]['powerOut']) + ','
        csv += str(edge[2]['weight']) + ','
        csv += str(edge[1]) + ','
        csv += str(In_G.node[edge[1]]['amenity']) + ','
        csv += str(In_G.node[edge[1]]['powerIn']) + ','
        csv += str(Out_G.node[edge[1]]['powerOut']) + '\n'
    f = open(file_name, 'w')
    f.writelines(csv)
    f.close()


def convert_to_digraph(Graph):
    M = nx.DiGraph()
    M.add_nodes_from(Graph.nodes(data=True))
    for ed in Graph.edges(data=True):
        w = sum([v['weight'] for k, v in (Graph[ed[0]][ed[1]]).items()])
        M.add_edge(ed[0], ed[1], weight=w)
    return M


if __name__ == "__main__":
    doc_list = list()
    graphs = (["graphs/" + file for root, dirs, files in os.walk((os.getcwd() + "/graphs/"))
               for file in files if file.startswith('inf') and file.endswith('.gml')])
    for graph in graphs:
        H = nx.read_gml(graph)
        In_G = power_indegree_influence(H)
        Out_G = power_outdegree_influence(H)
        file_name = graph.replace("inf", "power_in")
        print('saving graph %s' % file_name)
        nx.write_gml(In_G, file_name)
        file_name = graph.replace("inf", "power_out")
        print('saving graph %s' % file_name)
        nx.write_gml(Out_G, file_name)
        file_name = graph.replace(".gml", ".csv")
        file_name = file_name.replace("inf", "power")
        print('saving CSV %s' % file_name)
        write_csv(In_G, Out_G, file_name)
