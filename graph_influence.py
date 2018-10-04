import networkx as nx
from scipy.stats import beta
import os


def influence_degree(x, y, a):
    b = 1
    return ((beta.pdf(x, a, b) + y) / (a + 1))


def direct_influence(Graph):
    out_degree = Graph.out_degree()
    M = nx.DiGraph()
    M.add_nodes_from(Graph.nodes(data=True))
    for node in Graph.nodes(data=True):
        if(out_degree[node[0]] > 0):
            Wik = Graph.out_degree(node[0], weight='weight')
            for j in Graph.neighbors(node[0]):
                Wij = Graph[node[0]][j]['weight']
                Nik = Graph.in_degree(j, weight='weight')
                influencer = Wij / Wik
                influencee = Wij / Nik
                inf_degree = influence_degree(influencee, influencer, 5)
                M.add_edge(node[0], j, weight=inf_degree)
    return M


if __name__ == "__main__":
    doc_list = list()
    graphs = (["graphs/" + file for root, dirs, files in os.walk((os.getcwd() + "/graphs/"))
               for file in files if file.startswith('inf') and file.endswith('.gml')])
    for graph in graphs:
        H = nx.read_gml(graph)
        H = direct_influence(H)
        file_name = graph.replace("inf", "deg_inf")
        print('saving graph %s' % file_name)
        nx.write_gml(H, file_name)
        file_name = file_name.replace(".gml",".csv")
        print('saving graph %s' % file_name)
        nx.write_edgelist(H, file_name, delimiter=',')
