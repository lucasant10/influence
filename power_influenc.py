import networkx as nx
import os
import numpy as np


def power_influence(Graph):
    out_degree = Graph.out_degree()
    M = nx.DiGraph()
    M.add_nodes_from(Graph.nodes(data=True))
    nx.set_node_attributes(M, 0, 'power')
    for node in Graph.nodes(data=True):
        if(out_degree[node[0]] > 0):
            out_dg = out_degree[node[0]]
            sum_Wij = 0
            for j in Graph.neighbors(node[0]):
                Wij = Graph[node[0]][j]['weight']
                Nik = Graph.in_degree(j, weight='weight')
                sum_Wij += Wij / Nik
                M.add_edge(node[0], j, weight=Wij)
            power = np.log2(out_dg) + sum_Wij
            M.node[node[0]]['power'] = power
    return M

def write_csv(Graph, file_name):
    csv = "in,in_amenity,in_power,out,out_amenity,out_power\n"
    for edge in Graph.edges():
        csv += str(edge[0]) + ','
        csv += str(Graph.node[edge[0]]['amenity']) + ','
        csv += str(Graph.node[edge[0]]['power']) + ','
        csv +=str( edge[1]) + ','
        csv += str(Graph.node[edge[1]]['amenity']) + ','
        csv += str(Graph.node[edge[1]]['power']) + '\n'
    f = open(file_name,'w')
    f.writelines(csv) 
    f.close()        

if __name__ == "__main__":
    doc_list = list()
    graphs = (["graphs/" + file for root, dirs, files in os.walk((os.getcwd() + "/graphs/"))
               for file in files if file.startswith('inf') and file.endswith('.gml')])
    for graph in graphs:
        H = nx.read_gml(graph)
        H = power_influence(H)
        file_name = graph.replace("inf", "power")
        print('saving graph %s' % file_name)
        nx.write_gml(H, file_name)
        file_name = file_name.replace(".gml",".csv")
        print('saving graph %s' % file_name)
        write_csv(H, file_name)
